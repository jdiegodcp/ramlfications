# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function


from six import iterkeys, itervalues

from ramlfications.utils import NodeList
from ramlfications.utils.parser import resolve_inherited_scalar
from .parameters import ParameterParser


class BaseParser(object):
    """
    Base parser from which Python-RAML objects to inherit.
    """
    def __init__(self, data, config):
        self.data = data
        self.config = config
        self.kw = {}
        self.resolve_from = []

    def create_node(self):
        raise NotImplemented()

    def create_node_dict(self):
        raise NotImplemented()

    def create_param_objects(self, param):
        """
        Create a :py:class:`ramlfications.parameters` object.

        :param str param: RAML parameter name to parse (e.g. uriParameters)
        :ret: :py:class:`ramlfications.parameters` object
        """
        param_parser = ParameterParser(param, self.kw, self.resolve_from)
        return param_parser.parse()


class BaseNodeParser(BaseParser):
    raml_property = None

    def __init__(self, data, root, config):
        super(BaseNodeParser, self).__init__(data, config)
        self.root = root
        self.avail = root.config.get("http_optional")
        self.name = None
        self.method = None

    def create_nodes(self):
        data = self.data.get(self.raml_property, [])
        node_objects = NodeList()

        for d in data:
            self.name = list(iterkeys(d))[0]
            self.data = list(itervalues(d))[0]
            node_objects.append(self.create_node())

        return node_objects

    def create_node_dict(self):
        return {
            "name": self.name,
            "root": self.root,
            "raw": self.kw.get("data", {}),
            "headers": self.create_param_objects("headers"),
            "body": self.create_param_objects("body"),
            "responses": self.create_param_objects("responses"),
            "uri_params": self.create_param_objects("uriParameters"),
            "base_uri_params": self.create_param_objects("baseUriParameters"),
            "query_params": self.create_param_objects("queryParameters"),
            "form_params": self.create_param_objects("formParameters"),
            "media_type": self.resolve_inherited("mediaType"),
            "desc": self.resolve_inherited("description"),
            "protocols": self.protocols(),
            "errors": self.root.errors,
        }

    def resolve_inherited(self, item):
        return resolve_inherited_scalar(item, self.resolve_from, **self.kw)

    def display_name(self):
        # Not used in TraitParser but left in BaseNodeParser to have access
        # for any new parsers to use
        # only care about method and resource-level data
        res = ["method", "resource"]
        ret = resolve_inherited_scalar("displayName", res, **self.kw)
        return ret or self.name

    def protocols(self):
        ret = self.resolve_inherited("protocols")

        if not ret:
            return [self.root.base_uri.split("://")[0].upper()]
        return ret

    # TODO this is actually already defined in .utils.common
    def get_data_from_kwargs(self, item, data_default={}, item_default=None):
        data = self.kw.get("data", data_default)
        return data.get(item, item_default)
