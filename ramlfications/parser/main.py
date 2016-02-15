# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function


import re

from six import iteritems, iterkeys, itervalues


from ramlfications.parameters import (
    Documentation, SecurityScheme
)
from ramlfications.raml import (
    RootNodeAPI08, RootNodeAPI10, ResourceTypeNode, TraitNode, ResourceNode
)
from ramlfications.utils import load_schema

# Private utility functions
from ramlfications.utils.common import _get
from ramlfications.utils.parser import (
    parse_assigned_dicts, resolve_inherited_scalar, sort_uri_params
)
from ramlfications.types import create_type

from .parameters import create_param_objs


def create_root(raml, config):
    """
    Creates a :py:class:`.raml.RootNodeAPI08` based off of the RAML's root
    section.

    :param RAMLDict raml: loaded RAML file
    :returns: :py:class:`.raml.RootNodeAPI08` object with API root attributes.
    """

    errors = []

    def protocols():
        explicit_protos = _get(raml, "protocols")
        implicit_protos = re.findall(r"(https|http)", base_uri())
        implicit_protos = [p.upper() for p in implicit_protos]

        return explicit_protos or implicit_protos or None

    def base_uri():
        base_uri = _get(raml, "baseUri", "")
        if "{version}" in base_uri:
            base_uri = base_uri.replace("{version}",
                                        str(_get(raml, "version")))
        return base_uri

    def base_uri_params(kwargs):
        return create_param_objs("baseUriParameters", **kwargs)

    def uri_params(kwargs):
        kwargs["base"] = base
        return create_param_objs("uriParameters", **kwargs)

    def docs():
        d = _get(raml, "documentation", [])
        assert isinstance(d, list), "Error parsing documentation"
        docs = [Documentation(_get(i, "title"), _get(i, "content")) for i in d]
        return docs or None

    def schemas():
        _schemas = _get(raml, "schemas")
        if not _schemas:
            return None
        schemas = []
        for schema in _schemas:
            value = load_schema(list(itervalues(schema))[0])
            schemas.append({list(iterkeys(schema))[0]: value})
        return schemas or None

    def types():
        _types = _get(raml, "types")
        if not _types:
            return None
        return [
            create_type(k, v) for k, v in iteritems(_types)]

    uri = _get(raml, "baseUri", "")
    kwargs = dict(data=raml,
                  uri=uri,
                  method=None,
                  errs=errors,
                  conf=config)
    base = base_uri_params(kwargs)
    if raml._raml_version == "0.8":
        return RootNodeAPI08(
            raml_obj=raml,
            raw=raml,
            raml_version=raml._raml_version,
            title=_get(raml, "title"),
            version=_get(raml, "version"),
            protocols=protocols(),
            base_uri=base_uri(),
            base_uri_params=base_uri_params(kwargs),
            uri_params=uri_params(kwargs),
            media_type=_get(raml, "mediaType"),
            documentation=docs(),
            schemas=schemas(),
            config=config,
            secured_by=_get(raml, "securedBy"),
            errors=errors,
        )
    elif raml._raml_version == "1.0":
        return RootNodeAPI10(
            raml_obj=raml,
            raw=raml,
            raml_version=raml._raml_version,
            title=_get(raml, "title"),
            version=_get(raml, "version"),
            protocols=protocols(),
            base_uri=base_uri(),
            base_uri_params=base_uri_params(kwargs),
            uri_params=uri_params(kwargs),
            media_type=_get(raml, "mediaType"),
            documentation=docs(),
            schemas=schemas(),
            config=config,
            secured_by=_get(raml, "securedBy"),
            errors=errors,
            types=types(),
        )


def create_sec_schemes(raml_data, root):
    """
    Parse security schemes into :py:class:.raml.SecurityScheme` objects

    :param dict raml_data: Raw RAML data
    :param RootNodeAPI08 root: Root Node
    :returns: list of :py:class:`.parameters.SecurityScheme` objects
    """
    schemes = _get(raml_data, "securitySchemes", [])
    scheme_objs = []
    for s in schemes:
        name = list(iterkeys(s))[0]
        data = list(itervalues(s))[0]
        node = _create_sec_scheme_node(name, data, root)
        scheme_objs.append(node)
    return scheme_objs or None


