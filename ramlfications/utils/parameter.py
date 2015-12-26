# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function


from six import iterkeys, iteritems

from .common import (
    _get, _get_inherited_trait_data, _get_inherited_res_type_data,
    merge_dicts, _map_attr
)

from ramlfications.parameters import (
    Body, Response, Header, QueryParameter, URIParameter, FormParameter,
)


# TODO: not sure I need this here ... I'm essentially creating another
#       object rather than inherit/assign, like with types & traits
def _get_scheme(item, root):
    schemes = root.raw.get("securitySchemes", [])
    for s in schemes:
        if item == list(iterkeys(s))[0]:
            return s


# TODO: refactor - this ain't pretty
# Note: this is only used in `create_node`
def _remove_duplicates(inherit_params, resource_params):
    ret = []
    if not resource_params:
        return inherit_params
    if isinstance(resource_params[0], Body):
        _params = [p.mime_type for p in resource_params]
    elif isinstance(resource_params[0], Response):
        _params = [p.code for p in resource_params]
    else:
        _params = [p.name for p in resource_params]

    for p in inherit_params:
        if isinstance(p, Body):
            if p.mime_type not in _params:
                ret.append(p)
        elif isinstance(p, Response):
            if p.code not in _params:
                ret.append(p)
        else:
            if p.name not in _params:
                ret.append(p)
    ret.extend(resource_params)
    return ret or None


def _map_object(param_type):
    """
    Map raw string name from RAML to mirrored ``ramlfications`` object
    """
    return {
        "headers": Header,
        "body": Body,
        "responses": Response,
        "uriParameters": URIParameter,
        "baseUriParameters": URIParameter,
        "queryParameters": QueryParameter,
        "formParameters": FormParameter
    }[param_type]


def resolve_scalar_data(param, resolve_from, **kwargs):
    ret = {}
    for obj_type in resolve_from:
        func = __map_data_inheritance(obj_type)
        inherited = func(param, **kwargs)
        ret[obj_type] = inherited
    return _merge_resolve_scalar_data(ret, resolve_from)


def _merge_resolve_scalar_data(resolved, resolve_from):
    # TODO hmm should this happen...
    if len(resolve_from) == 0:
        return resolved
    if len(resolve_from) == 1:
        return _get(resolved, resolve_from[0], {})

    # the prefered should always be first in resolved_from
    data = _get(resolved, resolve_from[0])
    for item in resolve_from[1:]:
        data = merge_dicts(data, _get(resolved, item, {}))
    return data


def __map_data_inheritance(obj_type):
    return {
        "traits": __trait_data,
        "types": __resource_type_data,
        "method": __method_data,
        "resource": __resource_data,
        "parent": __parent_data,
        "root": __root_data,
    }[obj_type]


def __trait_data(item, **kwargs):
    root = kwargs.get("root_")
    is_ = kwargs.get("is_")
    if is_:
        root_trait = _get(root.raw, "traits")
        if root_trait:
            # returns a list of params
            data = _get_inherited_trait_data(item, root_trait, is_, root)
            ret = {}
            for i in data:
                _data = _get(i, item)
                for k, v in list(iteritems(_data)):
                    ret[k] = v
            return ret
    return {}


def __resource_type_data(item, **kwargs):
    root = kwargs.get("root_")
    type_ = kwargs.get("type_")
    method = kwargs.get("method")
    item = _map_attr(item)
    if type_:
        root_resource_types = _get(root.raw, "resourceTypes", {})
        if root_resource_types:
            item = __reverse_map_attr(item)
            data = _get_inherited_res_type_data(item, root_resource_types,
                                                type_, method, root)
            return data
    return {}


def __method_data(item, **kwargs):
    data = kwargs.get("data")
    return _get(data, item, {})


def __resource_data(item, **kwargs):
    data = kwargs.get("resource_data")
    return _get(data, item, {})


def __parent_data(item, **kwargs):
    data = kwargs.get("parent_data")
    return _get(data, item, {})


def __root_data(item, **kwargs):
    root = kwargs.get("root_")
    return _get(root.raw, item, {})


# <---[.resolve_inherited_scalar helpers]--->
def __reverse_map_attr(attribute):
    """Map RAML attr name to ramlfications attr name"""
    return {
        "media_ype": "mediaType",
        "protocols": "protocols",
        "headers": "headers",
        "body": "body",
        "responses": "responses",
        "uri_params": "uriParameters",
        "base_uri_params": "baseUriParameters",
        "query_params": "queryParameters",
        "form_params": "formParameters",
        "description": "description",
        "secured_by": "securedBy",
    }[attribute]
# </---[.resolve_inherited_scalar helpers]--->
