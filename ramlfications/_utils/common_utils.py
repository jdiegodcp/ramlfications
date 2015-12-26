# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function


#####
# General Helper functions
#####

# general
def _get(data, item, default=None):
    """
    Helper function to catch empty mappings in RAML. If item is optional
    but not in the data, or data is ``None``, the default value is returned.

    :param data: RAML data
    :param str item: RAML key
    :param default: default value if item is not in dict
    :param bool optional: If RAML item is optional or needs to be defined
    :ret: value for RAML key
    """
    try:
        return data.get(item, default)
    except AttributeError:
        return default
