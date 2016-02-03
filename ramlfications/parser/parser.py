# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function


from abc import ABCMeta, abstractmethod

import re

from six import iterkeys, itervalues, iteritems

from ramlfications.parameters import Documentation
from ramlfications.raml import RootNode, ResourceNode
from ramlfications.utils import load_schema
from ramlfications.utils.parser import (
    parse_assigned_dicts, resolve_inherited_scalar, sort_uri_params
)

from .parameters import create_param_objs


class AbstractBaseParser(object):
    """
    Base parser for Python-RAML objects to inherit from
    """
    __metaclass__ = ABCMeta

    def __init__(self, data, config):
        self.data = data
        self.config = config

    @abstractmethod
    def create_node(self):
        pass


# TODO: this probably needs a better name as it wouldn't be used for
# objects like DataTypes etc
class RAMLParser(AbstractBaseParser):
    """
    Base parser for RAML objects
    """
    def __init__(self, data, config):
        super(RAMLParser, self).__init__(data, config)

    @abstractmethod
    def protocols(self):
        pass

    @abstractmethod
    def base_uri_params(self):
        pass

    @abstractmethod
    def uri_params(self):
        pass

    @abstractmethod
    def media_type(self):
        pass


class RootParser(RAMLParser):
    """
    Parses raw RAML data to create :py:class:`ramlfications.raml.RootNode` \
    object.
    """
    def __init__(self, data, config):
        super(RootParser, self).__init__(data, config)
        self.errors = []
        self.uri = data.get("baseUri", "")
        self.kwargs = {}
        self.base = None

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

    def base_uri_params(self):
        return create_param_objs("baseUriParameters", **self.kwargs)

    def uri_params(self):
        self.kwargs["base"] = self.base
        return create_param_objs("uriParameters", **self.kwargs)

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

    def create_node(self):
        self.kwargs = dict(
            data=self.data,
            uri=self.uri,
            method=None,
            errs=self.errors,
            conf=self.config,
        )
        self.base = self.base_uri_params()
        node = dict(
            raml_obj=self.data,
            raw=self.data,
            title=self.data.get("title", ""),
            version=self.data.get("version"),
            protocols=self.protocols(),
            base_uri=self.base_uri(),
            base_uri_params=self.base,
            uri_params=self.uri_params(),
            media_type=self.media_type(),
            documentation=self.docs(),
            schemas=self.schemas(),
            secured_by=self.data.get("securedBy"),
            config=self.config,
            errors=self.errors,
        )
        return RootNode(**node)


class BaseNodeParser(RAMLParser):
    def __init__(self, data, root, config):
        super(BaseNodeParser, self).__init__(data, config)
        self.root = root
        self.name = None
        self.kwargs = {}
        self.resolve_from = []  # Q: what should the default be?

    def create_base_node(self):
        node = dict(
            name=self.name,
            root=self.root,
            raw=self.kwargs.get("data", {}),
            desc=self.description(),
            protocols=self.protocols(),
            headers=self.headers(),
            body=self.body(),
            responses=self.responses(),
            base_uri_params=self.base_uri_params(),
            uri_params=self.uri_params(),
            query_params=self.query_params(),
            form_params=self.form_params(),
            errors=self.root.errors,
        )
        return node

    def create_param_objects(self, item):
        return create_param_objs(item, self.resolve_from, **self.kwargs)

    def resolve_inherited(self, item):
        return resolve_inherited_scalar(item, self.resolve_from, **self.kwargs)

    def display_name(self):
        # only care about method and resource-level data
        self.resolve_from = ["method", "resource"]
        ret = self.resolve_inherited("displayName")
        return ret or self.name

    def description(self):
        return self.resolve_inherited("description")

    def protocols(self):
        ret = self.resolve_inherited("protocols")

        if not ret:
            return [self.root.base_uri.split("://")[0].upper()]
        return ret

    def headers(self):
        return self.create_param_objects("headers")

    def body(self):
        return self.create_param_objects("body")

    def responses(self):
        return self.create_param_objects("responses")

    def uri_params(self):
        return self.create_param_objects("uriParameters")

    def base_uri_params(self):
        return self.create_param_objects("baseUriParameters")

    def query_params(self):
        return self.create_param_objects("queryParameters")

    def form_params(self):
        return self.create_param_objects("formParameters")

    def is_(self):
        return self.resolve_inherited("is")

    def type_(self):
        return self.resolve_inherited("type")


class TraitTypeMixin(object):
    pass


class ResourceParser(BaseNodeParser, TraitTypeMixin):
    def __init__(self, data, root, config):
        super(ResourceParser, self).__init__(data, root, config)
        self.avail = root.config.get("http_optional")
        self.nodes = []
        self.parent = None
        self.method = None
        self.child_data = {}
        self.method_data = None
        self.resolve_from = ["method", "resource", "types", "traits", "root"]
        self.node = {}
        self.path = None
        self.protos = None
        self.uri = None
        self.assigned_type = None

    def create_nodes(self, nodes):
        for k, v in list(iteritems(self.data)):
            if k.startswith("/"):
                self.name = k
                self.child_data = v
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
                self.parent = child
                nodes = self.create_nodes()

        return nodes

    def absolute_uri(self):
        self.uri = self.root.base_uri + self.path
        if self.protos:
            self.uri = self.uri.split("://")
            if len(self.uri) == 2:
                self.uri = self.uri[1]
            if self.root.protocols:
                self.uri = self.protos[0].lower() + "://" + self.uri
                _protos = list(set(self.root.protocols) & set(self.protos))
                if _protos:
                    self.uri = _protos[0].lower() + "://" + self.uri
        return self.uri

    def protocols(self):
        if self.kwargs.get("parent_data"):
            self.resolve_from.insert(-1, "parent")
        # hmm does this work as intended?
        protos = super(ResourceParser, self).protocols()
        if self.kwargs.get("parent_data"):
            self.resolve_from.remove(-1, "parent")
        return protos

    def uri_params(self):
        if self.kwargs.get("parent_data"):
            self.resolve_from.insert(2, "parent")
        # hmm does this work as intended?
        params = super(ResourceParser, self).uri_params()
        if self.kwargs.get("parent_data"):
            self.resolve_from.remove(2, "parent")
        return params

    def create_node_dict(self):
        self.node = self.create_base_node()
        self.assigned_type = parse_assigned_dicts(self.node["type"])

        self.node["absolute_uri"] = self.absolute_uri()
        self.node["parent"] = self.parent
        self.node["path"] = self.path
        self.node["resource_type"] = self.resource_type(self.assigned_type)
        self.node["media_type"] = self.media_type()
        self.node["method"] = self.method
        self.node["raw"] = self.data
        self.node["uri_params"] = sort_uri_params(
            self.node["uri_params"], self.node["absolute_uri"]
        )
        self.node["base_uri_params"] = sort_uri_params(
            self.node["base_uri_params"], self.node["absolute_uri"]
        )

    def create_node(self):
        self.method_data = {}
        if self.method is not None:
            self.method_data = self.data.get(self.method, {})
        self.path = self.resource_path()
        self.protos = self.protocols()
        self.kwargs = dict(
            data=self.method_data,
            method=self.method,
            resource_data=self.data,
            parent_data=getattr(self.parent, "raw", {}),
            root=self.root,
            resource_path=self.path,
            conf=self.root.config,
            errs=self.root.errors,
        )

        self.create_node_dict()

        return ResourceNode(**self.node)
