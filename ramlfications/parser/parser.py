# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function


import re

from six import iterkeys, itervalues, iteritems

from ramlfications.parameters import Documentation
from ramlfications.raml import (
    ResourceNode, RAML_ROOT_LOOKUP, TraitNode, ResourceTypeNode,
    SecuritySchemeNode
)
from ramlfications.utils import load_schema, NodeList
from ramlfications.utils.common import _map_attr
from ramlfications.utils.parser import sort_uri_params
from ramlfications.types import create_type

from .base import BaseParser, BaseNodeParser
from .mixins import HelperMixin


parsers = []


def collectparser(kls):
    def klass():
        if kls not in parsers:
            parsers.append(kls)
    klass()
    return kls


class RAMLParser(object):
    """
    Main RAML Parser

    :param dict data: raw RAML data
    :param dict config: parser configuration

    :ret: A `RootNodeAPI` object
    """
    def __init__(self, data, config):
        self.data = data
        self.config = config

    def parse(self):
        root_parser = RootParser(self.data, self.config)
        root = root_parser.create_node()
        for p in parsers:
            parser = p(self.data, root, self.config)
            nodes = parser.create_nodes()
            setattr(root, p.root_property, nodes)

        resource_parser = ResourceParser(self.data, root, self.config)
        root.resources = resource_parser.create_nodes(nodes=NodeList())
        return root


class RootParser(BaseParser):
    """
    Parses raw RAML data into a RootNodeAPI object.

    :param dict data: raw RAML data
    :param dict config: parser configuration

    :ret: :py:class:`ramlfications.raml.RootNodeAPI` object
    """
    def __init__(self, data, config):
        super(RootParser, self).__init__(data, config)
        self.uri = data.get("baseUri", "")
        self.errors = []
        self.base = None
        self.raml_version = None

    def protocols(self):
        explicit_protos = self.data.get("protocols")
        implicit_protos = re.findall(r"(https|http)", self.base_uri())
        implicit_protos = [p.upper() for p in implicit_protos]

        return explicit_protos or implicit_protos or None

    def media_type(self):
        return self.data.get("mediaType")

    def base_uri(self):
        base_uri = self.data.get("baseUri", "")
        if "{version}" in base_uri:
            version = str(self.data.get("version", ""))
            base_uri = base_uri.replace("{version}", version)
        return base_uri

    def docs(self):
        d = self.data.get("documentation", [])
        assert isinstance(d, list), "Error parsing documentation"
        docs = [Documentation(i.get("title"), i.get("content")) for i in d]
        return docs or None

    def schemas(self):
        _schemas = self.data.get("schemas")
        if not _schemas:
            return None
        schemas = []
        for s in _schemas:
            value = load_schema(list(itervalues(s))[0])
            schemas.append({list(iterkeys(s))[0]: value})
        return schemas or None

    def create_node_dict(self):
        self.node["raml_obj"] = self.data
        self.node["raw"] = self.data
        self.node["raml_version"] = self.data._raml_version
        self.node["title"] = self.data.get("title", "")
        self.node["version"] = self.data.get("version")
        self.node["protocols"] = self.protocols()
        self.node["base_uri"] = self.base_uri()
        self.node["base_uri_params"] = self.base
        self.node["uri_params"] = self.create_param_objects("uriParameters")
        self.node["media_type"] = self.media_type()
        self.node["documentation"] = self.docs()
        self.node["schemas"] = self.schemas()
        self.node["secured_by"] = self.data.get("securedBy")
        self.node["config"] = self.config
        self.node["errors"] = self.errors

    def create_node(self):
        self.kw["data"] = self.data
        self.kw["uri"] = self.uri
        self.kw["method"] = None
        self.kw["errs"] = self.errors
        self.kw["conf"] = self.config

        self.base = self.create_param_objects("baseUriParameters")
        self.kw["base"] = self.base

        self.create_node_dict()

        return RAML_ROOT_LOOKUP[self.data._raml_version](**self.node)


