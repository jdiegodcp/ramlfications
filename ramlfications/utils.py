#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

try:
    from collections import OrderedDict
except ImportError:  # pragma: no cover
    # python 2.6
    from ordereddict import OrderedDict

import yaml


class EndpointOrderError(Exception):
    pass


class EndpointOrder(object):
    """Parses a YAML file that defines order for RAML resources"""
    def __init__(self, yaml_file):
        self.yaml = yaml_file

    @property
    def order(self):
        """
        Returns the desired visual order of endpoints defined in a
        YAML file
        """
        class OrderedLoader(yaml.SafeLoader):
            pass

        def construct_mapping(loader, node):
            loader.flatten_mapping(node)
            return OrderedDict(loader.construct_pairs(node))

        OrderedLoader.add_constructor(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            construct_mapping)

        try:
            return yaml.load(open(self.yaml), OrderedLoader)
        except IOError as e:
            raise EndpointOrderError(e)

    @property
    def groupings(self):
        """Returns groupings of endpoints defined in endpoint-order.yaml"""
        return list(self.order.keys())