def _create_sec_scheme_node(name, data, root):
    """
    Create a :py:class:`.raml.SecurityScheme` object.

    :param str name: Name of the security scheme
    :param dict data: Raw method-level RAML data associated with \
        security scheme
    :param RootNodeAPI08 root: API ``RootNodeAPI08`` that the security scheme \
        attached to
    :returns: :py:class:`.raml.SecurityScheme` object
    """
    def _map_object_types(item):
        return {
            "headers": headers,
            "body": body,
            "responses": responses,
            "queryParameters": query_params,
            "uriParameters": uri_params,
            "formParameters": form_params,
            "usage": usage,
            "mediaType": media_type,
            "protocols": protocols,
            "documentation": documentation,
        }[item]

    def headers(kwargs):
        return create_param_objs("headers", **kwargs)

    def body(kwargs):
        return create_param_objs("body", **kwargs)

    def responses(kwargs):
        return create_param_objs("responses", **kwargs)

    def query_params(kwargs):
        return create_param_objs("queryParameters", **kwargs)

    def uri_params(kwargs):
        return create_param_objs("uriParameters", **kwargs)

    def form_params(kwargs):
        return create_param_objs("formParameters", **kwargs)

    def usage(kwargs):
        data = _get(kwargs, "data")
        return _get(data, "usage")

    def media_type(kwargs):
        data = _get(kwargs, "data")
        return _get(data, "mediaType")

    def protocols(kwargs):
        data = _get(kwargs, "data")
        return _get(data, "protocols")

    def documentation(kwargs):
        d = _get(kwargs, "data", {})
        d = _get(d, "documentation", [])
        assert isinstance(d, list), "Error parsing documentation"
        docs = [Documentation(_get(i, "title"), _get(i, "content")) for i in d]
        return docs or None

    def set_property(node, obj, node_data):
        func = _map_object_types(obj)
        data = {obj: node_data}
        kwargs["data"] = data
        item_objs = func(kwargs)
        setattr(node, func.__name__, item_objs)

    def initial_wrap(key, data):
        return SecurityScheme(
            name=key,
            raw=data,
            type=_get(data, "type"),
            described_by=_get(data, "describedBy", {}),
            desc=_get(data, "description"),
            settings=_get(data, "settings"),
            config=root.config,
            errors=root.errors
        )

    def final_wrap(node):
        for obj, node_data in list(iteritems(node.described_by)):
            set_property(node, obj, node_data)
        return node

    method = None
    kwargs = dict(
        data=data,
        method=method,
        conf=root.config,
        errs=root.errors,
        root=root
    )
    node = initial_wrap(name, data)
    return final_wrap(node)


def create_traits(raml_data, root):
    """
    Parse traits into :py:class:`.raml.TraitNode` objects.

    :param dict raml_data: Raw RAML data
    :param RootNodeAPI08 root: Root Node
    :returns: list of :py:class:`.raml.TraitNode` objects
    """
    traits = _get(raml_data, "traits", [])
    trait_objects = []

    for trait in traits:
        name = list(iterkeys(trait))[0]
        data = list(itervalues(trait))[0]
        trait_objects.append(_create_trait_node(name, data, root))
    return trait_objects or None


def _create_trait_node(name, data, root):
    """
    Create a ``.raml.TraitNode`` object.

    :param str name: Name of trait node
    :param dict data: Raw method-level RAML data associated with \
        trait node
    :param str method: HTTP method associated with resource type node
    :param RootNodeAPI08 root: API ``RootNodeAPI08`` that the trait node is \
        attached to
    :returns: :py:class:`.raml.TraitNode` object
    """
    method = None
    kwargs = dict(
        data=data,
        method=method,
        root=root,
        errs=root.errors,
        conf=root.config
    )
    resolve_from = ["method"]
    node = _create_base_node(name, root, "trait", kwargs, resolve_from)
    node["usage"] = _get(data, "usage")
    node["media_type"] = _get(data, "mediaType")
    return TraitNode(**node)


def create_resource_types(raml_data, root):
    """
    Parse resourceTypes into :py:class:`.raml.ResourceTypeNode` objects.

    :param dict raml_data: Raw RAML data
    :param RootNodeAPI08 root: Root Node
    :returns: list of :py:class:`.raml.ResourceTypeNode` objects
    """
    accepted_methods = _get(root.config, "http_optional")

    resource_types = _get(raml_data, "resourceTypes", [])
    resource_type_objects = []

    for res in resource_types:
        for k, v in list(iteritems(res)):
            if isinstance(v, dict):
                values = list(iterkeys(v))
                methods = [m for m in accepted_methods if m in values]
                # it's possible for resource types to not define methods
                if len(methods) == 0:
                    meth = None
                    resource = _create_resource_type_node(k, {}, meth,
                                                          v, root)
                    resource_type_objects.append(resource)
                else:
                    for meth in methods:
                        method_data = _get(v, meth, {})
                        resource = _create_resource_type_node(k, method_data,
                                                              meth, v, root)
                        resource_type_objects.append(resource)
            # is it ever not a dictionary?
            else:
                meth = None
                resource = _create_resource_type_node(k, {}, meth, v, root)
                resource_type_objects.append(resource)

    return resource_type_objects or None


