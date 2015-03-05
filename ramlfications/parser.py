# ! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function
import re

try:
    from collections import OrderedDict
except ImportError:  # pragma: no cover
    from ordereddict import OrderedDict

import attr
from six import iteritems, iterkeys, itervalues


from .base_config import config
from .parameters import (
    Documentation, Header, Body, Response, URIParameter, QueryParameter,
    FormParameter, SecurityScheme
)
from .raml import RootNode, ResourceNode, ResourceTypeNode, TraitNode

__all__ = ["parse_raml"]


def parse_raml(loaded_raml_file):
    root = create_root(loaded_raml_file)
    root.traits = create_traits(root.raml_obj.data, root)
    root.resource_types = create_resource_types(root.raml_obj.data, root)
    root.resources = create_resources(root.raml_obj.data, [], root,
                                      parent=None)
    attr.validate(root)
    return root


def _create_base_param_obj(property_data, param_obj):
    objects = []

    for key, value in list(iteritems(property_data)):
        if param_obj is URIParameter:
            required = value.get("required", True)
        else:
            required = value.get("required", False)
        item = param_obj(
            name=key,
            raw=value,
            description=value.get("description"),
            display_name=value.get("displayName", key),
            min_length=value.get("minLength"),
            max_length=value.get("maxLength"),
            minimum=value.get("minimum"),
            maximum=value.get("maximum"),
            default=value.get("default"),
            enum=value.get("enum"),
            example=value.get("example"),
            required=required,
            repeat=value.get("repeat", False),
            pattern=value.get("pattern"),
            type=value.get("type", "string")
        )
        objects.append(item)

    return objects or None


def create_root(loaded_raml_file):
    """
    Creates a Root Node based off of the RAML's root section.

    :param RAMLDict loaded_raml_file: loaded RAML file
    :ret root: RootNode object with API root properties set
    :rtype: RootNode
    """
    def title():
        return raml.get("title")

    def version():
        return raml.get("version")

    def protocols():
        explicit_protos = raml.get('protocols')
        implicit_protos = re.findall(r"(https|http)", base_uri())

        return explicit_protos or implicit_protos or None

    def base_uri():
        base_uri = raml.get('baseUri', "")
        if "{version}" in base_uri:
            base_uri = base_uri.replace('{version}', str(raml.get('version')))
        return base_uri

    def base_uri_params():
        data = raml.get("baseUriParameters", {})
        return _create_base_param_obj(data, URIParameter)

    def uri_params():
        data = raml.get("uriParameters", {})
        return _create_base_param_obj(data, URIParameter)

    def media_type():
        return raml.get("mediaType")

    def docs():
        d = raml.get('documentation', [])
        assert isinstance(d, list), "Error parsing documentation"
        docs = [Documentation(i.get('title'), i.get('content')) for i in d]
        return docs or None

    def schemas():
        return raml.get("schemas")

    raml = loaded_raml_file.data
    root = RootNode(
        raml_obj=loaded_raml_file,
        raw=raml,
        title=title(),
        version=version(),
        protocols=protocols(),
        base_uri=base_uri(),
        base_uri_params=base_uri_params(),
        uri_params=uri_params(),
        media_type=media_type(),
        docs=docs(),
        schemas=schemas(),
        raml_file=loaded_raml_file.raml_file
    )
    return root


