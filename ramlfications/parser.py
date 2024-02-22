# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function
import re

import attr
from six import iteritems, iterkeys, itervalues


from .config import MEDIA_TYPES
from .errors import InvalidRAMLError
from .parameters import (
    Documentation, Header, Body, Response, URIParameter, QueryParameter,
    FormParameter, SecurityScheme
)
from .parser_utils import (
    security_schemes
)
from .raml import RootNode, ResourceNode, ResourceTypeNode, TraitNode
from .utils import (
    load_schema, _resource_type_lookup,
    _get_resource_type, _get_trait, _get_attribute,
    _get_inherited_attribute, _remove_duplicates, _create_uri_params,
    _get, _create_base_param_obj, _get_res_type_attribute,
    _get_inherited_type_params, _get_inherited_item, _get_attribute_dict,
    get_inherited, set_param_object, set_params, _get_data_union,
    _preserve_uri_order
)


__all__ = ["parse_raml"]


def parse_raml(loaded_raml, config):
    """
    Parse loaded RAML file into RAML/Python objects.

    :param RAMLDict loaded_raml: OrderedDict of loaded RAML file
    :returns: :py:class:`.raml.RootNode` object.
    :raises: :py:class:`.errors.InvalidRAMLError` when RAML file is invalid
    """

    validate = str(_get(config, "validate")).lower() == 'true'

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


