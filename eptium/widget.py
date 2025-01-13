#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Ognyan Moore.
# Distributed under the terms of the Modified BSD License.

"""
TODO: Add module docstring
"""

__all__ = ["Eptium"]

import os
import pathlib
from urllib.parse import urlparse, urlencode

from ipywidgets import DOMWidget, ValueWidget, register
from traitlets import Unicode, validate, TraitError

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
    height = Unicode('400px').tag(sync=True)

    def __init__(
        self,
        src="https://viewer.copc.io",
    ):
        super().__init__()
        self.src = src
        self.height

    def set_height(self, value: int | str):
        """Set the height of the Eptium View

        Parameters
        ----------
        value : int | str
            Accepted values are used to set the ``height`` attribute
            of an iframe. 

        Examples
        --------
        >>> widget.set_height('200px')
        """
        if isinstance(value, int):
            value = str(value)
        self.height = value

    def render(self, path: str | pathlib.Path):
        """Method to call to generate the Eptium View

        Parameters
        ----------
        path : str | pathlib.Path
            Path to the asset that Eptium should display. Acceptable
            values include local file paths, or URLs to 
        """
        if isinstance(path, pathlib.Path):
            # not using os.fsdecode since we want forward-slashes
            # even on windows
            path = path.as_posix()
        parsed_url = urlparse(path)

        if parsed_url.scheme in ("https", "http"):
            path = f"https://viewer.copc.io/?q={path}"
        else:
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
            
            path = f"https://viewer.copc.io/?q={server['url']}files/{path}?{params}"

        self.src = path