def create_traits(raml_data, root):
    """
    Parse traits into ``Trait`` objects.

    :param dict raml_data: Raw RAML data
    :param RootNode root: Root Node
    :ret: list of ``Trait`` objects
    :rtype: list
    """
    def description():
        return data.get("description")

    def media_type():
        return data.get("mediaType")

    def usage():
        return data.get('usage')

    def protocols():
        return data.get("protocols")

    def query_params():
        params = data.get("queryParameters", {})
        return _create_base_param_obj(params, QueryParameter)

    def uri_params():
        params = data.get("uriParameters", {})
        return _create_base_param_obj(params, URIParameter)

    def form_params():
        params = data.get("formParameters", {})
        return _create_base_param_obj(params, FormParameter)

    def base_uri_params():
        params = data.get("baseUriParameters", {})
        return _create_base_param_obj(params, URIParameter)

    def headers(data):
        headers_ = data.get("headers", {})
        return _create_base_param_obj(headers_, Header)

    def body(data):
        body = data.get("body", {})
        body_objects = []
        for key, value in list(iteritems(body)):
            body = Body(
                mime_type=key,
                raw=value,
                schema=value.get("schema"),
                example=value.get("example"),
                form_params=value.get("formParameters")
            )
            body_objects.append(body)
        return body_objects or None

    def responses():
        response_objects = []
        for key, value in list(iteritems(data.get("responses", {}))):
            response = Response(
                code=key,
                raw=value,
                description=value.get("description"),
                headers=headers(value),
                body=body(value)
            )
            response_objects.append(response)
        return response_objects or None

    def wrap(key, data):
        return TraitNode(
            name=key,
            raw=data,
            root=root,
            query_params=query_params(),
            uri_params=uri_params(),
            form_params=form_params(),
            base_uri_params=base_uri_params(),
            headers=headers(data),
            body=body(data),
            responses=responses(),
            description=description(),
            media_type=media_type(),
            usage=usage(),
            protocols=protocols()
        )

    traits = raml_data.get("traits", [])
    trait_objects = []
    for trait in traits:
        name = list(iterkeys(trait))[0]
        data = list(itervalues(trait))[0]
        trait_objects.append(wrap(name, data))
    return trait_objects or None


