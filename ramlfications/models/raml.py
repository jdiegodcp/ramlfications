# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB
#
# Objects representing RAML file types

from __future__ import absolute_import, division, print_function

import attr

from .root import BaseRootNode


@attr.s
class RootNodeDataType(BaseRootNode):
    """
    API Root Node for 1.0 DataType fragment files
    """
    type = attr.ib()
