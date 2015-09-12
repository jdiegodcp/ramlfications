# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function
import re

try:
    from collections import OrderedDict
except ImportError:  # NOCOV
    from ordereddict import OrderedDict

import attr
from six import iteritems, iterkeys, itervalues


from .parameters import (
    Documentation, Header, Body, Response, URIParameter, QueryParameter,
    FormParameter, SecurityScheme
)
from .raml import RootNode, ResourceNode, ResourceTypeNode, TraitNode
from .utils import load_schema, _resource_type_lookup
from .config import MEDIA_TYPES
from .errors import InvalidRAMLError

__all__ = ["parse_raml"]


def parse_raml(loaded_raml, config):
    """
    Parse loaded RAML file into RAML/Python objects.

    :param RAMLDict loaded_raml: OrderedDict of loaded RAML file
    :returns: :py:class:`.raml.RootNode` object.
    :raises: :py:class:`.errors.InvalidRAMLError` when RAML file is invalid
    """

    validate = str(config.get("validate")).lower() == 'true'

    # Postpone validating the root node until the end; otherwise,
    # we end up with duplicate validation exceptions.
    attr.set_run_validators(False)
    root = create_root(loaded_raml, config)
    attr.set_run_validators(validate)

    root.security_schemes = create_sec_schemes(root.raml_obj, root)
    root.traits = create_traits(root.raml_obj, root)
    root.resource_types = create_resource_types(root.raml_obj, root)
    root.resources = create_resources(root.raml_obj, [], root,
                                      parent=None)

    if validate:
        attr.validate(root)  # need to validate again for root node

        if root.errors:
            raise InvalidRAMLError(root.errors)

    return root


def _get(data, item, default=None):
    """
    Helper function to catch empty mappings in RAML. If item is optional
    but not in the data, or data is ``None``, the default value is returned.

    :param data: RAML data
    :param str item: RAML key
    :param default: default value if item is not in dict
    :param bool optional: If RAML item is optional or needs to be defined
    :ret: value for RAML key
    """
    try:
        return data.get(item, default)
    except AttributeError:
        return default


def _create_base_param_obj(attribute_data, param_obj, config, errors, **kw):
    """Helper function to create a BaseParameter object"""
    objects = []

    for key, value in list(iteritems(attribute_data)):
        if param_obj is URIParameter:
            required = _get(value, "required", default=True)
        else:
            required = _get(value, "required", default=False)
        kwargs = dict(
            name=key,
            raw={key: value},
            desc=_get(value, "description"),
            display_name=_get(value, "displayName", key),
            min_length=_get(value, "minLength"),
            max_length=_get(value, "maxLength"),
            minimum=_get(value, "minimum"),
            maximum=_get(value, "maximum"),
            default=_get(value, "default"),
            enum=_get(value, "enum"),
            example=_get(value, "example"),
            required=required,
            repeat=_get(value, "repeat", False),
            pattern=_get(value, "pattern"),
            type=_get(value, "type", "string"),
            config=config,
            errors=errors
        )
        if param_obj is Header:
            kwargs["method"] = _get(kw, "method")

        item = param_obj(**kwargs)
        objects.append(item)

    return objects or None


def create_root(raml, config):
    """
    Creates a Root Node based off of the RAML's root section.

    :param RAMLDict raml: loaded RAML file
    :returns: :py:class:`.raml.RootNode` object with API root attributes set
    """

    errors = []

    def title():
        return raml.get("title")

    def version():
        return raml.get("version")

    def protocols():
        explicit_protos = raml.get("protocols")
        implicit_protos = re.findall(r"(https|http)", base_uri())
        implicit_protos = [p.upper() for p in implicit_protos]

        return explicit_protos or implicit_protos or None

    def base_uri():
        base_uri = raml.get("baseUri", "")
        if "{version}" in base_uri:
            base_uri = base_uri.replace("{version}", str(raml.get("version")))
        return base_uri

    def base_uri_params():
        data = raml.get("baseUriParameters", {})
        return _create_base_param_obj(data, URIParameter, config, errors)

    def uri_params():
        data = raml.get("uriParameters", {})
        return _create_base_param_obj(data, URIParameter, config, errors)

    def media_type():
        return raml.get("mediaType")

    def docs():
        d = raml.get("documentation", [])
        assert isinstance(d, list), "Error parsing documentation"
        docs = [Documentation(i.get("title"), i.get("content")) for i in d]
        return docs or None

    def schemas():
        _schemas = raml.get("schemas")
        if not _schemas:
            return None
        schemas = []
        for schema in _schemas:
            value = load_schema(list(itervalues(schema))[0])
            schemas.append({list(iterkeys(schema))[0]: value})
        return schemas or None

    def secured_by():
        return raml.get("securedBy")

    return RootNode(
        raml_obj=raml,
        raw=raml,
        title=title(),
        version=version(),
        protocols=protocols(),
        base_uri=base_uri(),
        base_uri_params=base_uri_params(),
        uri_params=uri_params(),
        media_type=media_type(),
        documentation=docs(),
        schemas=schemas(),
        config=config,
        secured_by=secured_by(),
        errors=errors
    )


