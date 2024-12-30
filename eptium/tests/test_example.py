#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Ognyan Moore.
# Distributed under the terms of the Modified BSD License.

import pytest

from .. import Eptium


def test_example_creation_blank():
    w = Eptium()
    assert w.src == "https://viewer.copc.io"
