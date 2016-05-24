# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function

import re

from six import iteritems, iterkeys

from .common import (
    _get, get_inherited_trait_data, merge_dicts, INH_FUNC_MAPPING
)

from ramlfications.models.parameters import (
    QueryParameter, URIParameter, FormParameter, Body, Response, Header
)


#####
# Public util functions for ramlfications.parser.parameters.py
#####
def resolve_scalar_data(param, resolve_from, **kwargs):
    """
    Returns data associated with item (e.g. URI parameters) while
    preserving order of inheritance.
    """
    ret = {}
    for obj_type in resolve_from:
        func = __map_inheritance(obj_type)
        inherited = func(param, **kwargs)
        ret[obj_type] = inherited
    return __merge_resolve_scalar_data(ret, resolve_from)


def map_object(param_type):
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


#####
# Private module-level helper functions
#####
def __merge_resolve_scalar_data(resolved, resolve_from):
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


def __trait(item, **kwargs):
    root = _get(kwargs, "root")
    is_ = _get(kwargs, "is_")
    if is_:
        raml = _get(root.raw, "traits")
        if raml:
            # returns a list of params
            data = get_inherited_trait_data(item, raml, is_, root)
            ret = {}
            for i in data:
                _data = _get(i, item)
                for k, v in list(iteritems(_data)):
                    ret[k] = v
            return ret
    return {}


def __map_inheritance(obj_type):
    INH_FUNC_MAPPING["traits"] = __trait
    return INH_FUNC_MAPPING[obj_type]


def add_missing_uri_data(path, data):
    # if this is hit, RAML shouldn't be valid anyways.
    if isinstance(path, list):
        path = path[0]

    pattern = re.compile(r'\{(.*?)\}')
    params = re.findall(pattern, path)

    default_data = {"type": "string", "required": True}
    defined_params = list(iterkeys(data))
    if params:
        missing_params = set(params).difference(defined_params)
        for p in missing_params:
            # no need to create a URI param for version
            if p == "version":
                continue
            data[p] = default_data
    return data