def create_sec_schemes(raml_data, root):
    """
    Parse security schemes into ``SecurityScheme`` objects

    :param dict raml_data: Raw RAML data
    :param RootNode root: Root Node
    :returns: list of :py:class:`.parameters.SecurityScheme` objects
    """
    def map_object_types(item):
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

    def type_():
        return data.get("type")

    def headers(header_data):
        _headers = []
        header_data = header_data.get("headers", {})
        for k, v in list(iteritems(header_data)):
            h = _create_base_param_obj({k: v}, Header, root.config,
                                       root.errors)
            _headers.extend(h)
        return _headers

    def body(body_data):
        body_data = body_data.get("body", {})
        _body = []
        for k, v in list(iteritems(body_data)):
            body = Body(
                mime_type=k,
                raw=v,
                schema=load_schema(v.get("schema")),
                example=load_schema(v.get("example")),
                form_params=v.get("formParameters"),
                config=root.config,
                errors=root.errors
            )
            _body.append(body)
        return _body

    def responses(resp_data):
        _resps = []
        resp_data = resp_data.get("responses", {})
        for k, v in list(iteritems(resp_data)):
            response = Response(
                code=k,
                raw=v,
                desc=v.get("description"),
                headers=headers(v.get("headers", {})),
                body=body(v.get("body", {})),
                config=root.config,
                errors=root.errors
            )
            _resps.append(response)
        return sorted(_resps, key=lambda x: x.code)

    def query_params(param_data):
        param_data = param_data.get("queryParameters", {})
        _params = []
        for k, v in list(iteritems(param_data)):
            p = _create_base_param_obj({k: v}, QueryParameter, root.config,
                                       root.errors)
            _params.extend(p)
        return _params

    def uri_params(param_data):
        param_data = param_data.get("uriParameters")
        _params = []
        for k, v in list(iteritems(param_data)):
            p = _create_base_param_obj({k: v}, URIParameter, root.config,
                                       root.errors)
            _params.extend(p)
        return _params

    def form_params(param_data):
        param_data = param_data.get("formParameters", {})
        _params = []
        for k, v in list(iteritems(param_data)):
            p = _create_base_param_obj({k: v}, FormParameter, root.config,
                                       root.errors)
            _params.extend(p)
        return _params

    def usage(desc_by_data):
        return desc_by_data.get("usage")

    def media_type(desc_by_data):
        return desc_by_data.get("mediaType")

    def protocols(desc_by_data):
        return desc_by_data.get("protocols")

    def documentation(desc_by_data):
        d = desc_by_data.get("documentation", [])
        assert isinstance(d, list), "Error parsing documentation"
        docs = [Documentation(i.get("title"), i.get("content")) for i in d]
        return docs or None

    def set_property(node, obj, node_data):
        func = map_object_types(obj)
        item_objs = func({obj: node_data})
        setattr(node, func.__name__, item_objs)

    def described_by():
        return data.get("describedBy", {})

    def description():
        return data.get("description")

    def settings():
        return data.get("settings")

    def initial_wrap(key, data):
        return SecurityScheme(
            name=key,
            raw=data,
            type=type_(),
            described_by=described_by(),
            desc=description(),
            settings=settings(),
            config=root.config,
            errors=root.errors
        )

    def final_wrap(node):
        for obj, node_data in list(iteritems(node.described_by)):
            set_property(node, obj, node_data)
        return node

    schemes = raml_data.get("securitySchemes", [])
    scheme_objs = []
    for s in schemes:
        name = list(iterkeys(s))[0]
        data = list(itervalues(s))[0]
        node = initial_wrap(name, data)
        node = final_wrap(node)
        scheme_objs.append(node)
    return scheme_objs or None


