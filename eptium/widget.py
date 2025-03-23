#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Ognyan Moore.
# Distributed under the terms of the Modified BSD License.

"""
TODO: Add module docstring
"""

__all__ = ["Eptium"]

import json
import pathlib
import sys
import uuid

from base64 import b64encode
from urllib.parse import urlparse, urlencode

from IPython.display import IFrame
import requests
from jupyter_server import serverapp

class Eptium:

    def __init__(self, server='https://viewer.copc.io'):
        self.src = self.server = server.rstrip("/")
        self.height = '600px'
        template_path = pathlib.Path(__file__).parent / "template_state.json"
        with open(template_path) as t:
            self.state = json.load(t)        

    def _setHeight(self, value: int | str):
        if isinstance(value, int):
            value = str(value)
        self.height = value

    def _setBoundingGeometry(self, left, bottom, right, top):
        self.state["bbox"] = (left, bottom, right, top)

    def _setColorOn(self, attribute: str):
        # TODO: insert checks to ensure attribute is one of the supported ones
        self.state['groups'][0]['colorId'] = attribute

    def _setPointCloudColorRamp(self, ramp: str):
        group = self.state['groups'][0]
        colors = group['colors']
        for color in colors:
            if color['id'] == group['colorId'] and color['type'] == 'continuous':
                color['rampId'] = ramp

    def _setRasterColorRamp(self, ramp: str):
        group = self.state['rasterGroups'][0]
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
            # construct a "local" URL

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
        if extension.startswith("tif"):
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
        color_ramp_pc: str | None = None,
        color_ramp_raster: str | None = None,
        viewBounds: tuple[float, float, float, float] | None = None,
        wireFrame: bool = False
    ):
        """Method to call to generate the Eptium View

        Parameters
        ----------
        path : str | pathlib.Path
            Path to the asset that Eptium should display. Acceptable
            values include local file paths, or URLs to 
        height : int | str, default='600px'
            Accepted values are used to set the ``height`` attribute
            of an iframe.
        color_on : str, default='elevation'
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

        color_ramp_pc : str
            Color ramp to set the coloring for point clouds when coloring on
            a continuous attribute.  Possible values include

            * viridis
            * magma
            * plasma
            * inferno
            * cividis
            * turbo
            * dem-screen
            * usgs
            * black-to-white
            * blue-to-red
            * pink-to-yellow

        color_ramp_raster : str, default='dem-screen'
            Color ramp to set the coloring for rasters when coloring on a
            continuous attribute. Possible values include

            * viridis
            * magma
            * plasma
            * inferno
            * cividis
            * turbo
            * dem-screen
            * usgs
            * black-to-white
            * blue-to-red
            * pink-to-yellow

        viewBounds : (float, float, float, float), Optional, default=None
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
        if color_ramp_pc is not None:
            # needs to happen after _setColorOn
            self._setPointCloudColorRamp(color_ramp_pc)
        if color_ramp_raster is not None:
            self._setRasterColorRamp(color_ramp_raster)
        if viewBounds is not None:
            self._setBoundingGeometry(*viewBounds)

        # set wireframe
        self.state['isWireframeEnabled'] = wireFrame
        
        # determine the URL
        state_hash = b64encode(json.dumps(self.state).encode('utf-8')).decode('utf-8')
        self.src = f"{self.server}/#{state_hash}"
        return IFrame(src=self.src, height=self.height, width='100%')
