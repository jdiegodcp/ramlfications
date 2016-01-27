# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function

import re

from six import iterkeys, string_types

from .common import (
    _get, get_inherited_trait_data, substitute_parameters,
    INH_FUNC_MAPPING
)


#####
# Public util functions for ramlfications.parser.main.py
#####
def parse_assigned_dicts(items):
    """
    Return a list of trait/type/scheme names if an assigned trait/
    resource type/secured_by is a dictionary.
    """
    if not items:
        return
    if isinstance(items, dict):
        return list(iterkeys(items))[0]
    if isinstance(items, list):
        item_names = []
        for i in items:
            if isinstance(i, string_types):
                item_names.append(i)
            elif isinstance(i, dict):
                name = list(iterkeys(i))[0]
                item_names.append(name)
        return item_names
    return items


def resolve_inherited_scalar(item, inherit_from=[], **kwargs):
    """
    Returns data associated with item (e.g. ``protocols``) while
    preserving order of inheritance.
    """
    path = _get(kwargs, "resource_path")
    path_name = "<<resourcePathName>>"
    if path:
        path_name = path.lstrip("/")
    else:
        path = "<<resourcePath>>"
    for obj_type in inherit_from:
        inherit_func = __map_inheritance(obj_type)
        inh = inherit_func(item, **kwargs)
        if inh:
            param = {}
            param["resourcePath"] = path
            param["resourcePathName"] = path_name
            return substitute_parameters(inh, param)
    return None


def sort_uri_params(params, path):
    if not params:
        return params
    # if this is hit, RAML shouldn't be valid anyways.
    if isinstance(path, list):
        path = path[0]

    pattern = re.compile(r'\{(.*?)\}')
    param_order = re.findall(pattern, path)

    media_type = None
    media_type_param = None
    for p in params:
        if p.name == "mediaTypeExtension":
            media_type = params.index(p)
            break

    if media_type is not None:
        media_type_param = params.pop(media_type)

    to_sort = []

    for p in params:
        if p.name == "version":
            continue
        index = param_order.index(p.name)
        to_sort.append((index, p))

    params = [p[1] for p in sorted(to_sort, key=lambda item: item[0])]

    if media_type_param:
        params.append(media_type_param)

    return params


#####
# Private module-level helper functions
#####
def __trait(item, **kwargs):
    root = _get(kwargs, "root")
    is_ = _get(kwargs, "is_")
    if is_ and root:
        raml = _get(root.raw, "traits")
        if raml:
            data = get_inherited_trait_data(item, raml, is_, root)
            return _get(data, item)


def __map_inheritance(obj_type):
    INH_FUNC_MAPPING["traits"] = __trait
    return INH_FUNC_MAPPING[obj_type]


def convert_camel_case(name):
    """convert CamlCase to under_score names to better match pep8 style

    :param string name: camlCase name of a raml Property
    :returns string: under_score version of the raml Property

    implementation courtesy of:
    http://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-camel-case
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
