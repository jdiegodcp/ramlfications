# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

__all__ = ["RAMLLoader"]

try:
    from collections import OrderedDict
except ImportError:  # pragma: no cover
    from ordereddict import OrderedDict

import os

import yaml

from .errors import LoadRAMLFileError


class RAMLLoader(object):
    """
    Extends YAML loader to load RAML files with ``!include`` tags.
    """
    def _yaml_include(self, loader, node):
        """
        Adds the ability to follow ``!include`` directives within
        RAML Files.
        """
        # Get the path out of the yaml file
        file_name = os.path.join(os.path.dirname(loader.name), node.value)

        with open(file_name) as inputfile:
            return yaml.load(inputfile)

    def _ordered_load(self, stream, loader=yaml.Loader):
        """
        Preserves order set in RAML file.
        """
        class OrderedLoader(loader):
            pass

        def construct_mapping(loader, node):
            loader.flatten_mapping(node)
            return OrderedDict(loader.construct_pairs(node))
        OrderedLoader.add_constructor("!include", self._yaml_include)
        OrderedLoader.add_constructor(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)
        return yaml.load(stream, OrderedLoader)

    def load(self, raml):
        """
        Loads the desired RAML file and returns an instance of ``RAMLDict``.

        Accepts either:
        :param str raml_file: string path to RAML file
        :param unicode raml_file: unicode string path to RAML file
        :param file raml_file: file-like object of RAML file \
            (must have a ``read`` method)

        :return: An instance of ``RAMLDict``
        :rtype: ``RAMLDict``
        """

        try:
            return self._ordered_load(raml, yaml.SafeLoader)
        except yaml.parser.ParserError as e:
            msg = "Error parsing RAML: {0}".format(e)
            raise LoadRAMLFileError(msg)
