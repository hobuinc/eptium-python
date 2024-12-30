#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Ognyan Moore.
# Distributed under the terms of the Modified BSD License.

"""
TODO: Add module docstring
"""

from ipywidgets import DOMWidget, ValueWidget, register
from traitlets import Unicode, Bool, validate, TraitError

from ._frontend import module_name, module_version


# class ExampleWidget(DOMWidget):
#     """TODO: Add docstring here
#     """
#     _model_name = Unicode('ExampleModel').tag(sync=True)
#     _model_module = Unicode(module_name).tag(sync=True)
#     _model_module_version = Unicode(module_version).tag(sync=True)
#     _view_name = Unicode('ExampleView').tag(sync=True)
#     _view_module = Unicode(module_name).tag(sync=True)
#     _view_module_version = Unicode(module_version).tag(sync=True)

#     value = Unicode('Hello World').tag(sync=True)

@register
class PointCloud(DOMWidget, ValueWidget):
    _model_name = Unicode('EptiumModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)

    _view_name = Unicode('EptiumView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    # value = Unicode('example.laz.copc').tag(sync=True)