def create_traits(raml_data, root):
    """
    Parse traits into ``Trait`` objects.

    :param dict raml_data: Raw RAML data
    :param RootNode root: Root Node
    :returns: list of :py:class:`.raml.TraitNode` objects
    """
    def description():
        return _get(data, "description")

    def media_type():
        return _get(data, "mediaType")

    def usage():
        return _get(data, "usage")

    def protocols():
        return _get(data, "protocols")

    def query_params():
        params = _get(data, "queryParameters", {})
        return _create_base_param_obj(params, QueryParameter, root.config,
                                      root.errors)

    def uri_params():
        params = _get(data, "uriParameters", {})
        return _create_base_param_obj(params, URIParameter, root.config,
                                      root.errors)

    def form_params():
        params = _get(data, "formParameters", {})
        return _create_base_param_obj(params, FormParameter, root.config,
                                      root.errors)

    def base_uri_params():
        params = _get(data, "baseUriParameters", {})
        return _create_base_param_obj(params, URIParameter, root.config,
                                      root.errors)

    def headers(data):
        headers_ = _get(data, "headers", {})
        return _create_base_param_obj(headers_, Header, root.config,
                                      root.errors)

    def body(data):
        body = _get(data, "body", {})
        body_objects = []
        for key, value in list(iteritems(body)):
            body = Body(
                mime_type=key,
                raw=value,
                schema=load_schema(value.get("schema")),
                example=load_schema(value.get("example")),
                form_params=value.get("formParameters"),
                config=root.config,
                errors=root.errors
            )
            body_objects.append(body)
        return body_objects or None

    def responses():
        response_objects = []
        for key, value in list(iteritems(_get(data, "responses", {}))):
            response = Response(
                code=key,
                raw=value,
                desc=value.get("description"),
                headers=headers(value),
                body=body(value),
                config=root.config,
                errors=root.errors
            )
            response_objects.append(response)
        return sorted(response_objects, key=lambda x: x.code) or None

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
            desc=description(),
            media_type=media_type(),
            usage=usage(),
            protocols=protocols(),
            errors=root.errors
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
    Parse resourceTypes into ``ResourceTypeNode`` objects.

    :param dict raml_data: Raw RAML data
    :param RootNode root: Root Node
    :returns: list of :py:class:`.raml.ResourceTypeNode` objects
    """
    # TODO: move this outside somewhere - config?
    accepted_methods = root.config.get("http_optional")

    #####
    # Helper functions
    #####

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

    def get_inherited_type(root, resource, _type, raml):
        inherited = get_inherited_resource(_type)
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
                        headers=headers(data_union.get("headers", {})),
                        body=body(data_union.get("body", {})),
                        responses=responses(data_union),
                        uri_params=uri_params(data_union),
                        base_uri_params=base_uri_params(data_union),
                        query_params=query_params(data_union),
                        form_params=form_params(data_union),
                        media_type=media_type(),
                        desc=description(),
                        type=type_(),
                        method=method(i),
                        usage=usage(),
                        optional=optional(),
                        is_=is_(data_union),
                        traits=traits(data_union),
                        secured_by=secured_by(data_union),
                        security_schemes=security_schemes(data_union),
                        display_name=display_name(data_union, key),
                        protocols=protocols(data_union),
                        errors=root.errors
                    )
                    res_type_objs.append(res)
        return res_type_objs

    def get_scheme(item):
        schemes = raml_data.get("securitySchemes", [])
        for s in schemes:
            if item == list(iterkeys(s))[0]:
                return s

    def get_inherited_type_params(data, attribute, params):
        inherited = get_inherited_resource(data.get("type"))
        inherited = inherited.get(data.get("type"))
        inherited_params = inherited.get(attribute, {})

        return dict(list(iteritems(params)) +
                    list(iteritems(inherited_params)))

    def get_attribute(res_data, method_data, item, default={}):
        method_level = _get(method_data, item, default)
        resource_level = _get(res_data, item, default)
        return method_level, resource_level

    def get_inherited_item(items, item_name):
        inherited = get_inherited_resource(v.get("type"))
        resource = inherited.get(v.get("type"))
        res_level = resource.get(meth, {}).get(item_name, {})

        method = resource.get(meth, {})
        method_level = method.get(item_name, {})
        items = dict(
            list(iteritems(items)) +
            list(iteritems(res_level)) +
            list(iteritems(method_level))
        )
        return items

    def get_attribute_dict(data, item):
        resource_level = _get(v, item, {})
        method_level = _get(data, item, {})
        return dict(list(iteritems(resource_level)) +
                    list(iteritems(method_level)))

    #####
    # Set ResourceTypeNode attributes
    #####

    def display_name(data, name):
        return data.get("displayName", name)

    def headers(data):
        _headers = _get(data, "headers", {})
        if _get(v, "type"):
            _headers = get_inherited_item(_headers, "headers")

        header_objs = _create_base_param_obj(_headers, Header, root.config,
                                             root.errors)
        if header_objs:
            for h in header_objs:
                h.method = method(meth)

        return header_objs

    def body(data):
        _body = _get(data, "body", default={})
        if _get(v, "type"):
            _body = get_inherited_item(_body, "body")

        body_objects = []
        for key, value in list(iteritems(_body)):
            body = Body(
                mime_type=key,
                raw=value,
                schema=load_schema(value.get("schema")),
                example=load_schema(value.get("example")),
                form_params=value.get("formParameters"),
                config=root.config,
                errors=root.errors
            )
            body_objects.append(body)
        return body_objects or None

    def responses(data):
        response_objects = []
        _responses = _get(data, "responses", {})
        if _get(v, "type"):
            _responses = get_inherited_item(_responses, "responses")

        for key, value in list(iteritems(_responses)):
            _headers = data.get("responses", {}).get(key, {})
            _headers = _get(_headers, "headers", {})
            header_objs = _create_base_param_obj(_headers, Header,
                                                 root.config, root.errors)
            if header_objs:
                for h in header_objs:
                    h.method = method(meth)
            response = Response(
                code=key,
                raw={key: value},
                desc=_get(value, "description"),
                headers=header_objs,
                body=body(value),
                config=root.config,
                method=method(meth),
                errors=root.errors
            )
            response_objects.append(response)
        if response_objects:
            return sorted(response_objects, key=lambda x: x.code)
        return None

    def uri_params(data):
        uri_params = get_attribute_dict(data, "uriParameters")

        if _get(v, "type"):
            uri_params = get_inherited_type_params(v, "uriParameters",
                                                   uri_params)
        return _create_base_param_obj(uri_params, URIParameter, root.config,
                                      root.errors)

    def base_uri_params(data):
        uri_params = get_attribute_dict(data, "baseUriParameters")

        return _create_base_param_obj(uri_params, URIParameter, root.config,
                                      root.errors)

    def query_params(data):
        query_params = get_attribute_dict(data, "queryParameters")

        if _get(v, "type"):
            query_params = get_inherited_type_params(v, "queryParameters",
                                                     query_params)

        return _create_base_param_obj(query_params, QueryParameter,
                                      root.config, root.errors)

    def form_params(data):
        form_params = get_attribute_dict(data, "formParameters")

        if _get(v, "type"):
            form_params = get_inherited_type_params(v, "formParameters",
                                                    form_params)

        return _create_base_param_obj(form_params, FormParameter, root.config,
                                      root.errors)

    def media_type():
        return _get(v, "mediaType")

    def description():
        # prefer the resourceType method description
        if meth:
            method_attr = _get(v, meth)
            desc = _get(method_attr, "description")
            return desc or _get(v, "description")
        return _get(v, "description")

    def type_():
        return _get(v, "type")

    def method(meth):
        if not meth:
            return None
        if "?" in meth:
            return meth[:-1]
        return meth

    def usage():
        return _get(v, "usage")

    def optional():
        if meth:
            return "?" in meth

    def protocols(data):
        m, r = get_attribute(v, data, "protocols", None)
        if m:
            return m
        return r

    def is_(data):
        m, r = get_attribute(v, data, "is", default=[])
        return m + r or None

    def get_trait(item):
        traits = raml_data.get("traits", [])
        for t in traits:
            if item == list(iterkeys(t))[0]:
                return t

    # TODO: clean up
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
                    errors=root.errors,
                    headers=headers(raw_data),
                    body=body(raw_data),
                    responses=responses(raw_data),
                    uri_params=uri_params(raw_data),
                    base_uri_params=base_uri_params(raw_data),
                    query_params=query_params(raw_data),
                    form_params=form_params(raw_data),
                    media_type=media_type(),
                    desc=description(),
                    usage=usage(),
                    protocols=protocols(raw_data)
                )
                trait_objs.append(trait)
            return trait_objs
        return None

    def secured_by(data):
        m, r = get_attribute(v, data, "securedBy", [])
        return m + r or None

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
                    type=raw_data.get("type"),
                    described_by=raw_data.get("describedBy"),
                    desc=raw_data.get("description"),
                    settings=raw_data.get("settings"),
                    config=root.config,
                    errors=root.errors
                )
                secured_objs.append(scheme)
            return secured_objs
        return None

    def wrap(key, data, meth, v):
        return ResourceTypeNode(
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
            desc=description(),
            type=type_(),
            method=method(meth),
            usage=usage(),
            optional=optional(),
            is_=is_(data),
            traits=traits(data),
            secured_by=secured_by(data),
            security_schemes=security_schemes(data),
            display_name=display_name(data, key),
            protocols=protocols(data),
            errors=root.errors
        )

    resource_types = raml_data.get("resourceTypes", [])
    resource_type_objects = []

    for res in resource_types:
        for k, v in list(iteritems(res)):
            if isinstance(v, dict):
                if "type" in list(iterkeys(v)):
                    r = get_inherited_type(root, res, v.get("type"), raml_data)
                    resource_type_objects.extend(r)
                else:
                    for meth in list(iterkeys(v)):
                        if meth in accepted_methods:
                            method_data = v.get(meth, {})
                            resource = wrap(k, method_data, meth, v)
                            resource_type_objects.append(resource)
            else:
                meth = None
                resource = wrap(k, {}, meth, v)
                resource_type_objects.append(resource)
    return resource_type_objects or None


def create_resources(node, resources, root, parent):
    """
    Recursively traverses the RAML file via DFS to find each resource
    endpoint.

    :param dict node: Dictionary of node to traverse
    :param list resources: List of collected ``ResourceNode`` s
    :param RootNode root: The ``RootNode`` of the API
    :param ResourceNode parent: Parent ``ResourceNode`` of current ``node``
    :returns: List of :py:class:`.raml.ResourceNode` objects.
    """
    for k, v in list(iteritems(node)):
        if k.startswith("/"):
            avail = root.config.get("http_optional")
            methods = [m for m in avail if m in list(iterkeys(v))]
            if "type" in list(iterkeys(v)):
                assigned = _resource_type_lookup(v.get("type"), root)
                if hasattr(assigned, "method"):
                    if not assigned.optional:
                        methods.append(assigned.method)
                        methods = list(set(methods))
            if methods:
                for m in methods:
                    child = create_node(name=k,
                                        raw_data=v,
                                        method=m,
                                        parent=parent,
                                        root=root)
                    resources.append(child)
            # inherit resource type methods
            elif "type" in list(iterkeys(v)):
                if hasattr(assigned, "method"):
                    method = assigned.method
                else:
                    method = None
                child = create_node(name=k,
                                    raw_data=v,
                                    method=method,
                                    parent=parent,
                                    root=root)
                resources.append(child)
            else:
                child = create_node(name=k,
                                    raw_data=v,
                                    method=None,
                                    parent=parent,
                                    root=root)
                resources.append(child)
            resources = create_resources(child.raw, resources, root, child)
    return resources


def create_node(name, raw_data, method, parent, root):
    """
    Create a Resource Node object.

    :param str name: Name of resource node
    :param dict raw_data: Raw RAML data associated with resource node
    :param str method: HTTP method associated with resource node
    :param ResourceNode parent: Parent node object of resource node, if any
    :param RootNode api: API ``RootNode`` that the resource node is attached to
    :returns: :py:class:`.raml.ResourceNode` object
    """
    #####
    # Helper functions
    #####
    def get_method(attribute):
        """Returns ``attribute`` defined at the method level, or ``None``."""
        if method is not None:  # must explicitly say `not None`
            get_attribute = raw_data.get(method, {})
            if get_attribute is not None:
                return get_attribute.get(attribute, {})
        return {}

    def get_resource(attribute):
        """Returns ``attribute`` defined at the resource level, or ``None``."""
        return raw_data.get(attribute, {})

    def get_parent(attribute):
        if parent:
            return getattr(parent, attribute, {})
        return {}

    def get_resource_type(attribute):
        """Returns ``attribute`` defined in the resource type, or ``None``."""
        if type_() and root.resource_types:
            types = root.resource_types
            r_type = [r for r in types if r.name == type_()]
            r_type = [r for r in r_type if r.method == method]
            if r_type:
                if hasattr(r_type[0], attribute):
                    if getattr(r_type[0], attribute) is not None:
                        return getattr(r_type[0], attribute)
        return []

    def get_trait(attribute):
        """Returns ``attribute`` defined in a trait, or ``None``."""

        if is_():
            traits = root.traits
            if traits:
                trait_objs = []
                for i in is_():
                    trait = [t for t in traits if t.name == i]
                    if trait:
                        if hasattr(trait[0], attribute):
                            if getattr(trait[0], attribute) is not None:
                                trait_objs.extend(getattr(trait[0], attribute))
                return trait_objs
        return []

    def get_scheme(item):
        schemes = root.raw.get("securitySchemes", [])
        for s in schemes:
            if isinstance(item, str):
                if item == list(iterkeys(s))[0]:
                    return s
            elif isinstance(item, dict):
                if list(iterkeys(item))[0] == list(iterkeys(s))[0]:
                    return s

    def get_attribute_levels(attribute):
        method_level = get_method(attribute)
        resource_level = get_resource(attribute)
        return OrderedDict(list(iteritems(method_level)) +
                           list(iteritems(resource_level)))

    def get_inherited_attributes(attribute):
        type_objects = get_resource_type(attribute)
        trait_objects = get_trait(attribute)
        return type_objects + trait_objects

    # TODO: refactor - this ain't pretty
    def _remove_duplicates(inherit_params, resource_params):
        ret = []
        if isinstance(resource_params[0], Body):
            _params = [p.mime_type for p in resource_params]
        else:
            _params = [p.name for p in resource_params]

        for p in inherit_params:
            if isinstance(p, Body):
                if p.mime_type not in _params:
                    ret.append(p)
            else:
                if p.name not in _params:
                    ret.append(p)
        ret.extend(resource_params)
        return ret or None

    #####
    # Node attribute functions
    #####
    def display_name():
        """Set resource's ``displayName``."""
        return raw_data.get("displayName", name)

    def path():
        """Set resource's relative URI path."""
        parent_path = ""
        if parent:
            parent_path = parent.path
        return parent_path + name

    def absolute_uri():
        """Set resource's absolute URI path."""
        uri = root.base_uri + path()
        proto = protocols()
        if proto:
            uri = uri.split("://")
            if len(uri) == 2:
                uri = uri[1]
            if root.protocols:
                _proto = list(set(root.protocols) & set(proto))
                # if resource protocols and root protocols share a protocol
                # then use that one
                if _proto:
                    uri = _proto[0].lower() + "://" + uri
                # if no shared protocols, use the first of the resource
                # protocols
                else:
                    uri = proto[0].lower() + "://" + uri
        return uri

    def protocols():
        """Set resource's supported protocols."""
        trait_protocols = get_trait("protocols")
        r_type_protocols = get_resource_type("protocols")
        m_protocols = get_method("protocols")
        r_protocols = get_resource("protocols")
        parent = get_parent("protocols")
        if m_protocols:
            return m_protocols
        elif r_type_protocols:
            return r_type_protocols
        elif trait_protocols:
            return trait_protocols
        elif r_protocols:
            return r_protocols
        elif parent:
            return parent
        return [root.base_uri.split(":")[0].upper()]

    def headers():
        """Set resource's supported headers."""
        headers = get_attribute_levels("headers")
        header_objs = get_inherited_attributes("headers")

        _headers = _create_base_param_obj(headers, Header, root.config,
                                          root.errors, method=method)
        if _headers is None:
            return header_objs or None
        return _remove_duplicates(header_objs, _headers)

    def body():
        """Set resource's supported request/response body."""
        bodies = get_attribute_levels("body")
        body_objects = get_inherited_attributes("body")

        _body_objs = []
        for k, v in list(iteritems(bodies)):
            if v is None:
                continue
            body = Body(
                mime_type=k,
                raw={k: v},
                schema=load_schema(v.get("schema")),
                example=load_schema(v.get("example")),
                form_params=v.get("formParameters"),
                config=root.config,
                errors=root.errors
            )
            _body_objs.append(body)
        if _body_objs == []:
            return body_objects or None
        return _remove_duplicates(body_objects, _body_objs)

    def responses():
        """Set resource's expected responses."""
        def resp_headers(headers):
            """Set response headers."""
            header_objs = []
            for k, v in list(iteritems(headers)):
                header = Header(
                    name=k,
                    display_name=_get(v, "displayName", default=k),
                    method=method,
                    raw=headers,
                    type=_get(v, "type", default="string"),
                    desc=_get(v, "description"),
                    example=_get(v, "example"),
                    default=_get(v, "default"),
                    minimum=_get(v, "minimum"),
                    maximum=_get(v, "maximum"),
                    min_length=_get(v, "minLength"),
                    max_length=_get(v, "maxLength"),
                    enum=_get(v, "enum"),
                    repeat=_get(v, "repeat", default=False),
                    pattern=_get(v, "pattern"),
                    config=root.config,
                    errors=root.errors
                )
                header_objs.append(header)
            return header_objs or None

        def resp_body(body):
            """Set response body."""
            body_list = []
            default_body = {}
            for (key, spec) in body.items():
                if key not in MEDIA_TYPES:
                    # if a root mediaType was defined, the response body
                    # may omit the mime_type definition
                    if key == 'schema':
                        schema = load_schema(spec) if spec else {}
                        default_body['schema'] = schema
                    if key == 'example':
                        example = load_schema(spec) if spec else {}
                        default_body['example'] = example
                else:
                    mime_type = key
                    if spec is None:
                        # spec might be '!!null'
                        body_list.append(Body(
                            mime_type=mime_type,
                            raw=body,
                            schema={},
                            example={},
                            form_params=None,
                            config=root.config,
                            errors=root.errors
                        ))
                    else:
                        schema = spec.get('schema', '')
                        example = spec.get('example', '')
                        body_list.append(Body(
                            mime_type=mime_type,
                            raw=spec,
                            schema=load_schema(schema) if schema else {},
                            example=load_schema(example) if example else {},
                            form_params=None,
                            config=root.config,
                            errors=root.errors
                        ))
            if default_body:
                body_list.append(Body(
                    mime_type=root.media_type,
                    raw=body,
                    schema=default_body['schema'],
                    example=default_body['example'],
                    form_params=None,
                    config=root.config,
                    errors=root.errors
                ))

            return body_list or None

        resps = get_attribute_levels("responses")
        type_resp = get_resource_type("responses")
        trait_resp = get_trait("responses")
        resp_objs = type_resp + trait_resp
        resp_codes = [r.code for r in resp_objs]
        for k, v in list(iteritems(resps)):
            if k in resp_codes:
                resp = [r for r in resp_objs if r.code == k][0]
                index = resp_objs.index(resp)
                inherit_resp = resp_objs.pop(index)
                headers = resp_headers(_get(v, "headers", default={}))
                if inherit_resp.headers:
                    headers = _remove_duplicates(inherit_resp.headers, headers)
                    # if headers:
                    #     headers.extend(inherit_resp.headers)
                    # else:
                    #     headers = inherit_resp.headers
                body = resp_body(v.get("body", {}))
                if inherit_resp.body:
                    body = _remove_duplicates(inherit_resp.body, body)
                    # if body:
                    #     body.extend(inherit_resp.body)
                    # else:
                    #     body = inherit_resp.body
                resp = Response(
                    code=k,
                    raw={k: v},  # should prob get data union
                    method=method,
                    desc=v.get("description") or inherit_resp.desc,
                    headers=headers,
                    body=body,
                    config=root.config,
                    errors=root.errors
                )
                resp_objs.insert(index, resp)  # preserve order
            else:
                _headers = _get(v, "headers", default={})
                _body = _get(v, "body", default={})
                resp = Response(
                    code=k,
                    raw={k: v},
                    method=method,
                    desc=_get(v, "description"),
                    headers=resp_headers(_headers),
                    body=resp_body(_body),
                    config=root.config,
                    errors=root.errors
                )
                resp_objs.append(resp)

        return resp_objs or None

    def uri_params():
        """Set resource's URI parameters."""
        uri_params = get_attribute_levels("uriParameters")
        param_objs = get_inherited_attributes("uri_params")

        params = _create_base_param_obj(uri_params, URIParameter, root.config,
                                        root.errors)
        if params:
            param_objs.extend(params)
        if parent and parent.uri_params:
            param_objs.extend(parent.uri_params)
        if root.uri_params:
            root_params = root.uri_params
            param_names = [p.name for p in param_objs]
            _params = [p for p in root_params if p.name not in param_names]
            param_objs.extend(_params)

        return param_objs or None

    def base_uri_params():
        """Set resource's base URI parameters."""
        uri_params = get_attribute_levels("baseUriParameters")
        param_objs = get_inherited_attributes("base_uri_params")

        params = _create_base_param_obj(uri_params, URIParameter, root.config,
                                        root.errors)
        if params:
            param_objs.extend(params)

        # if parent and parent.base_uri_params:
            # param_objs.extend(parent.base_uri_params)

        if root.base_uri_params:
            root_params = root.base_uri_params
            param_names = [p.name for p in param_objs]
            _params = [p for p in root_params if p.name not in param_names]
            param_objs.extend(_params)
        return param_objs or None

    def query_params():
        """Set resource's query parameters."""
        query_params = get_attribute_levels("queryParameters")
        param_objs = get_inherited_attributes("query_params")

        params = _create_base_param_obj(query_params, QueryParameter,
                                        root.config, root.errors)

        if params is None:
            return param_objs or None
        return _remove_duplicates(param_objs, params)

    def form_params():
        """Set resource's form parameters."""
        form_params = get_attribute_levels("formParameters")
        param_objs = get_inherited_attributes("form_params")

        params = _create_base_param_obj(form_params, FormParameter,
                                        root.config, root.errors)
        if params is None:
            return param_objs or None
        return _remove_duplicates(param_objs, params)

    def media_type():
        """Set resource's supported media types."""
        if raw_data.get(method, {}):
            if raw_data.get(method, {}).get("mediaType"):
                return raw_data.get(method, {}).get("mediaType")
        if get_trait("media_type"):
            return "".join(get_trait("media_type"))
        if get_resource_type("media_type"):
            return get_resource_type("media_type")
        if raw_data.get("mediaType"):
            return raw_data.get("mediaType")
        if root.media_type:
            return root.media_type

    def description():
        """Set resource's description."""
        desc = raw_data.get("description")
        try:
            desc = raw_data.get(method).get("description")
            if desc is None:
                raise AttributeError
        except AttributeError:
            if type_():
                assigned = _resource_type_lookup(type_(), root)
                try:
                    if assigned.method == method:
                        desc = assigned.description.raw
                except AttributeError:
                    pass
            else:
                desc = raw_data.get("description")
        return desc

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
            if root.traits:
                trait_objs = []
                for trait in assigned:
                    obj = [t for t in root.traits if t.name == trait]
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
                        return list(iterkeys(assigned_type))[0]  # NOCOV
                    else:
                        return assigned_type

        assigned_type = raw_data.get("type")
        if isinstance(assigned_type, dict):
            return list(iterkeys(assigned_type))[0]  # NOCOV
        return assigned_type

    def resource_type():
        """Set resource's assigned resource type objects."""
        if type_() and root.resource_types:
            assigned_name = type_()
            res_types = root.resource_types
            type_obj = [r for r in res_types if r.name == assigned_name]
            if type_obj:
                return type_obj[0]

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
        resource_level = raw_data.get("securedBy")
        if resource_level:
            return resource_level
        root_level = root.secured_by
        if root_level:
            return root_level

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
                        type=raw_data.get("type"),
                        described_by=raw_data.get("describedBy"),
                        desc=raw_data.get("description"),
                        settings=raw_data.get("settings"),
                        config=root.config,
                        errors=root.errors
                    )
                    secured_objs.append(scheme)
            return secured_objs
        return None

    node = ResourceNode(
        name=name,
        raw=raw_data,
        method=method,
        parent=parent,
        root=root,
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
        desc=description(),
        is_=is_(),
        traits=traits(),
        type=type_(),
        resource_type=resource_type(),
        secured_by=secured_by(),
        security_schemes=security_schemes(),
        errors=root.errors
    )
    if resource_type():
        # correct inheritance (issue #23)
        node._inherit_type()
    return node
