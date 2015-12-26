# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function


import json
import re

try:
    from collections import OrderedDict
except ImportError:  # pragma: no cover
    from ordereddict import OrderedDict

from six import iterkeys, iteritems

from . import tags

# pattern for `<<parameter>>` substitution
PATTERN = r'(<<\s*)(?P<pname>{0}\b[^\s|]*)(\s*\|?\s*(?P<tag>!\S*))?(\s*>>)'


#####
# General Helper functions
#####

# general
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


def _get_inherited_res_type_data(attr, types, name, method, root):
    res_level = [
        "baseUriParameters", "uriParameters", "uri_params", "base_uri_params"
    ]
    if isinstance(name, dict):
        name = list(iterkeys(name))[0]
    res_type_raml = [r for r in types if list(iterkeys(r))[0] == name]
    if attr == "uri_params":
        attr = "uriParameters"
    if res_type_raml:
        res_type_raml = _get(res_type_raml[0], name, {})
        raw = _get(res_type_raml, method, None)
        if not raw:
            if method:
                raw = _get(res_type_raml, method + "?", {})

        attribute_data = _get(raw, attr, {})
        if not attribute_data and attr in res_level:
            attribute_data = _get(res_type_raml, attr, {})
        if _get(res_type_raml, "type"):
            inherited = __resource_type_data(attr, root,
                                             res_type_raml.get("type"),
                                             method)
            attribute_data = merge_dicts(attribute_data, inherited)
        return attribute_data
    return {}


def _get_inherited_trait_data(attr, traits, name, root):
    names = []
    if not isinstance(name, list):
        names.append(name)
    else:
        for n in name:
            if isinstance(n, dict):
                n = list(iterkeys(n))[0]
            names.append(n)

    trait_raml = [t for t in traits if list(iterkeys(t))[0] in names]
    trait_data = []
    for n in names:
        for t in trait_raml:
            t_raml = _get(t, n, {})
            attribute_data = _get(t_raml, attr, {})
            trait_data.append({attr: attribute_data})
    return trait_data


def __resource_type_data(attr, root, res_type, method):
    if not res_type:
        return {}
    raml = _get(root.raw, "resourceTypes")
    if raml:
        return _get_inherited_res_type_data(attr, raml, res_type,
                                            method, root)


def merge_dicts(child, parent, path=[]):
    "merges parent into child"
    if path is None:
        path = []
    if not parent:
        return child
    for key in parent:
        if key in child:
            if isinstance(child[key], dict) and isinstance(parent[key], dict):
                merge_dicts(child[key], parent[key], path + [str(key)])
            elif child[key] == parent[key]:
                pass  # same leaf value
            # else:
                # print('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            child[key] = parent[key]
    return child


def _map_attr(attribute):
    """Map RAML attr name to ramlfications attr name"""
    return {
        "mediaType": "media_type",
        "protocols": "protocols",
        "headers": "headers",
        "body": "body",
        "responses": "responses",
        "uriParameters": "uri_params",
        "baseUriParameters": "base_uri_params",
        "queryParameters": "query_params",
        "formParameters": "form_params",
        "description": "description",
        "securedBy": "secured_by",
    }[attribute]


def _replace_str_attr(param, new_value, current_str):
    """
    Replaces ``<<parameters>>`` with their assigned value, processed with \
    any function tags, e.g. ``!pluralize``.
    """
    p = re.compile(PATTERN.format(param))
    ret = re.findall(p, current_str)
    if not ret:
        return current_str
    for item in ret:
        to_replace = "".join(item[0:3]) + item[-1]
        tag_func = item[3]
        if tag_func:
            tag_func = tag_func.strip("!")
            tag_func = tag_func.strip()
            func = getattr(tags, tag_func)
            if func:
                new_value = func(new_value)
        current_str = current_str.replace(to_replace, str(new_value), 1)
    return current_str


def _substitute_parameters(data, param_data):
    json_data = json.dumps(data)
    for key, value in list(iteritems(param_data)):
        json_data = _replace_str_attr(key, value, json_data)
    if isinstance(json_data, str):
        json_data = json.loads(json_data, object_pairs_hook=OrderedDict)
    return json_data