@collectparser
class SecuritySchemeParser(BaseNodeParser):
    """
    Parse raw RAML data to create `SecurityScheme` objects, if any.
    """
    raml_property = "securitySchemes"
    root_property = "security_schemes"

    def __init__(self, data, root, config):
        super(SecuritySchemeParser, self).__init__(data, root, config)
        self.resolve_from = ["method"]

    def _map_object_types(self, item):
        return {
            "usage": self.usage,
            "mediaType": self.media_type,
            "protocols": self.protocols,
            "documentation": self.documentation,
        }[item]

    def _set_property(self, node, obj, node_data):
        data = {obj: node_data}
        self.kw["data"] = data
        try:
            item_objs = self._map_object_types(obj)()
        except KeyError:
            item_objs = self.create_param_objects(obj)

        attr = _map_attr(obj)
        setattr(node, attr, item_objs)

    def _described_by_properties(self, node):
        for obj, node_data in list(iteritems(self.node.get("described_by"))):
            self._set_property(node, obj, node_data)
        return node

    def usage(self):
        return self.get_data_from_kwargs("usage")

    def media_type(self):
        return self.get_data_from_kwargs("mediaType")

    def protocols(self):
        return self.get_data_from_kwargs("protocols")

    def documentation(self):
        d = self.get_data_from_kwargs("documentation", {}, [])
        assert isinstance(d, list), "Error parsing documentation"
        docs = [Documentation(i.get("title"), i.get("content")) for i in d]
        return docs or None

    def create_node_dict(self):
        self.node = super(SecuritySchemeParser, self).create_node_dict()

        self.node["type"] = self.data.get("type")
        self.node["config"] = self.root.config
        self.node["settings"] = self.data.get("settings")
        self.node["described_by"] = self.data.get("describedBy", {})

    def create_node(self):
        self.kw["data"] = self.data
        self.kw["method"] = self.method
        self.kw["root"] = self.root

        self.create_node_dict()

        node = SecuritySchemeNode(**self.node)
        return self._described_by_properties(node)


@collectparser
class TraitParser(BaseNodeParser):
    """
    Parse raw RAML data to create `TraitNode` objects, if any.
    """
    raml_property = "traits"
    root_property = "traits"

    def __init__(self, data, root, config):
        super(TraitParser, self).__init__(data, root, config)
        self.resolve_from = ["method"]

    def create_node_dict(self):
        self.node = super(TraitParser, self).create_node_dict()
        self.node["usage"] = self.data.get("usage")

    def create_node(self):
        self.kw = dict(
            data=self.data,
            resource_data=self.data,
            root=self.root,
            conf=self.root.config,
            errs=self.root.errors,
        )

        self.create_node_dict()

        return TraitNode(**self.node)


@collectparser
class ResourceTypeParser(BaseNodeParser, HelperMixin):
    """
    Parses raw RAML data to create `ResourceTypeNode` objects, if any.
    """
    raml_property = "resourceTypes"
    root_property = "resource_types"

    def __init__(self, data, root, config):
        super(ResourceTypeParser, self).__init__(data, root, config)
        self.resolve_from = ["method", "resource", "types", "traits", "root"]

    def optional(self):
        if self.method:
            return "?" in self.method

    def method_(self):
        if not self.method:
            return None
        if "?" in self.method:
            return self.method[:-1]
        return self.method

    def create_node_dict(self):
        self.node = super(ResourceTypeParser, self).create_node_dict()

        self.node["is_"] = self.is_()
        self.node["type"] = self.type_()
        self.node["usage"] = self.data.get("usage")
        self.node["method"] = self.method_()
        self.node["traits"] = self.traits()
        self.node["optional"] = self.optional()
        self.node["secured_by"] = self.secured_by()
        self.node["display_name"] = self.display_name()
        self.node["security_schemes"] = self.security_schemes()

    def create_node(self):
        self.kw["data"] = self.method_data
        self.kw["root"] = self.root
        self.kw["method"] = self.method_()
        self.kw["resource_data"] = self.data

        self.is__ = self.is_()
        self.type__ = self.type_()
        self.kw["is_"] = self.is__
        self.kw["type_"] = self.type__

        self.create_node_dict()

        return ResourceTypeNode(**self.node)

    def create_nodes(self):
        resource_types = self.data.get(self.raml_property, [])
        resource_type_objects = NodeList()

        for res in resource_types:
            for k, v in list(iteritems(res)):
                self.name = k
                self.data = v
                self.method = None
                self.method_data = {}
                if isinstance(v, dict):
                    values = list(iterkeys(v))
                    methods = [m for m in self.avail if m in values]
                    # it's possible for resource types to not define methods
                    if len(methods) == 0:
                        node = self.create_node()
                        resource_type_objects.append(node)
                    else:
                        for meth in methods:
                            self.method = meth
                            self.method_data = self.data.get(self.method, {})
                            node = self.create_node()
                            resource_type_objects.append(node)
                # is it ever not a dictionary?
                # yes, if there's an empty mapping
                else:
                    self.data = {}
                    node = self.create_node()
                    resource_type_objects.append(node)
        return resource_type_objects