def create_resource_types(raml_data, root):
    """
    Parse resourceTypes into ``ResourceType`` objects.

    :param dict raml_data: Raw RAML data
    :param RootNode root: Root Node
    :ret: list of ``ResourceType`` objects
    :rtype: list
    """
    # TODO: move this outside somewhere - config?
    accepted_methods = [
        "get", "get?",
        "post", "post?",
        "put", "put?",
        "delete", "delete?",
        "options", "options?",
        "head", "head?",
        "patch", "patch?",
        "trace", "trace?",
        "connect", "connect?"
    ]

    def get_union(resource, method, inherited):
        union = {}
        for key, value in list(iteritems(inherited)):
            if resource.get(method) is not None:
                if key not in list(iterkeys(resource.get(method, {}))):
                    union[key] = value
                else:
                    resource_values = resource.get(method, {}).get(key)
                    inherited_values = inherited.get(key, {})
                    union[key] = dict(list(iteritems(resource_values)) +
                                      list(iteritems(inherited_values)))
        if resource.get(method) is not None:
            for key, value in list(iteritems(resource.get(method, {}))):
                if key not in list(iterkeys(inherited)):
                    union[key] = value
        return union

    def get_inherited_resource(res_name):
        for resource in resource_types:
            if res_name == list(iterkeys(resource))[0]:
                return resource

    def get_inherited_type(root, resource, type, raml):
        inherited = get_inherited_resource(type)
        res_type_objs = []
        for key, value in list(iteritems(resource)):
            for i in list(iterkeys(value)):
                if i in accepted_methods:
                    data_union = get_union(
                        value, i, list(itervalues(inherited))[0].get(i, {})
                    )
                    # res = wrap(key, data_union, i)
                    res = ResourceTypeNode(
                        name=key,
                        raw=data_union,
                        root=root,
                        headers=headers(data_union.get('headers', {})),
                        body=body(data_union.get('body', {})),
                        responses=responses(data_union),
                        uri_params=uri_params(data_union),
                        base_uri_params=base_uri_params(data_union),
                        query_params=query_params(data_union),
                        form_params=form_params(data_union),
                        media_type=media_type(),
                        description=description(),
                        type=type_(),
                        method=method(i),
                        usage=usage(),
                        optional=optional(),
                        is_=is_(data_union),
                        traits=traits(data_union),
                        secured_by=secured_by(data_union),
                        security_schemes=security_schemes(data_union),
                        display_name=display_name(data_union, key),
                        protocols=protocols(data_union)
                    )
                    res_type_objs.append(res)
        return res_type_objs

    def display_name(data, name):
        return data.get('displayName', name)

    def headers(data):
        _headers = data.get("headers", {})
        if v.get("type"):
            inherited = get_inherited_resource(v.get("type"))
            inherited = inherited.get(v.get("type"))
            inherited_res_level = inherited.get(meth, {}).get("headers", {})
            _inherited = inherited.get(meth, {})
            inherited_meth_level_params = _inherited.get("headers", {})
            _headers = dict(list(iteritems(_headers)) +
                            list(iteritems(inherited_res_level)) +
                            list(iteritems(inherited_meth_level_params)))

        header_objs = _create_base_param_obj(_headers, Header)
        if header_objs:
            for h in header_objs:
                h.method = method(meth)

        return header_objs

    def body(data):
        _body = data.get("body", {})
        if v.get("type"):
            inherited = get_inherited_resource(v.get("type"))
            inherited = inherited.get(v.get("type"))
            inherited_res_level_params = inherited.get(meth, {})
            _inherited = inherited_res_level_params.get("body", {})
            inherited_meth_level_params = _inherited.get("body", {})
            _body = dict(list(iteritems(_body)) +
                         list(iteritems(_inherited)) +
                         list(iteritems(inherited_meth_level_params)))
        body_objects = []
        for key, value in list(iteritems(_body)):
            body = Body(
                mime_type=key,
                raw=value,
                schema=value.get("schema"),
                example=value.get("example"),
                form_params=value.get("formParameters")
            )
            body_objects.append(body)
        return body_objects or None

    def responses(data):
        response_objects = []
        for key, value in list(iteritems(data.get("responses", {}))):
            _headers = data.get("responses", {}).get(key, {})
            _headers = _headers.get("headers", {})
            header_objs = _create_base_param_obj(_headers, Header)
            if header_objs:
                for h in header_objs:
                    h.method = method(meth)
            response = Response(
                code=key,
                raw=value,
                description=value.get("description"),
                headers=header_objs,
                body=body(value)
            )
            response_objects.append(response)
        if response_objects:
            for r in response_objects:
                r.method = method(meth)

        return response_objects or None

    def uri_params(data):
        uri_params = dict(list(iteritems(data.get("uriParameters", {}))) +
                          list(iteritems(v.get("uriParameters", {}))))

        if v.get("type"):
            inherited = get_inherited_resource(v.get("type"))
            inherited_params = inherited.get(v.get("type"))
            inherited_params = inherited_params.get("uriParameters", {})
            uri_params = dict(list(iteritems(uri_params)) +
                              list(iteritems(inherited_params)))
        return _create_base_param_obj(uri_params, URIParameter)

    def base_uri_params(data):
        resource_level = data.get("baseUriParameters", {})
        method_level = data.get("baseUriParameters", {})
        uri_params = dict(list(iteritems(resource_level)) +
                          list(iteritems(method_level)))

        return _create_base_param_obj(uri_params, URIParameter)

    def query_params(data):
        query_params = data.get("queryParameters", {})

        if v.get("type"):
            inherited = get_inherited_resource(v.get("type"))
            inherited_params = list(itervalues(inherited))[0]
            inherited_params = inherited_params.get("queryParameters", {})
            query_params = dict(list(iteritems(query_params)) +
                                list(iteritems(inherited_params)))

        return _create_base_param_obj(query_params, QueryParameter)

    def form_params(data):
        form_params = data.get("formParameters", {})

        if v.get("type"):
            inherited = get_inherited_resource(v.get("type"))
            inherited_params = list(itervalues(inherited))[0]
            inherited_params = inherited_params.get("formParameters", {})
            form_params = dict(list(iteritems(form_params)) +
                               list(iteritems(inherited_params)))

        return _create_base_param_obj(form_params, FormParameter)

    def media_type():
        return v.get('mediaType')

    def description():
        return v.get('description')

    def type_():
        return v.get('type')

    def method(meth):
        if "?" in meth:
            return meth[:-1]
        return meth

    def usage():
        return v.get('usage')

    def optional():
        return "?" in meth

    def protocols(data):
        if data.get("protocols"):
            return data.get("protocols")
        return v.get("protocols")

    def is_(data):
        resource_level = v.get("is", [])
        method_level = data.get("is", [])
        return resource_level + method_level or None

    def get_trait(item):
        traits = raml_data.get('traits', [])
        for t in traits:
            if item == list(iterkeys(t))[0]:
                return t

    def traits(data):
        assigned = is_(data)
        if assigned:
            trait_objs = []
            for item in assigned:
                assigned_trait = get_trait(item)
                raw_data = list(itervalues(assigned_trait))[0]
                trait = TraitNode(
                    name=list(iterkeys(assigned_trait))[0],
                    raw=raw_data,
                    root=root,
                    headers=headers(raw_data),
                    body=body(raw_data),
                    responses=responses(raw_data),
                    uri_params=uri_params(raw_data),
                    base_uri_params=base_uri_params(raw_data),
                    query_params=query_params(raw_data),
                    form_params=form_params(raw_data),
                    media_type=media_type(),
                    description=description(),
                    usage=usage(),
                    protocols=protocols(raw_data)
                )
                trait_objs.append(trait)
            return trait_objs
        return None

    def secured_by(data):
        resource_level = v.get('securedBy', [])
        method_level = data.get("securedBy", [])
        return resource_level + method_level or None

    def get_scheme(item):
        schemes = raml_data.get('securitySchemes', [])
        for s in schemes:
            if item == list(iterkeys(s))[0]:
                return s

    def security_schemes(data):
        secured = secured_by(data)
        if secured:
            secured_objs = []
            for item in secured:
                assigned_scheme = get_scheme(item)
                raw_data = list(itervalues(assigned_scheme))[0]
                scheme = SecurityScheme(
                    name=list(iterkeys(assigned_scheme))[0],
                    raw=raw_data,
                    type=raw_data.get('type'),
                    described_by=raw_data.get("describedBy"),
                    description=raw_data.get("description"),
                    settings=raw_data.get("settings")
                )
                secured_objs.append(scheme)
            return secured_objs
        return None

    def wrap(key, data, meth, v):
        resource_type = ResourceTypeNode(
            name=key,
            raw=data,
            root=root,
            headers=headers(data),
            body=body(data),
            responses=responses(data),
            uri_params=uri_params(data),
            base_uri_params=base_uri_params(data),
            query_params=query_params(data),
            form_params=form_params(data),
            media_type=media_type(),
            description=description(),
            type=type_(),
            method=method(meth),
            usage=usage(),
            optional=optional(),
            is_=is_(data),
            traits=traits(data),
            secured_by=secured_by(data),
            security_schemes=security_schemes(data),
            display_name=display_name(data, key),
            protocols=protocols(data)
        )
        return resource_type

    resource_types = raml_data.get("resourceTypes", [])
    resource_type_objects = []

    for res in resource_types:
        for k, v in list(iteritems(res)):
            if "type" in list(iterkeys(v)):
                r = get_inherited_type(root, res, v.get("type"), raml_data)
                resource_type_objects.extend(r)
            else:
                for meth in list(iterkeys(v)):
                    if meth in accepted_methods:
                        method_data = v.get(meth, {})
                        resource = wrap(k, method_data, meth, v)
                        resource_type_objects.append(resource)
    return resource_type_objects or None