def create_root(raml, config):
    """
    Creates a Root Node based off of the RAML's root section.

    :param RAMLDict raml: loaded RAML file
    :returns: :py:class:`.raml.RootNode` object with API root attributes set
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

    def base_uri_params():
        data = _get(raml, "baseUriParameters", {})
        params = _create_base_param_obj(data, URIParameter, config, errors)
        uri = _get(raml, "baseUri", "")
        declared = _get(raml, "uriParameters", {})
        declared = list(iterkeys(declared))
        return _preserve_uri_order(uri, params, config, errors, declared)

    def uri_params():
        data = _get(raml, "uriParameters", {})
        params = _create_base_param_obj(data, URIParameter, config, errors)
        uri = _get(raml, "baseUri", "")

        declared = []
        base = base_uri_params()
        if base:
            declared = [p.name for p in base]
        return _preserve_uri_order(uri, params, config, errors, declared)

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

    return RootNode(
        raml_obj=raml,
        raw=raml,
        title=_get(raml, "title"),
        version=_get(raml, "version"),
        protocols=protocols(),
        base_uri=base_uri(),
        base_uri_params=base_uri_params(),
        uri_params=uri_params(),
        media_type=_get(raml, "mediaType"),
        documentation=docs(),
        schemas=schemas(),
        config=config,
        secured_by=_get(raml, "securedBy"),
        errors=errors
    )


def create_sec_schemes(raml_data, root):
    """
    Parse security schemes into ``SecurityScheme`` objects

    :param dict raml_data: Raw RAML data
    :param RootNode root: Root Node
    :returns: list of :py:class:`.parameters.SecurityScheme` objects
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

    def headers(header_data):
        _headers = []
        header_data = _get(header_data, "headers", {})
        for k, v in list(iteritems(header_data)):
            h = _create_base_param_obj({k: v},
                                       Header,
                                       root.config,
                                       root.errors)
            _headers.extend(h)
        return _headers

    def body(body_data):
        body_data = _get(body_data, "body", {})
        _body = []
        for k, v in list(iteritems(body_data)):
            body = Body(
                mime_type=k,
                raw=v,
                schema=load_schema(_get(v, "schema")),
                example=load_schema(_get(v, "example")),
                form_params=_get(v, "formParameters"),
                config=root.config,
                errors=root.errors
            )
            _body.append(body)
        return _body

    def responses(resp_data):
        _resps = []
        resp_data = _get(resp_data, "responses", {})
        for k, v in list(iteritems(resp_data)):
            response = Response(
                code=k,
                raw=v,
                desc=_get(v, "description"),
                headers=headers(_get(v, "headers", {})),
                body=body(_get(v, "body", {})),
                config=root.config,
                errors=root.errors
            )
            _resps.append(response)
        return sorted(_resps, key=lambda x: x.code)

    def query_params(param_data):
        param_data = _get(param_data, "queryParameters", {})
        _params = []
        for k, v in list(iteritems(param_data)):
            p = _create_base_param_obj({k: v},
                                       QueryParameter,
                                       root.config,
                                       root.errors)
            _params.extend(p)
        return _params

    def uri_params(param_data):
        param_data = _get(param_data, "uriParameters")
        _params = []
        for k, v in list(iteritems(param_data)):
            p = _create_base_param_obj({k: v},
                                       URIParameter,
                                       root.config,
                                       root.errors)
            _params.extend(p)
        return _params

    def form_params(param_data):
        param_data = _get(param_data, "formParameters", {})
        _params = []
        for k, v in list(iteritems(param_data)):
            p = _create_base_param_obj({k: v},
                                       FormParameter,
                                       root.config,
                                       root.errors)
            _params.extend(p)
        return _params

    def usage(desc_by_data):
        return _get(desc_by_data, "usage")

    def media_type(desc_by_data):
        return _get(desc_by_data, "mediaType")

    def protocols(desc_by_data):
        return _get(desc_by_data, "protocols")

    def documentation(desc_by_data):
        d = _get(desc_by_data, "documentation", [])
        assert isinstance(d, list), "Error parsing documentation"
        docs = [Documentation(_get(i, "title"), _get(i, "content")) for i in d]
        return docs or None

    def set_property(node, obj, node_data):
        func = _map_object_types(obj)
        item_objs = func({obj: node_data})
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

    schemes = _get(raml_data, "securitySchemes", [])
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

    def protocols():
        return _get(data, "protocols")

    def query_params():
        return set_param_object(data, "queryParameters", root)

    def uri_params():
        return set_param_object(data, "uriParameters", root)

    def form_params():
        return set_param_object(data, "formParameters", root)

    def base_uri_params():
        return set_param_object(data, "baseUriParameters", root)

    def headers(data):
        return set_param_object(data, "headers", root)

    def body(data):
        body = _get(data, "body", {})
        body_objects = []
        for key, value in list(iteritems(body)):
            body = Body(
                mime_type=key,
                raw=value,
                schema=load_schema(_get(value, "schema")),
                example=load_schema(_get(value, "example")),
                form_params=_get(value, "formParameters"),
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
                desc=_get(value, "description"),
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
            media_type=_get(data, "mediaType"),
            usage=_get(data, "usage"),
            protocols=protocols(),
            errors=root.errors
        )

    traits = _get(raml_data, "traits", [])
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
    accepted_methods = _get(root.config, "http_optional")

    #####
    # Set ResourceTypeNode attributes
    #####

    def headers(data):
        _headers = _get(data, "headers", {})
        if _get(v, "type"):
            _headers = _get_inherited_item(_headers, "headers",
                                           resource_types,
                                           meth, v)

        header_objs = _create_base_param_obj(_headers,
                                             Header,
                                             root.config,
                                             root.errors)
        if header_objs:
            for h in header_objs:
                h.method = method(meth)

        return header_objs

    def body(data):
        _body = _get(data, "body", default={})
        if _get(v, "type"):
            _body = _get_inherited_item(_body, "body", resource_types,
                                        meth, v)

        body_objects = []
        for key, value in list(iteritems(_body)):
            body = Body(
                mime_type=key,
                raw=value,
                schema=load_schema(_get(value, "schema")),
                example=load_schema(_get(value, "example")),
                form_params=_get(value, "formParameters"),
                config=root.config,
                errors=root.errors
            )
            body_objects.append(body)
        return body_objects or None

    def responses(data):
        response_objects = []
        _responses = _get(data, "responses", {})
        if _get(v, "type"):
            _responses = _get_inherited_item(_responses, "responses",
                                             resource_types, meth, v)

        for key, value in list(iteritems(_responses)):
            _headers = _get(_get(data, "responses", {}), key, {})
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
        uri_params = _get_attribute_dict(data, "uriParameters", v)

        if _get(v, "type"):
            uri_params = _get_inherited_type_params(v, "uriParameters",
                                                    uri_params, resource_types)
        return _create_base_param_obj(uri_params,
                                      URIParameter,
                                      root.config,
                                      root.errors)

    def base_uri_params(data):
        uri_params = _get_attribute_dict(data, "baseUriParameters", v)

        return _create_base_param_obj(uri_params,
                                      URIParameter,
                                      root.config,
                                      root.errors)

    def query_params(data):
        query_params = _get_attribute_dict(data, "queryParameters", v)

        if _get(v, "type"):
            query_params = _get_inherited_type_params(v, "queryParameters",
                                                      query_params,
                                                      resource_types)

        return _create_base_param_obj(query_params,
                                      QueryParameter,
                                      root.config,
                                      root.errors)

    def form_params(data):
        form_params = _get_attribute_dict(data, "formParameters", v)

        if _get(v, "type"):
            form_params = _get_inherited_type_params(v, "formParameters",
                                                     form_params,
                                                     resource_types)

        return _create_base_param_obj(form_params,
                                      FormParameter,
                                      root.config,
                                      root.errors)

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

    def optional():
        if meth:
            return "?" in meth

    def protocols(data):
        m, r = _get_res_type_attribute(v, data, "protocols", None)
        return m or r or root.protocols

    def is_(data):
        m, r = _get_res_type_attribute(v, data, "is", default=[])
        return m + r or None

    def traits(data):
        assigned = is_(data)
        if assigned:
            if root.traits:
                trait_objs = []
                for trait in assigned:
                    obj = [t for t in root.traits if t.name == trait]
                    if obj:
                        trait_objs.append(obj[0])
                return trait_objs or None

    def secured_by(data):
        m, r = _get_res_type_attribute(v, data, "securedBy", [])
        return m + r or None

    def security_schemes_(data):
        secured = secured_by(data)
        return security_schemes(secured, root)

    def wrap(key, data, meth, _v):
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
            media_type=_get(v, "mediaType"),
            desc=description(),
            type=type_(),
            method=method(meth),
            usage=_get(v, "usage"),
            optional=optional(),
            is_=is_(data),
            traits=traits(data),
            secured_by=secured_by(data),
            security_schemes=security_schemes_(data),
            display_name=_get(data, "displayName", key),
            protocols=protocols(data),
            errors=root.errors
        )

    resource_types = _get(raml_data, "resourceTypes", [])
    resource_type_objects = []
    child_res_type_objects = []
    child_res_type_names = []

    for res in resource_types:
        for k, v in list(iteritems(res)):
            if isinstance(v, dict):
                if "type" in list(iterkeys(v)):
                    child_res_type_objects.append({k: v})
                    child_res_type_names.append(k)

                else:
                    for meth in list(iterkeys(v)):
                        if meth in accepted_methods:
                            method_data = _get(v, meth, {})
                            resource = wrap(k, method_data, meth, v)
                            resource_type_objects.append(resource)
            else:
                meth = None
                resource = wrap(k, {}, meth, v)
                resource_type_objects.append(resource)

    while child_res_type_objects:
        child = child_res_type_objects.pop()
        name = list(iterkeys(child))[0]
        data = list(itervalues(child))[0]
        parent = data.get("type")
        if parent in child_res_type_names:
            continue
        p_data = [r for r in resource_types if list(iterkeys(r))[0] == parent]
        p_data = p_data[0].get(parent)
        res_data = _get_data_union(data, p_data)

        for meth in list(iterkeys(res_data)):
            if meth in accepted_methods:
                method_data = _get(res_data, meth, {})
                comb_data = dict(list(iteritems(method_data)) +
                                 list(iteritems(res_data)))
                resource = ResourceTypeNode(
                    name=name,
                    raw=res_data,
                    root=root,
                    headers=headers(method_data),
                    body=body(method_data),
                    responses=responses(method_data),
                    uri_params=uri_params(comb_data),
                    base_uri_params=base_uri_params(comb_data),
                    query_params=query_params(method_data),
                    form_params=form_params(method_data),
                    media_type=_get(v, "mediaType"),
                    desc=description(),
                    type=_get(res_data, "type"),
                    method=method(meth),
                    usage=_get(res_data, "usage"),
                    optional=optional(),
                    is_=is_(res_data),
                    traits=traits(res_data),
                    secured_by=secured_by(res_data),
                    security_schemes=security_schemes_(res_data),
                    display_name=_get(method_data, "displayName", name),
                    protocols=protocols(res_data),
                    errors=root.errors
                )
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
            avail = _get(root.config, "http_optional")
            methods = [m for m in avail if m in list(iterkeys(v))]
            if "type" in list(iterkeys(v)):
                assigned = _resource_type_lookup(_get(v, "type"), root)
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
    # Node attribute functions
    #####
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
        # trait = _get_trait("protocols", root, is_())
        kwargs = dict(root=root,
                      is_=is_(),
                      type_=type_(),
                      method=method,
                      data=raw_data,
                      parent=parent)
        objects_to_inherit = [
            "traits", "types", "method", "resource", "parent"
        ]
        inherited = get_inherited("protocols", objects_to_inherit, **kwargs)
        trait = inherited["traits"]
        r_type = inherited["types"]
        meth = inherited["method"]
        res = inherited["resource"]
        parent_ = inherited["parent"]
        default = [root.base_uri.split("://")[0].upper()]

        return meth or r_type or trait or res or parent_ or default

    def headers():
        """Set resource's supported headers."""
        headers = _get_attribute("headers", method, raw_data)
        header_objs = _get_inherited_attribute("headers", root, type_(),
                                               method, is_())

        _headers = _create_base_param_obj(headers,
                                          Header,
                                          root.config,
                                          root.errors,
                                          method=method)
        if _headers is None:
            return header_objs or None
        return _remove_duplicates(header_objs, _headers)

    def body():
        """Set resource's supported request/response body."""
        bodies = _get_attribute("body", method, raw_data)
        body_objects = _get_inherited_attribute("body", root, type_(),
                                                method, is_())

        _body_objs = []
        for k, v in list(iteritems(bodies)):
            if v is None:
                continue
            body = Body(
                mime_type=k,
                raw={k: v},
                schema=load_schema(_get(v, "schema")),
                example=load_schema(_get(v, "example")),
                form_params=_get(v, "formParameters"),
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
                    if key in ('schema', 'example'):
                        default_body[key] = load_schema(spec) if spec else {}
                else:
                    mime_type = key
                    # spec might be '!!null'
                    raw = spec or body
                    _schema = {}
                    _example = {}
                    if spec:
                        _schema_spec = _get(spec, 'schema', '')
                        _example_spec = _get(spec, 'example', '')
                        if _schema_spec:
                            _schema = load_schema(_schema_spec)
                        if _example_spec:
                            _example = load_schema(_example_spec)
                    body_list.append(Body(
                        mime_type=mime_type,
                        raw=raw,
                        schema=_schema,
                        example=_example,
                        form_params=None,
                        config=root.config,
                        errors=root.errors
                    ))
            if default_body:
                body_list.append(Body(
                    mime_type=root.media_type,
                    raw=body,
                    schema=_get(default_body, 'schema'),
                    example=_get(default_body, 'example'),
                    form_params=None,
                    config=root.config,
                    errors=root.errors
                ))

            return body_list or None

        resps = _get_attribute("responses", method, raw_data)
        type_resp = _get_resource_type("responses", root, type_(), method)
        trait_resp = _get_trait("responses", root, is_())
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
                body = resp_body(_get(v, "body", {}))
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
                    desc=_get(v, "description") or inherit_resp.desc,
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
        unparsed_attr = "uriParameters"
        parsed_attr = "uri_params"
        root_params = root.uri_params
        params = _create_uri_params(unparsed_attr, parsed_attr, root_params,
                                    root, type_(), is_(), method, raw_data,
                                    parent)
        declared = []
        base = base_uri_params()
        if base:
            declared = [p.name for p in base]

        return _preserve_uri_order(absolute_uri(), params, root.config,
                                   root.errors, declared)

    def base_uri_params():
        """Set resource's base URI parameters."""
        root_params = root.base_uri_params
        kw = dict(type=type_(), is_=is_(), root_params=root_params)
        params = set_params(raw_data, "base_uri_params", root, method,
                            inherit=True, **kw)
        declared = []
        uri = root.uri_params
        base = root.base_uri_params
        if uri:
            declared = [p.name for p in uri]
        if base:
            declared.extend([p.name for p in base])
        return _preserve_uri_order(root.base_uri, params, root.config,
                                   root.errors, declared)

    def query_params():
        kw = dict(type_=type_(), is_=is_())
        return set_params(raw_data, "query_params", root, method,
                          inherit=True, **kw)

    def form_params():
        """Set resource's form parameters."""
        kw = dict(type_=type_(), is_=is_())
        return set_params(raw_data, "form_params", root, method,
                          inherit=True, **kw)

    def media_type_():
        """Set resource's supported media types."""
        if method is None:
            return None
        kwargs = dict(root=root,
                      is_=is_(),
                      type_=type_(),
                      method=method,
                      data=raw_data)
        objects_to_inherit = [
            "method", "traits", "types", "resource", "root"
        ]
        inherited = get_inherited("mediaType", objects_to_inherit, **kwargs)
        meth = inherited.get("method")
        trait = inherited.get("trait")
        r_type = inherited.get("types")
        res = inherited.get("resource")
        root_ = inherited.get("root")
        return meth or trait or r_type or res or root_

    def description():
        """Set resource's description."""
        desc = _get(raw_data, "description")
        try:
            desc = _get(_get(raw_data, method), "description")
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
                desc = _get(raw_data, "description")
        return desc

    def is_():
        """Set resource's assigned trait names."""
        is_list = []
        res_level = _get(raw_data, "is")
        if res_level:
            assert isinstance(res_level, list), "Error parsing trait"
            is_list.extend(res_level)
        method_level = _get(raw_data, method, {})
        if method_level:
            method_level = _get(method_level, "is")
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
        __get_method = _get(raw_data, method, {})
        assigned_type = _get(__get_method, "type")
        if assigned_type:
            if not isinstance(assigned_type, dict):
                return assigned_type
            return list(iterkeys(assigned_type))[0]  # NOCOV

        assigned_type = _get(raw_data, "type")
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
            method_level = _get(raw_data, method, {})
            if method_level:
                secured_by = _get(method_level, "securedBy")
                if secured_by:
                    return secured_by
        resource_level = _get(raw_data, "securedBy")
        if resource_level:
            return resource_level
        root_level = root.secured_by
        if root_level:
            return root_level

    def security_schemes_():
        """Set resource's assigned security scheme objects."""
        secured = secured_by()
        return security_schemes(secured, root)

    node = ResourceNode(
        name=name,
        raw=raw_data,
        method=method,
        parent=parent,
        root=root,
        display_name=_get(raw_data, "displayName", name),
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
        media_type=media_type_(),
        desc=description(),
        is_=is_(),
        traits=traits(),
        type=type_(),
        resource_type=resource_type(),
        secured_by=secured_by(),
        security_schemes=security_schemes_(),
        errors=root.errors
    )
    if resource_type():
        # correct inheritance (issue #23)
        node._inherit_type()
    return node