def _create_resource_type_node(name, method_data, method, resource_data, root):
    """
    Create a :py:class:`.raml.ResourceTypeNode` object.

    :param str name: Name of resource type node
    :param dict method_data: Raw method-level RAML data associated with \
        resource type node
    :param str method: HTTP method associated with resource type node
    :param dict resource_data: Raw resource-level RAML data associated with \
        resource type node
    :param RootNodeAPI08 root: API ``RootNodeAPI08`` that the resource type\
        node is attached to
    :returns: :py:class:`.raml.ResourceTypeNode` object
    """
    #####
    # Set ResourceTypeNode attributes
    def method_():
        if not method:
            return None
        if "?" in method:
            return method[:-1]
        return method

    def optional():
        if method:
            return "?" in method

    def create_node_dict():
        resolve_from = ["method", "resource", "types", "traits", "root"]
        node = _create_base_node(name, root, "resource_type",
                                 kwargs, resolve_from)
        node["media_type"] = _get(resource_data, "mediaType")
        node["optional"] = optional()
        node["method"] = _get(kwargs, "method")
        node["usage"] = _get(resource_data, "usage")
        return node

    kwargs = dict(
        data=method_data,
        resource_data=resource_data,
        method=method_(),
        root=root,
        errs=root.errors,
        conf=root.config
    )
    node = create_node_dict()
    return ResourceTypeNode(**node)


def create_resources(node, resources, root, parent):
    """
    Recursively traverses the RAML file via DFS to find each resource
    endpoint.

    :param dict node: Dictionary of node to traverse
    :param list resources: List of collected ``.raml.ResourceNode`` s
    :param RootNodeAPI08 root: The ``.raml.RootNodeAPI08`` of the API
    :param ResourceNode parent: Parent ``.raml.ResourceNode`` of current \
        ``node``
    :returns: List of :py:class:`.raml.ResourceNode` objects.
    """
    avail = _get(root.config, "http_optional")
    for k, v in list(iteritems(node)):
        if k.startswith("/"):
            methods = [m for m in avail if m in list(iterkeys(v))]
            if methods:
                for m in methods:
                    child = _create_resource_node(name=k, raw_data=v, method=m,
                                                  parent=parent, root=root)
                    resources.append(child)
            else:
                child = _create_resource_node(name=k, raw_data=v, method=None,
                                              parent=parent, root=root)
                resources.append(child)
            resources = create_resources(child.raw, resources, root, child)

    return resources


def _create_resource_node(name, raw_data, method, parent, root):
    """
    Create a :py:class:`.raml.ResourceNode` object.

    :param str name: Name of resource node
    :param dict raw_data: Raw RAML data associated with resource node
    :param str method: HTTP method associated with resource node
    :param ResourceNode parent: Parent node object of resource node, if any
    :param RootNodeAPI08 api: API ``RootNodeAPI08`` that the resource node\
        is attached to
    :returns: :py:class:`.raml.ResourceNode` object
    """
    #####
    # Node attribute functions
    #####
    def path():
        parent_path = ""
        if parent:
            parent_path = parent.path
        return parent_path + name

    def absolute_uri(path, protocols):
        uri = root.base_uri + path
        if protocols:
            uri = uri.split("://")
            if len(uri) == 2:
                uri = uri[1]
            if root.protocols:
                # find shared protocols
                _protos = list(set(root.protocols) & set(protocols))
                # if resource protocols and root protocols share a protocol
                # then use that one
                if _protos:
                    uri = _protos[0].lower() + "://" + uri
                # if no shared protocols, use the first of the resource
                # protocols
                else:
                    uri = protocols[0].lower() + "://" + uri
        return uri

    def media_type():
        if method is None:
            return None
        resolve_from = [
            "method", "traits", "types", "resource", "root"
        ]
        return resolve_inherited_scalar("mediaType", resolve_from, **kwargs)

    def resource_type(assigned_type):
        if assigned_type and root.resource_types:
            res_types = root.resource_types
            type_obj = [r for r in res_types if r.name == assigned_type]
            type_obj = [r for r in type_obj if r.method == method]
            if type_obj:
                return type_obj[0]

    def create_node_dict():
        resolve_from = ["method", "resource", "types", "traits", "root"]
        node = _create_base_node(name, root, "resource", kwargs, resolve_from)

        node["absolute_uri"] = absolute_uri(resource_path,
                                            _get(node, "protocols"))
        assigned_type = parse_assigned_dicts(_get(node, "type"))
        node["parent"] = parent
        node["path"] = resource_path
        node["resource_type"] = resource_type(assigned_type)
        node["media_type"] = media_type()
        node["method"] = method
        node["raw"] = raw_data
        node["uri_params"] = sort_uri_params(node["uri_params"],
                                             node["absolute_uri"])
        node["base_uri_params"] = sort_uri_params(node["base_uri_params"],
                                                  node["absolute_uri"])
        return node

    # Avoiding repeated function calls by calling them once here
    method_data = _get(raw_data, method, {})
    parent_data = getattr(parent, "raw", {})
    resource_path = path()

    kwargs = dict(
        data=method_data,
        method=method,
        resource_data=raw_data,
        parent_data=parent_data,
        root=root,
        resource_path=resource_path,
        conf=root.config,
        errs=root.errors,
    )

    node = create_node_dict()
    return ResourceNode(**node)