class ResourceParser(BaseNodeParser, HelperMixin):
    """
    Parses raw RAML data to create `ResourceTypeNode` objects, if any.
    """
    def __init__(self, data, root, config):
        super(ResourceParser, self).__init__(data, root, config)
        self.resolve_from = [
            "method", "resource", "types", "traits", "parent", "root"
        ]
        self.parent = None
        self.child_data = {}
        self.method_data = {}
        self.protos = None
        self.uri = None
        self.path = None

    def absolute_uri(self):
        self.uri = self.root.base_uri + self.path
        if self.protos:
            self.uri = self.uri.split("://")
            if len(self.uri) == 2:
                self.uri = self.uri[1]
            if self.root.protocols:
                _protos = list(set(self.root.protocols) & set(self.protos))
                if _protos:
                    self.uri = _protos[0].lower() + "://" + self.uri
        return self.uri

    def resource_path(self):
        parent_path = ""
        if self.parent:
            parent_path = self.parent.path
        return parent_path + self.name

    def create_node_dict(self):
        self.node = super(ResourceParser, self).create_node_dict()

        abs_uri = self.absolute_uri()
        uri_params = self.node.get("uri_params")
        base_uri_params = self.node.get("base_uri_params")

        self.node["raw"] = self.child_data
        self.node["path"] = self.path
        self.node["method"] = self.method
        self.node["parent"] = self.parent

        self.node["display_name"] = self.display_name()
        self.node["absolute_uri"] = abs_uri
        if uri_params:
            self.node["uri_params"] = sort_uri_params(
                uri_params, abs_uri
            )
        if base_uri_params:
            self.node["base_uri_params"] = sort_uri_params(
                base_uri_params, abs_uri
            )
        self.node["is_"] = self.is__
        self.node["type"] = self.type__
        self.node["traits"] = self.traits()
        self.node["secured_by"] = self.secured_by()
        self.node["resource_type"] = self.resource_type()
        self.node["security_schemes"] = self.security_schemes()

    def create_node(self):
        if self.method is not None:
            self.method_data = self.child_data.get(self.method, {})

        self.path = self.resource_path()

        self.kw["data"] = self.method_data
        self.kw["root"] = self.root
        self.kw["method"] = self.method
        self.kw["parent_data"] = getattr(self.parent, "raw", {})
        self.kw["resource_path"] = self.path
        self.kw["resource_data"] = self.child_data

        self.is__ = self.is_()
        self.type__ = self.type_()
        self.kw["is_"] = self.is__
        self.kw["type_"] = self.type__

        self.protos = self.protocols()

        self.create_node_dict()

        return ResourceNode(**self.node)

    def create_nodes(self, nodes, parent=None):
        for k, v in list(iteritems(self.data)):
            if k.startswith("/"):
                self.parent = parent

                self.name = k
                self.child_data = v
                self.data = self.child_data
                methods = [m for m in self.avail if m in list(iterkeys(v))]
                if methods:
                    for m in methods:
                        self.method = m
                        child = self.create_node()
                        nodes.append(child)
                else:
                    self.method = None
                    child = self.create_node()
                    nodes.append(child)
                nodes = self.create_nodes(nodes, child)

        return nodes
