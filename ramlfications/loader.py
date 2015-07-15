# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

__all__ = ["RAMLLoader"]

try:
    from collections import OrderedDict
except ImportError:  # pragma: no cover
    from ordereddict import OrderedDict

import copy
import os

import yaml

from .errors import LoadRAMLError
from .utils import download_url


class RAMLLoader(object):
    """
    Extends YAML loader to load RAML files with ``!include`` tags.
    """
    refs = {}
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

        with open(file_name) as inputfile:
            parsed = yaml.load(inputfile, self._ordered_loader)

            if file_ext == ".json":
                parsed = self._parse_json_refs(
                    parsed,
                    os.path.dirname(file_name),
                )

            return parsed

    def _lookup_json_ref(self, ref_key, base_path=None, parent_schema=None):
        """
        Traverses the json pointer and returns the value of the pointer.
        """
        if "#" not in ref_key:
            raise Exception("Ref values must contain a fragment (#).")

        ref_uri, ref_fragment = ref_key.split("#")
        # Load the ref and cache it if the ref is not an internal reference
        if ref_uri not in self.refs.keys():
            if ref_uri is not '':
                response = download_url(ref_uri)
                self.refs[ref_uri] = self._ordered_load(response,
                                                        yaml.SafeLoader)


        # Hack to make the "whole file" be the empty string, which is the
        # part of the reference fragment before the first slash (or the whole
        # fragment, if there's no slash). Also, grab the correct schema from the
        # cache.

        if ref_uri is not "":
            dereferenced_json = {"": self.refs[ref_uri]}
        else:
            dereferenced_json = {"": parent_schema}


        for reference_token in ref_fragment.split('/'):
            # Replace JSON Pointer escape sequences
            reference_token = reference_token.replace("~1", "/").replace("~0", "~")

            try:
                dereferenced_json = dereferenced_json[reference_token]
            except KeyError:
                raise LoadRAMLError(
                    "Invalid JSON ref: '{token}' not found in {keys}".format(
                        token=reference_token,
                        keys=dereferenced_json.keys()
                    )
                )
        return dereferenced_json

    def _parse_json_refs(self, schema, base_path=None, parent_schema=None):
        """
        Traverses the json schema and resolves the ref pointers recursively
        """

        if parent_schema is None: parent_schema = schema
        expanded = copy.deepcopy(schema)
        if isinstance(schema, dict):
            for k, v in schema.items():
                if isinstance(v, dict):
                    expanded[k] = self._parse_json_refs(v, base_path, parent_schema=parent_schema)
                elif isinstance(v, list):
                    for idx in xrange(len(v)):
                        expanded[k][idx] = self._parse_json_refs(
                            v[idx], base_path, parent_schema=parent_schema
                        )
                elif k == '$ref':
                    return  self._lookup_json_ref(v, base_path=base_path, parent_schema=parent_schema)
        return expanded

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

        self._ordered_loader = OrderedLoader

        return yaml.load(stream, OrderedLoader)

    def load(self, raml):
        """
        Loads the desired RAML file and returns data.

        :param raml: Either a string/unicode path to RAML file, a file object,\
            or string-representation of RAML.

        :return: Data from RAML file
        :rtype: ``dict``
        """

        try:
            return self._ordered_load(raml, yaml.SafeLoader)
        except yaml.parser.ParserError as e:
            msg = "Error parsing RAML: {0}".format(e)
            raise LoadRAMLError(msg)
        except yaml.constructor.ConstructorError as e:
            msg = "Error parsing RAML: {0}".format(e)
            raise LoadRAMLError(msg)