def create_resources(node, resources, root, parent):
    """
    Recursively traverses the RAML file via DFS to find each resource
    endpoint.

    :param dict node: Dictionary of node to traverse
    :param list resources: List of collected ``ResourceNode``s
    :param RootNode root: The ``RootNode`` of the API
    :param ResourceNode parent: Parent ``ResourceNode`` of current ``node``
    :ret: List of ``ResourceNode`` objects.
    :rtype: list
    """
    for k, v in list(iteritems(node)):
        if k.startswith("/"):
            avail = config.get('defaults', 'available_methods')
            methods = [m for m in avail if m in list(iterkeys(v))]
            if methods:
                for m in methods:
                    child = create_node(name=k,
                                        raw_data=v,
                                        method=m,
                                        parent=parent,
                                        api=root)
                    resources.append(child)
            else:
                child = create_node(name=k,
                                    raw_data=v,
                                    method=None,
                                    parent=parent,
                                    api=root)
                resources.append(child)
            resources = create_resources(child.raw, resources, root, child)
    return resources


def create_node(name, raw_data, method, parent, api):
    """
    Create a Resource Node object.

    :param str name: Name of resource node
    :param dict raw_data: Raw RAML data associated with resource node
    :param str method: HTTP method associated with resource node
    :param ResourceNode parent: Parent node object of resource node, if any
    :param RootNode api: API ``RootNode`` that the resource node is attached to
    :ret: Resource Node object
    :rtype: ``ResourceNode``
    """
    #####
    # Helper functions
    #####
    def get_method(property):
        """Returns ``property`` defined at the method level, or ``None``."""
        if method is not None:
            get_item = raw_data.get(method, {})
            if get_item is not None:
                return get_item.get(property, {})
        return {}

    def get_resource(property):
        """Returns ``property`` defined at the resource level, or ``None``."""
        return raw_data.get(property, {})

    def get_resource_type(property):
        """Returns ``property`` defined in the resource type, or ``None``."""
        if type_():
            types = api.resource_types
            r_type = [r for r in types if r.name == type_()]
            if r_type:
                if hasattr(r_type[0], property):
                    if getattr(r_type[0], property) is not None:
                        return getattr(r_type[0], property)
        return []

    def get_trait(property):
        """Returns ``property`` defined in a trait, or ``None``."""

        if is_():
            traits = api.traits
            if traits:
                trait_objs = []
                for i in is_():
                    trait = [t for t in traits if t.name == i]
                    if trait:
                        if hasattr(trait[0], property):
                            if getattr(trait[0], property) is not None:
                                trait_objs.extend(getattr(trait[0], property))
                return trait_objs
        return []

    def get_property_levels(property):
        method_level = get_method(property)
        resource_level = get_resource(property)
        return OrderedDict(list(iteritems(method_level)) +
                           list(iteritems(resource_level)))

    def get_inherited_properties(property):
        type_objects = get_resource_type(property)
        trait_objects = get_trait(property)
        return type_objects + trait_objects

    #####
    # Node attribute functions
    #####
    def display_name():
        """Set resource's ``displayName``."""
        return raw_data.get('displayName', name)

    def path():
        """Set resource's relative URI path."""
        parent_path = ''
        if parent:
            parent_path = parent.path
        return parent_path + name

    def absolute_uri():
        """Set resource's absolute URI path."""
        return api.base_uri + path()

    def protocols():
        """Set resource's supported protocols."""
        trait_protocols = get_trait("protocols")
        r_type_protocols = get_resource_type('protocols')
        m_protocols = get_method('protocols')
        r_protocols = get_resource('protocols')
        if m_protocols:
            return m_protocols
        elif r_type_protocols:
            return r_type_protocols
        elif trait_protocols:
            return trait_protocols
        elif r_protocols:
            return r_protocols
        return [api.base_uri.split(":")[0].upper()]

    def headers():
        """Set resource's supported headers."""
        headers = get_property_levels("headers")
        header_objs = get_inherited_properties("headers")

        _headers = _create_base_param_obj(headers, Header)
        if _headers:
            header_objs.extend(_headers)

        return header_objs or None

    def body():
        """Set resource's supported request/response body."""
        bodies = get_property_levels("body")
        body_objects = get_inherited_properties("body")
        for k, v in list(iteritems(bodies)):
            if v is None:
                continue
            body = Body(
                mime_type=k,
                raw={k: v},
                schema=v.get('schema'),
                example=v.get('example'),
                form_params=v.get('formParameters')
            )
            body_objects.append(body)

        return body_objects or None

    def responses():
        """Set resource's expected responses."""
        def resp_headers(headers):
            """Set response headers."""
            header_objs = []
            for k, v in list(iteritems(headers)):
                header = Header(
                    name=k,
                    display_name=v.get('displayName', k),
                    method=method,
                    raw=headers,
                    type=v.get('type', 'string'),
                    description=v.get('description'),
                    example=v.get('example'),
                    default=v.get('default'),
                    minimum=v.get("minimum"),
                    maximum=v.get("maximum"),
                    min_length=v.get("minLength"),
                    max_length=v.get("maxLength"),
                    enum=v.get("enum"),
                    repeat=v.get("repeat", False),
                    pattern=v.get("pattern")
                )
                header_objs.append(header)
            return header_objs or None

        def resp_body(body):
            """Set response body."""
            body_objs = []

            for k, v in list(iteritems(body)):
                body = Body(
                    mime_type=k,
                    raw={k: v},
                    schema=v.get('schema'),
                    example=v.get('example'),
                    form_params=None
                )
                body_objs.append(body)
            return body_objs or None

        resps = get_property_levels("responses")
        type_resp = get_resource_type("responses")
        trait_resp = get_trait("responses")
        resp_objs = type_resp + trait_resp
        for k, v in list(iteritems(resps)):
            resp = Response(
                code=k,
                raw={k: v},
                method=method,
                description=v.get('description'),
                headers=resp_headers(v.get('headers', {})),
                body=resp_body(v.get('body', {}))
            )
            resp_objs.append(resp)

        return resp_objs or None

    def uri_params():
        """Set resource's URI parameters."""
        uri_params = get_property_levels("uriParameters")
        param_objs = get_inherited_properties("uri_params")

        params = _create_base_param_obj(uri_params, URIParameter)
        if params:
            param_objs.extend(params)
        return param_objs or None

    def base_uri_params():
        """Set resource's base URI parameters."""
        uri_params = get_property_levels("baseUriParameters")
        param_objs = get_inherited_properties("base_uri_params")

        params = _create_base_param_obj(uri_params, URIParameter)
        if params:
            param_objs.extend(params)
        return param_objs or None

    def query_params():
        """Set resource's query parameters."""
        query_params = get_property_levels("queryParameters")
        param_objs = get_inherited_properties("query_params")

        params = _create_base_param_obj(query_params, QueryParameter)
        if params:
            param_objs.extend(params)
        return param_objs or None

    def form_params():
        """Set resource's form parameters."""
        form_params = get_property_levels("formParameters")
        param_objs = get_inherited_properties("form_params")

        params = _create_base_param_obj(form_params, FormParameter)
        if params:
            param_objs.extend(params)
        return param_objs or None

    def media_type():
        """Set resource's supported media types."""
        return raw_data.get("mediaType")

    def description():
        """Set resource's description."""
        return raw_data.get("description")

    def is_():
        """Set resource's assigned trait names."""
        is_list = []
        res_level = raw_data.get("is")
        if res_level:
            assert isinstance(res_level, list), "Error parsing trait"
            is_list.extend(res_level)
        method_level = raw_data.get(method, {})
        if method_level:
            method_level = method_level.get("is")
            if method_level:
                assert isinstance(method_level, list), "Error parsing trait"
                is_list.extend(method_level)
        return is_list or None

    def traits():
        """Set resource's assigned trait objects."""
        assigned = is_()
        if assigned:
            if api.traits:
                trait_objs = []
                for trait in assigned:
                    obj = [t for t in api.traits if t.name == trait]
                    if obj:
                        trait_objs.append(obj[0])
                return trait_objs or None

    # TODO: wow this function sucks.
    def type_():
        """Set resource's assigned resource type name."""
        if method is not None:
            get_method = raw_data.get(method, {})
            if get_method:
                assigned_type = get_method.get("type")
                if assigned_type:
                    if isinstance(assigned_type, dict):
                        return list(iterkeys(assigned_type))[0]
                    else:
                        return assigned_type

        assigned_type = raw_data.get("type")
        if isinstance(assigned_type, dict):
            return list(iterkeys(assigned_type))[0]
        return assigned_type

    def resource_type():
        """Set resource's assigned resource type objects."""
        if type_():
            assigned_name = type_()
            res_types = api.resource_types
            type_obj = [r for r in res_types if r.name == assigned_name]
            if type_obj:
                return type_obj[0]

    def get_scheme(item):
        schemes = api.raw.get('securitySchemes', [])
        for s in schemes:
            if isinstance(item, str):
                if item == list(iterkeys(s))[0]:
                    return s
            elif isinstance(item, dict):
                if list(iterkeys(item))[0] == list(iterkeys(s))[0]:
                    return s

    def secured_by():
        """
        Set resource's assigned security scheme names and related paramters.
        """
        if method is not None:
            method_level = raw_data.get(method, {})
            if method_level:
                secured_by = method_level.get("securedBy")
                if secured_by:
                    return secured_by
        return raw_data.get("securedBy")

    def security_schemes():
        """Set resource's assigned security scheme objects."""
        secured = secured_by()
        if secured:
            secured_objs = []
            for item in secured:
                assigned_scheme = get_scheme(item)
                if assigned_scheme:
                    raw_data = list(itervalues(assigned_scheme))[0]
                    scheme = SecurityScheme(
                        name=list(iterkeys(assigned_scheme))[0],
                        raw=raw_data,
                        type=raw_data.get('type'),
                        described_by=raw_data.get("describedBy"),
                        description=raw_data.get("description"),
                        settings=raw_data.get("settings")
                    )
                    secured_objs.append(scheme)
            return secured_objs
        return None

    node = ResourceNode(
        name=name,
        raw=raw_data,
        method=method,
        parent=parent,
        root=api,
        display_name=display_name(),
        path=path(),
        absolute_uri=absolute_uri(),
        protocols=protocols(),
        headers=headers(),
        body=body(),
        responses=responses(),
        uri_params=uri_params(),
        base_uri_params=base_uri_params(),
        query_params=query_params(),
        form_params=form_params(),
        media_type=media_type(),
        description=description(),
        is_=is_(),
        traits=traits(),
        type=type_(),
        resource_type=resource_type(),
        secured_by=secured_by(),
        security_schemes=security_schemes()
    )

    return node
