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
from six.moves.urllib.parse import urlparse

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
                    parsed, os.path.dirname(file_name)
                )
            return parsed

    def _lookup_json_ref(self, ref_key, base_path=None):
        ref_source, ref_fragment = ref_key.split("#/")

        # Determine the correct identifier
        relative_path = os.path.join(base_path, ref_source)
        file_name, uri = None, None
        if ref_source.startswith('/'):  # Absolute path
            file_name = ref_source if os.path.isfile(ref_source) else None
        elif bool(urlparse(ref_source).scheme):  # URL
            uri = ref_source
        elif base_path and os.path.exists(relative_path):
            file_name = relative_path
        else:
            raise LoadRAMLError(
                "Invalid JSON ref: unable to process {src}".format(
                    src=ref_source
                )
            )

        # Load the ref if we dont have it
        if ref_source not in self.refs.keys():
            if file_name is not None:
                with open(file_name) as reffed_file:
                    self.refs[file_name] = yaml.load(
                        reffed_file,
                        self._ordered_loader
                    )
            elif uri is not None:
                response = download_url(uri)
                self.refs[uri] = yaml.load(response)

        reffed_json = self.refs[file_name if file_name else uri]

        # If no path, use the whole object, otherwise down the hole we go
        for key in filter(lambda x: len(x) > 0, ref_fragment.split('/')):
            try:
                reffed_json = reffed_json[key]
            except KeyError:
                raise LoadRAMLError(
                    "Invalid JSON ref: {fragment} not found in {keys}".format(
                        fragment=ref_fragment,
                        keys=reffed_json.keys()
                    )
                )

        return reffed_json

    def _parse_json_refs(self, schema, base_path=None):
        expanded = copy.deepcopy(schema)
        if type(schema) in [dict, OrderedDict]:
            for k, v in schema.items():
                if type(v) in [dict, OrderedDict]:
                    expanded[k] = self._parse_json_refs(v, base_path)
                elif type(v) == list:
                    for idx in xrange(len(v)):
                        expanded[k][idx] = self._parse_json_refs(
                            v[idx], base_path
                        )
                elif k == '$ref':
                    # For a $ref, dereference it
                    del expanded['$ref']
                    expanded.update(
                        self._lookup_json_ref(v, base_path=base_path)
                    )
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
