# ! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function

import re

import attr
from six import iteritems, iterkeys


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


def create_root(loaded_raml_file):
    def base_uri():
        base_uri = raml.get('baseUri', "")
        if "{version}" in base_uri:
            base_uri = base_uri.replace('{version}', str(raml.get('version')))
        return base_uri

    def protocols():
        explicit_protos = raml.get('protocols')
        implicit_protos = re.findall(r"(https|http)", base_uri())

        return explicit_protos or implicit_protos or None

    def docs():
        d = raml.get('documentation', [])
        assert isinstance(d, list), "Error parsing documentation"
        docs = [Documentation(i.get('title'), i.get('content')) for i in d]
        return docs or None

    def base_uri_params():
        base_uri_params = raml.get('baseUriParameters', {})
        uri_params = []
        for k, v in list(base_uri_params.items()):
            uri_params.append(
                URIParameter(
                    name=k,
                    raw=v,
                    description=v.get('description'),
                    default=v.get('default'),
                    display_name=v.get('displayName', k),
                    min_length=v.get("minLength"),
                    max_length=v.get("maxLength"),
                    minimum=v.get("minimum"),
                    maximum=v.get("maximum"),
                    example=v.get("example"),
                    repeat=v.get("repeat", False),
                    pattern=v.get("pattern"),
                    param_type=v.get("type", "string")
                )
            )
        return uri_params or None

    def uri_params():
        uri_params = raml.get('uriParameters', {})
        params = []
        for k, v in list(uri_params.items()):
            params.append(
                URIParameter(
                    name=k,
                    raw=v,
                    description=v.get('description'),
                    default=v.get('default'),
                    display_name=v.get('displayName', k),
                    min_length=v.get('minLength'),
                    max_length=v.get("maxLength"),
                    minimum=v.get("minimum"),
                    maximum=v.get("maximum"),
                    example=v.get("example"),
                    param_type=v.get("type", "string")
                )
            )
        return params or None

    def title():
        return raml.get('title')

    def version():
        return raml.get('version')

    def schemas():
        return raml.get('schemas')

    def media_type():
        return raml.get('mediaType')

    raml = loaded_raml_file.data
    root = RootNode(
        raml_obj=loaded_raml_file,
        raw=raml,
        version=version(),
        base_uri=base_uri(),
        base_uri_params=base_uri_params(),
        uri_params=uri_params(),
        protocols=protocols(),
        title=title(),
        docs=docs(),
        schemas=schemas(),
        media_type=media_type(),
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
    def query_params():
        query_params = data.get("queryParameters", {})
        param_objs = []
        for key, value in iteritems(query_params):
            param = QueryParameter(
                name=key,
                raw=value,
                description=value.get("description"),
                display_name=value.get("displayName", name),
                min_length=value.get('minLength'),
                max_length=value.get("maxLength"),
                minimum=value.get("minimum"),
                maximum=value.get("maximum"),
                default=value.get("default"),
                enum=value.get("enum"),
                example=value.get("example"),
                required=value.get("required", False),
                repeat=value.get("repeat", False),
                pattern=value.get("pattern"),
                param_type=value.get("type", "string")
            )
            param_objs.append(param)
        return param_objs or None

    def uri_params():
        uri_params = data.get('uriParameters', {})
        param_objs = []
        for key, value in iteritems(uri_params):
            param = URIParameter(
                name=key,
                raw=value,
                description=value.get('description'),
                display_name=value.get('displayName', name),
                min_length=value.get('minLength'),
                max_length=value.get("maxLength"),
                minimum=value.get("minimum"),
                maximum=value.get("maximum"),
                param_type=value.get('type', 'string'),
                default=value.get("default"),
                enum=value.get("enum"),
                example=value.get("example"),
                repeat=value.get("repeat", False),
                pattern=value.get("pattern")
            )
            param_objs.append(param)
        return param_objs or None

    def form_params():
        form_params = data.get("formParameters", {})
        param_objs = []
        for key, value in iteritems(form_params):
            param = FormParameter(
                name=key,
                raw=value,
                description=value.get("description"),
                display_name=value.get("displayName", name),
                min_length=value.get('minLength'),
                max_length=value.get("maxLength"),
                minimum=value.get("minimum"),
                maximum=value.get("maximum"),
                default=value.get('default'),
                enum=value.get("enum"),
                example=value.get("example"),
                required=value.get("required", False),
                repeat=value.get("repeat", False),
                pattern=value.get("pattern"),
                param_type=value.get("type", "string")
            )
            param_objs.append(param)
        return param_objs or None

    def base_uri_params():
        params = data.get('baseUriParameters', {})
        param_objs = []
        for key, value in iteritems(params):
            param = URIParameter(
                name=key,
                raw=value,
                description=value.get("description"),
                display_name=value.get("displayName", name),
                min_length=value.get("minLength"),
                max_length=value.get("maxLength"),
                minimum=value.get("minimum"),
                maximum=value.get("maximum"),
                param_type=value.get("type", "string"),
                default=value.get("default"),
                enum=value.get("enum"),
                example=value.get("example"),
                repeat=value.get("repeat", False),
                pattern=value.get("pattern")
            )
            param_objs.append(param)
        return param_objs

    def headers(headers):
        header_objs = []
        for key, value in iteritems(headers):
            header = Header(
                name=key,
                display_name=value.get('displayName', key),
                raw=value,
                param_type=value.get('type', 'string'),
                description=value.get('description'),
                example=value.get('example'),
                default=value.get('default'),
                required=value.get('required', False),
                min_length=value.get("minLength"),
                max_length=value.get("maxLength"),
                minimum=value.get("minimum"),
                maximum=value.get("maximum"),
                repeat=value.get("repeat", False),
                pattern=value.get("pattern")
            )
            header_objs.append(header)
        return header_objs or None

    def body(body):
        body_objs = []
        for key, value in iteritems(body):
            body = Body(
                mime_type=key,
                raw=value,
                schema=value.get("schema"),
                example=value.get("example"),
                form_params=value.get("formParameters")
            )
            body_objs.append(body)
        return body_objs or None

    def responses():
        resp_objs = []
        for key, value in iteritems(data.get('responses', {})):
            response = Response(
                code=key,
                raw=value,
                description=value.get("description"),
                headers=headers(value.get('headers', {})),
                body=body(value.get('body', {}))
            )
            resp_objs.append(response)
        return resp_objs or None

    def description():
        return data.get("description")

    def media_type():
        return data.get("mediaType")

    def usage():
        return data.get('usage')

    def protocols():
        return data.get("protocols")

    def wrap(key, raw_data):
        return TraitNode(
            name=key,
            raw=raw_data,
            root=root,
            query_params=query_params(),
            uri_params=uri_params(),
            form_params=form_params(),
            base_uri_params=base_uri_params(),
            headers=headers(data.get("headers", {})),
            body=body(data.get("body", {})),
            responses=responses(),
            description=description(),
            media_type=media_type(),
            usage=usage(),
            protocols=protocols())

    traits = raml_data.get('traits', [])
    trait_objs = []
    for trait in traits:
        name = trait.keys()[0]
        data = trait.values()[0]
        trait_objs.append(wrap(name, data))
    return trait_objs or None


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
        for key, value in iteritems(inherited):
            if resource.get(method) is not None:
                if key not in resource.get(method, {}).keys():
                    union[key] = value
                else:
                    resource_values = resource.get(method, {}).get(key)
                    inherited_values = inherited.get(key, {})
                    union[key] = dict(resource_values.items() +
                                      inherited_values.items())
        if resource.get(method) is not None:
            for key, value in iteritems(resource.get(method, {})):
                if key not in inherited.keys():
                    union[key] = value
        return union

    def get_inherited_resource(res_name):
        for resource in res_types:
            if res_name == resource.keys()[0]:
                return resource

    def get_inherited_type(root, resource, type, raml):
        inherited = get_inherited_resource(type)
        res_type_objs = []
        for key, value in iteritems(resource):
            for i in iterkeys(value):
                if i in accepted_methods:
                    data_union = get_union(value, i,
                                           inherited.values()[0].get(i, {}))
                    # res = wrap(key, data_union, i)
                    res = ResourceTypeNode(
                        name=key,
                        raw=data_union,
                        root=root,
                        headers=headers(data_union.get('headers', {})),
                        body=body(data_union.get('body', {})),
                        responses=responses(data_union),
                        uri_params=uri_params(),
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

    def headers(items):
        header_objs = []
        for key, value in iteritems(items):
            header = Header(
                name=key,
                display_name=value.get('displayName', key),
                method=method(i),
                raw=value,
                param_type=value.get('type', 'string'),
                description=value.get('description'),
                example=value.get('example'),
                default=value.get('default'),
                required=value.get('required', False),
                min_length=value.get("minLength"),
                max_length=value.get("maxLength"),
                minimum=value.get("minimum"),
                maximum=value.get("maximum"),
                repeat=value.get("repeat", False),
                pattern=value.get("pattern")
            )
            header_objs.append(header)
        return header_objs or None

    def body(items):
        body_objs = []
        for key, value in iteritems(items):
            body = Body(
                mime_type=key,
                raw=value,
                schema=value.get("schema"),
                example=value.get("example"),
                form_params=value.get("formParameters")
            )
            body_objs.append(body)
        return body_objs or None

    def responses(resp_data):
        responses = resp_data.get('responses', {})
        resp_objs = []
        for key, value in iteritems(responses):
            response = Response(
                code=key,
                raw=value,
                method=method(i),
                description=value.get("description"),
                headers=headers(value.get('headers', {})),
                body=body(value.get('body', {}))
            )
            resp_objs.append(response)
        return resp_objs or None

    def uri_params():
        uri_params = v.get('uriParameters', {})
        if v.get("type"):
            inherited = get_inherited_resource(v.get("type"))
            inherited_params = inherited.values()[0].get("uriParameters", {})
            uri_params = dict(uri_params.items() + inherited_params.items())
        param_objs = []
        for key, value in iteritems(uri_params):
            param = URIParameter(
                name=key,
                raw=value,
                description=value.get('description'),
                display_name=value.get('displayName', k),
                min_length=value.get('minLength'),
                max_length=value.get("maxLength"),
                minimum=value.get("minimum"),
                maximum=value.get("maximum"),
                param_type=value.get('type', 'string'),
                default=value.get("default"),
                enum=value.get("enum"),
                example=value.get("example"),
                repeat=value.get("repeat", False),
                pattern=value.get("pattern")
            )
            param_objs.append(param)
        return param_objs or None

    def base_uri_params(data):
        res_level = v.get('baseUriParameters', {})
        method_level = data.get("baseUriParameters", {})
        uri_params = dict(res_level.items() + method_level.items())
        param_objs = []
        for key, value in iteritems(uri_params):
            param = URIParameter(
                name=key,
                raw=value,
                description=value.get("description"),
                display_name=value.get("displayName", k),
                min_length=value.get("minLength"),
                max_length=value.get("maxLength"),
                minimum=value.get("minimum"),
                maximum=value.get("maximum"),
                param_type=value.get("type", "string"),
                default=value.get("default"),
                enum=value.get("enum"),
                example=value.get("example"),
                repeat=value.get("repeat", False),
                pattern=value.get("pattern")
            )
            param_objs.append(param)
        return param_objs or None

    def query_params(item):
        query_params = item.get("queryParameters", {})
        if v.get("type"):
            inherited = get_inherited_resource(v.get("type"))
            inherited_params = inherited.values()[0].get("queryParameters", {})
            query_params = dict(query_params.items() +
                                inherited_params.items())
        param_objs = []
        for key, value in iteritems(query_params):
            param = QueryParameter(
                name=key,
                raw=value,
                description=value.get("description"),
                display_name=value.get("displayName", k),
                min_length=value.get('minLength'),
                max_length=value.get("maxLength"),
                minimum=value.get("minimum"),
                maximum=value.get("maximum"),
                default=value.get("default"),
                enum=value.get("enum"),
                example=value.get("example"),
                required=value.get("required", False),
                repeat=value.get("repeat", False),
                pattern=value.get("pattern"),
                param_type=value.get("type", "string")

            )
            param_objs.append(param)
        return param_objs or None

    def form_params(data):
        form_params = data.get("formParameters", {})
        if v.get("type"):
            inherited = get_inherited_resource(v.get("type"))
            inherited_params = inherited.values()[0].get("formParameters", {})
            form_params = dict(form_params.items() + inherited_params.items())
        param_objs = []
        for key, value in iteritems(form_params):
            param = FormParameter(
                name=key,
                raw=value,
                description=value.get("description"),
                display_name=value.get("displayName", k),
                min_length=value.get('minLength'),
                max_length=value.get("maxLength"),
                minimum=value.get("minimum"),
                maximum=value.get("maximum"),
                default=value.get('default'),
                enum=value.get("enum"),
                example=value.get("example"),
                required=value.get("required", False),
                repeat=value.get("repeat", False),
                pattern=value.get("pattern")
            )
            param_objs.append(param)
        return param_objs or None

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
        return "?" in i

    def protocols(data):
        method_level = data.get(method(i), {})
        if method_level:
            return method_level.get("protocols")
        return data.get("protocols")

    def is_(data):
        resource_level = v.get("is", [])
        method_level = data.get("is", [])
        return resource_level + method_level or None

    def get_trait(item):
        traits = raml_data.get('traits', [])
        for t in traits:
            if item == t.keys()[0]:
                return t

    def traits(data):
        assigned = is_(data)
        if assigned:
            trait_objs = []
            for item in assigned:
                assigned_trait = get_trait(item)
                raw_data = assigned_trait.values()[0]
                trait = TraitNode(
                    name=assigned_trait.keys()[0],
                    raw=raw_data,
                    root=root,
                    headers=headers(raw_data.get('headers', {})),
                    body=body(raw_data.get('body', {})),
                    responses=responses(raw_data),
                    uri_params=uri_params(),
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
            if item == s.keys()[0]:
                return s

    def security_schemes(data):
        secured = secured_by(data)
        if secured:
            secured_objs = []
            for item in secured:
                assigned_scheme = get_scheme(item)
                raw_data = assigned_scheme.values()[0]
                scheme = SecurityScheme(
                    name=assigned_scheme.keys()[0],
                    raw=raw_data,
                    type=raw_data.get('type'),
                    described_by=raw_data.get("describedBy"),
                    description=raw_data.get("description"),
                    settings=raw_data.get("settings")
                )
                secured_objs.append(scheme)
            return secured_objs
        return None

    def wrap(key, raw_data, i):
        r = ResourceTypeNode(
            name=key,
            raw=raw_data,
            root=root,
            headers=headers(raw_data.get('headers', {})),
            body=body(raw_data.get('body', {})),
            responses=responses(raw_data),
            uri_params=uri_params(),
            base_uri_params=base_uri_params(raw_data),
            query_params=query_params(raw_data),
            form_params=form_params(raw_data),
            media_type=media_type(),
            description=description(),
            type=type_(),
            method=method(i),
            usage=usage(),
            optional=optional(),
            is_=is_(raw_data),
            traits=traits(raw_data),
            secured_by=secured_by(raw_data),
            security_schemes=security_schemes(raw_data),
            display_name=display_name(raw_data, key),
            protocols=protocols(v)
        )
        return r

    res_types = raml_data.get('resourceTypes', [])
    res_type_objs = []

    for res in res_types:
        for k, v in iteritems(res):
            if 'type' in iterkeys(v):
                r = get_inherited_type(root, res,
                                       v.get('type'),
                                       raml_data)
                res_type_objs.extend(r)
            else:
                for i in iterkeys(v):
                    if i in accepted_methods:
                        data = v.get(i, {})
                        r = wrap(k, data, i)
                        res_type_objs.append(r)
    return res_type_objs or None


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
    for k, v in node.iteritems():
        if k.startswith("/"):
            avail = config.get('defaults', 'available_methods')
            methods = [m for m in avail if m in v.keys()]
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
        m_headers = get_method('headers')
        r_headers = get_resource('headers')
        type_headers = get_resource_type('headers')
        trait_headers = get_trait('headers')

        headers = dict(m_headers.items() +
                       r_headers.items())

        header_objs = type_headers + trait_headers

        for k, v in iteritems(headers):
            header = Header(
                name=k,
                display_name=v.get('displayName', k),
                method=method,
                raw={k: v},
                param_type=v.get('type', 'string'),
                description=v.get('description'),
                example=v.get('example'),
                default=v.get('default'),
                min_length=v.get("minLength"),
                max_length=v.get("maxLength"),
                minimum=v.get("minimum"),
                maximum=v.get("maximum"),
                enum=v.get("enum"),
                repeat=v.get("repeat", False),
                pattern=v.get("pattern")
            )
            header_objs.append(header)

        return header_objs or None

    def body():
        """Set resource's supported request/response body."""
        m_body = get_method('body')
        r_body = get_resource('body')
        type_body = get_resource_type('body')
        trait_body = get_trait('body')

        bodies = dict(m_body.items() + r_body.items())
        body_objs = type_body + trait_body
        for k, v in iteritems(bodies):
            if v is None:
                continue
            body = Body(
                mime_type=k,
                raw={k: v},
                schema=v.get('schema'),
                example=v.get('example'),
                form_params=v.get('formParameters')
            )
            body_objs.append(body)

        return body_objs or None

    def responses():
        """Set resource's expected responses."""
        def resp_headers(headers):
            """Set response headers."""
            header_objs = []
            for k, v in iteritems(headers):
                header = Header(
                    name=k,
                    display_name=v.get('displayName', k),
                    method=method,
                    raw=headers,
                    param_type=v.get('type', 'string'),
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

            for k, v in iteritems(body):
                body = Body(
                    mime_type=k,
                    raw={k: v},
                    schema=v.get('schema'),
                    example=v.get('example'),
                    form_params=None
                )
                body_objs.append(body)
            return body_objs or None

        m_resp = get_method('responses')
        r_resp = get_resource('responses')
        type_resp = get_resource_type('responses')
        trait_resp = get_trait('responses')

        resps = dict(m_resp.items() + r_resp.items())

        resp_objs = type_resp + trait_resp
        for k, v in iteritems(resps):
            resp = Response(
                code=k,
                raw={k: v},
                method=v.get('method'),
                description=v.get('description'),
                headers=resp_headers(v.get('headers', {})),
                body=resp_body(v.get('body', {}))
            )
            resp_objs.append(resp)

        return resp_objs or None

    def uri_params():
        """Set resource's URI parameters."""
        m_params = get_method("uriParameters")
        r_params = get_resource("uriParameters")
        type_params = get_resource_type("uri_params")
        trait_params = get_trait("uri_params")

        uri_params = dict(m_params.items() +
                          r_params.items())
        param_objs = trait_params + type_params
        for key, value in iteritems(uri_params):
            param = URIParameter(
                name=key,
                raw=value,
                description=value.get('description'),
                display_name=value.get('displayName', key),
                min_length=value.get('minLength'),
                max_length=value.get("maxLength"),
                minimum=value.get("minimum"),
                maximum=value.get("maximum"),
                param_type=value.get('type', 'string'),
                default=value.get("default"),
                enum=value.get("enum"),
                example=value.get("example")
            )
            param_objs.append(param)
        return param_objs or None

    def base_uri_params():
        """Set resource's base URI parameters."""
        m_params = get_method("baseUriParameters")
        r_params = get_resource("baseUriParameters")
        type_params = get_resource_type("base_uri_params")
        trait_params = get_trait("base_uri_params")

        uri_params = dict(m_params.items() +
                          r_params.items())
        param_objs = trait_params + type_params
        for key, value in iteritems(uri_params):
            param = URIParameter(
                name=key,
                raw=value,
                description=value.get('description'),
                display_name=value.get('displayName', key),
                min_length=value.get('minLength'),
                max_length=value.get("maxLength"),
                minimum=value.get("minimum"),
                maximum=value.get("maximum"),
                param_type=value.get('type', 'string'),
                default=value.get("default"),
                enum=value.get("enum"),
                example=value.get("example"),
                repeat=value.get("repeat", False),
                pattern=value.get("pattern"),
            )
            param_objs.append(param)
        return param_objs or None

    def query_params():
        """Set resource's query parameters."""
        m_params = get_method("queryParameters")
        r_params = get_resource("queryParameters")
        type_params = get_resource_type("query_params")
        trait_params = get_trait("query_params")

        query_params = dict(m_params.items() + r_params.items())
        param_objs = type_params + trait_params
        for key, value in iteritems(query_params):
            param = QueryParameter(
                name=key,
                raw=value,
                description=value.get("description"),
                display_name=value.get("displayName", key),
                min_length=value.get('minLength'),
                max_length=value.get("maxLength"),
                minimum=value.get("minimum"),
                maximum=value.get("maximum"),
                default=value.get("default"),
                enum=value.get("enum"),
                example=value.get("example"),
                required=value.get("required", False)
            )
            param_objs.append(param)
        return param_objs or None

    def form_params():
        """Set resource's form parameters."""
        m_params = get_method("formParameters")
        r_params = get_resource("formParameters")
        type_params = get_resource_type("form_params")
        trait_params = get_trait("form_params")

        form_params = dict(m_params.items() + r_params.items())
        param_objs = type_params + trait_params
        for key, value in iteritems(form_params):
            param = FormParameter(
                name=key,
                raw=value,
                description=value.get("description"),
                display_name=value.get("displayName", key),
                min_length=value.get('minLength'),
                max_length=value.get("maxLength"),
                minimum=value.get("minimum"),
                maximum=value.get("maximum"),
                default=value.get('default'),
                enum=value.get("enum"),
                example=value.get("example"),
                required=value.get("required", False),
                repeat=value.get("repeat", False),
                pattern=value.get("pattern"),
            )
            param_objs.append(param)
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

    def type_():
        """Set resource's assigned resource type names."""
        get_method = raw_data.get(method, {})
        if get_method:
            method_level = get_method.get("type")
            if method_level:
                return method_level
        return raw_data.get("type")

    def resource_type():
        """Set resource's assigned resource type objects."""
        assigned = type_()
        if assigned:
            type_obj = [r for r in api.resource_types if r.name == assigned]
            if type_obj:
                return type_obj[0]

    def secured_by():
        """
        Set resource's assigned security scheme names and related paramters.
        """
        return raw_data.get("securedBy")

    def security_schemes():
        """Set resource's assigned security scheme objects."""
        pass

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
