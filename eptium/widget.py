#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Ognyan Moore.
# Distributed under the terms of the Modified BSD License.

"""
TODO: Add module docstring
"""

__all__ = ["Eptium"]

import json
import math

import pathlib
import uuid
import statistics
from base64 import b64encode

from urllib.parse import urlparse, urlencode

from ipywidgets import DOMWidget, ValueWidget, register
from traitlets import Unicode
import pyproj

import requests
from jupyter_server import serverapp
from ._frontend import module_name, module_version


@register
class Eptium(DOMWidget, ValueWidget):
    _model_name = Unicode('EptiumModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)

    _view_name = Unicode('EptiumView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    # read-write attributes
    src = Unicode('https://viewer.copc.io').tag(sync=True)
    height = Unicode('600px').tag(sync=True)

    def __init__(
        self,
        src="https://viewer.copc.io",
    ):
        super().__init__()
        self.src = src
        self.height
        template_path = pathlib.Path(__file__).parent / "template_state.json"
        with open(template_path) as t:
            self.state = json.load(t)        

    def _setHeight(self, value: int | str):
        if isinstance(value, int):
            value = str(value)
        self.height = value

    def _setBoundingGeometry(self, left, bottom, right, top):
        # get the midpoint:
        mid_x = statistics.mean([left, right])
        mid_y = statistics.mean([top, bottom])

        # figure out the height of the camera which has 60deg FOV
    
        # latitude degrees are roughly evenly spaced out so straight forward
        # 1deg latitude = 111,320m
        height = abs(top - bottom) * 111_320 

        # 1deg longitude = 40,075,000m * cos(latitude) / 360
        # for latitude we want to use the smaller absolute value
        latitude = min(abs(top), abs(bottom))
        width = abs(right - left) * (40_075_000 * math.cos(math.radians(latitude)) / 360)

        # camera has a 60deg FOV
        # we use 30deg for right triangle assumption and divide the diameter by 2
        camera_view_diameter = max(height, width)
        height = camera_view_diameter / (2 * math.tan(math.pi / 6))
        
        # add a fudge factor so we can see a little around the bounding box
        height *= 1.1

        # convert EPSG:4326 to cartesian
        # EPSG:4979 is EPSG:4326 with 3D (height)
        # EPSG:4978 is geocentric CRS 
        transformation = pyproj.Transformer.from_crs(4979, 4978, always_xy=True)

        # when using always_xy, longitude needs to go first
        x, y, z = transformation.transform(mid_x, mid_y, height)

        # direction of the camera should be straight "down"
        # need to compute unit vector, start with computing the length
        length = math.hypot(x, y, z)
        dir_x = -x / length
        dir_y = -y / length
        dir_z = -z / length

        # compute "up" direction, which should be towards the north pole
        # north pole is at 0, 0, 6356752.314245179
        # but cesium behavior seems to default to 2 * 6378137
        up_reference = (0., 0., 2 * 6378137. )
        d_x = up_reference[0] - x
        d_y = up_reference[1] - y
        d_z = up_reference[2] - z
        length = math.hypot(d_x, d_y, d_z)
        up_x = d_x / length
        up_y = d_y / length
        up_z = d_z / length

        # need to convert bbox to camera position and "up" feature
        camera = {
            "position": [
                x,
                y,
                z
            ],
            "direction": [
                dir_x,
                dir_y,
                dir_z
            ],
            "up": [
                up_x,
                up_y,
                up_z
            ]
        }
        self.state['camera'] = camera

    def _setColorOn(self, attribute: str):
        # TODO: insert checks to ensure attribute is one of the supported ones
        self.state['groups'][0]['colorId'] = attribute

    def _setColorRamp(self, ramp: str):
        group = self.state['groups'][0]
        colors = group['colors']
        for color in colors:
            if color['id'] == group['colorId'] and color['type'] == 'continuous':
                color['rampId'] = ramp



    def _addPath(self, path: str | pathlib.Path ):
        if isinstance(path, pathlib.Path):
            # not using os.fsdecode since we want forward-slashes
            # even on windows
            path = path.as_posix()
        parsed_url = urlparse(path)

        if parsed_url.scheme not in ("https", "http"):
            # we're dealing with a local file and need to
            # construct a remote accessible URL
            # TODO: maybe the first server isn't the one we want?
            # should check for a valid URL for all running servers
            server = next(serverapp.list_running_servers())
            cookies = {}

            # ensure token is good
            r = requests.post(
                url=f"{server['url']}api/contents",
                headers={'Authorization': f"token {server['token']}"},
                cookies=cookies
            )
            r.raise_for_status()

            # get the _xsrf cookie
            r = requests.get(
                url=f"{server['url']}lab/tree",
                cookies=r.cookies
            )

            # order matters!
            params = urlencode({
                'token': server['token'],
                '_xsrf': r.cookies['_xsrf']

            })

            # path = f"https://viewer.copc.io/?q={server['url']}files/{path}?{params}"
            path = f"{server['url']}files/{path}?{params}"

        # append resource 


        _, _, extension = path.rpartition(".")
        if extension == "tif":
            # geotiff
            resource = {
                "id": str(uuid.uuid4()),
                "name": "to-be-named",
                "url": path,
                "isVisible": True,
                "renderAsTerrain": False,
                "band": 0
            }
            self.state['rasterGroups'][0]['rasters'].append(resource)
        else:
            resource = {
                "id": str(uuid.uuid4()),
                "url": path,
                "name": "to-be-named",
                "options": {},
                "isVisible": True
            }
            self.state['groups'][0]['resources'].append(resource)


    def render(
        self,
        path: str | pathlib.Path | list[str | pathlib.Path],
        height: str | int = '600px',
        color_on: str = "elevation",
        color_ramp: str | None = None,
        viewBounds: tuple[float, float, float, float] | None = None,
        wireFrame: bool = False
    ):
        """Method to call to generate the Eptium View

        Parameters
        ----------
        path : str | pathlib.Path
            Path to the asset that Eptium should display. Acceptable
            values include local file paths, or URLs to 
        height : int | str
            Accepted values are used to set the ``height`` attribute
            of an iframe.  Defaults to ``600px``.
        color_on : str
            Attribute to set the coloring based off.  Possible values include
              * rgb
              * elevation (default)
              * intensity
              * classification
              * return-type
              * return-number
              * return-count
              * scan-angle
              * post-source-id
              * fixed
        color_ramp : str
            Color ramp to set the coloring based off.  Possible values include
              * black-to-white
              * blue-to-red
              * pink-to-yellow

            Default value depends on what the ``color_on`` attribute is set to.
            This setting only applies to ``color_on`` attributes that are continuous.
            Those include
              * elevation
              * intensity
              * scan-angle
        viewBounds : (float, float, float, float), Optional
            Bounding box in EPSG:4326 to set the initial view to.  If not specified,
            view will center about the resource being displayed.
        wireFrame : bool, default False
            Draw the wire frame around the item being displayed.
        """
        if isinstance(path, (list, tuple)):
            for p in path:
                self._addPath(p)
        else:
            self._addPath(path)
        self._setHeight(height)
        self._setColorOn(color_on)
        if color_ramp is not None:
            # needs to happen after _setColorOn
            self._setColorRamp(color_ramp)
        if viewBounds is not None:
            self._setBoundingGeometry(*viewBounds)

        # set wireframe
        self.state['isWireframeEnabled'] = wireFrame
        
        # determine the URL
        state_hash = f"{b64encode(
            json.dumps(self.state).encode('utf-8')
        ).decode('utf-8')}"
        self.src = f"https://viewer.copc.io/#{state_hash}"