def _create_base_node(name, root, node_type, kwargs, resolve_from=[]):
    """
    Create a dictionary of :py:class:`.raml.BaseNode` data.

    :param str name: Name of resource node
    :param RootNodeAPI08 api: API ``RootNodeAPI08`` that the resource node is\
        attached to
    :param str node_type: type of node, e.g. ``resource``, ``resource_type``
    :param dict kwargs: relevant node data to parse out
    :param list resolve_from: order of objects from which the node to \
        inherit data
    :returns: dictionary of :py:class:`.raml.BaseNode` data
    """
    def display_name():
        # only care about method and resource-level data
        resolve_from = ["method", "resource"]
        ret = resolve_inherited_scalar("displayName", resolve_from, **kwargs)
        return ret or name

    def description():
        return resolve_inherited_scalar("description", resolve_from, **kwargs)

    def protocols():
        if _get(kwargs, "parent_data"):
            # should go before "root"
            if "root" in resolve_from:
                index = resolve_from.index("root")
                resolve_from.insert(index, "parent")
            else:
                resolve_from.append("parent")
        ret = resolve_inherited_scalar("protocols", resolve_from, **kwargs)

        if not ret:
            return [root.base_uri.split("://")[0].upper()]
        return ret

    def headers():
        return create_param_objs("headers", resolve_from, **kwargs)

    def body():
        return create_param_objs("body", resolve_from, **kwargs)

    def responses():
        return create_param_objs("responses", resolve_from, **kwargs)

    def uri_params():
        if _get(kwargs, "parent_data"):
            # parent should be after resource
            resolve_from.insert(2, "parent")
        return create_param_objs("uriParameters", resolve_from, **kwargs)

    def base_uri_params():
        return create_param_objs("baseUriParameters", resolve_from, **kwargs)

    def query_params():
        return create_param_objs("queryParameters", resolve_from, **kwargs)

    def form_params():
        return create_param_objs("formParameters", resolve_from, **kwargs)

    def is_():
        return resolve_inherited_scalar("is", resolve_from, **kwargs)

    def type_():
        return resolve_inherited_scalar("type", resolve_from, **kwargs)

    def traits_():
        trait_objs = []
        if not isinstance(assigned_traits, list):
            # I think validate.py would error out so
            # I don't think anything is needed here...
            return None
        for trait in assigned_traits:
            obj = [t for t in root.traits if t.name == trait]
            if obj:
                trait_objs.append(obj[0])
        return trait_objs or None

    def secured_by():
        return resolve_inherited_scalar("securedBy", resolve_from, **kwargs)

    def security_schemes(secured):
        assigned_sec_schemes = parse_assigned_dicts(secured)
        sec_objs = []
        for sec in assigned_sec_schemes:
            obj = [s for s in root.security_schemes if s.name == sec]
            if obj:
                sec_objs.append(obj[0])
        return sec_objs or None

    if node_type in ("resource", "resource_type"):
        _is = is_()
        _type = type_()
        kwargs["is_"] = _is
        kwargs["type_"] = _type

    node = dict(
        name=name,
        root=root,
        raw=_get(kwargs, "data", {}),
        desc=description(),
        protocols=protocols(),
        headers=headers(),
        body=body(),
        responses=responses(),
        base_uri_params=base_uri_params(),
        uri_params=uri_params(),
        query_params=query_params(),
        form_params=form_params(),
        errors=root.errors
    )

    if node_type in ("resource", "resource_type"):
        node["is_"] = _is
        node["type"] = _type
        node["traits"] = None
        assigned_traits = parse_assigned_dicts(_is)
        if assigned_traits and root.traits:
            node["traits"] = traits_()

        node["security_schemes"] = None
        node["secured_by"] = None
        secured = secured_by()
        if secured and root.security_schemes:
            node["security_schemes"] = security_schemes(secured)
            node["secured_by"] = secured

        node["display_name"] = display_name()

    return node
