# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

__all__ = ["RAMLLoader"]

try:
    from collections import OrderedDict
except ImportError:  # pragma: no cover
    from ordereddict import OrderedDict

import os

import jsonref
import yaml

from six import string_types

from .errors import LoadRAMLError

RAMLHEADER = "#%RAML "

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
        file_ext = os.path.splitext(file_name)[1]
        parsable_ext = [".yaml", ".yml", ".raml", ".json"]

        if file_ext not in parsable_ext:
            with open(file_name) as inputfile:
                return inputfile.read()

        if file_ext == ".json":
            return self._parse_json(file_name, os.path.dirname(file_name))

        with open(file_name) as inputfile:
            return yaml.load(inputfile, self._ordered_loader)

    def _parse_json(self, jsonfile, base_path):
        """
        Parses JSON as well as resolves any `$ref`s, including references to
        local files and remote (HTTP/S) files.
        """
        base_path = os.path.abspath(base_path)
        if not base_path.endswith("/"):
            base_path = base_path + "/"
        base_path = "file://" + base_path

        with open(jsonfile, "r") as f:
            schema = jsonref.load(f, base_uri=base_path, jsonschema=True)
        return schema

    def _ordered_load(self, stream, loader=yaml.SafeLoader):
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

        self._ordered_loader = OrderedLoader

        return yaml.load(stream, OrderedLoader)

    def _parse_raml_header(self, raml):
        if isinstance(raml, string_types):
            header = raml.split('\n', 1)[0]
        else:
            header = raml.readline().strip()
        if not header.startswith(RAMLHEADER):
            msg = "Error raml file shall start with {0} but got {1}".format(
                RAMLHEADER, header)
            raise LoadRAMLError(msg)
        version_string = header[len(RAMLHEADER):]
        version = version_string.split(" ")[0]  # skip file type for now
        return version

    def load(self, raml):
        """
        Loads the desired RAML file and returns data.

        :param raml: Either a string/unicode path to RAML file,
            a file object, or string-representation of RAML.

        :return: Data from RAML file
        :rtype: ``dict``

        """
        raml_version = self._parse_raml_header(raml)
        try:
            ret = self._ordered_load(raml, yaml.SafeLoader)
        except yaml.parser.ParserError as e:
            msg = "Error parsing RAML: {0}".format(e)
            raise LoadRAMLError(msg)
        except yaml.constructor.ConstructorError as e:
            msg = "Error parsing RAML: {0}".format(e)
            raise LoadRAMLError(msg)

        if ret is None:
            ret = OrderedDict()
        ret._raml_version = raml_version
        return ret
