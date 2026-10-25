# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB


import json
import re

from collections import OrderedDict as PythonOrderedDict

from . import tags


class OrderedDict(PythonOrderedDict):
    """An OrderedDict subclass which displays OrderedDicts like dicts.
    As ramlfication is designed to have nice repr, OrderedDict original repr
    looks very bloated compared to the canonical dict representation.

    """
    def __repr__(self):
        ret = "o{"
        ret += ", ".join([
            "{0}: {1}".format(repr(k), repr(v))
            for k, v in self.items()])
        ret += "}"
        return ret


# pattern for `<<parameter>>` substitution
PATTERN = r'(<<\s*)(?P<pname>{0}\b[^\s|]*)(\s*\|?\s*(?P<tag>!\S*))?(\s*>>)'


#####
# Public functions for modules in ramlfications/parser & ramlfications/utils
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


def resource_path_name(path, raml_version):
    """
    Returns the value of ``<<resourcePathName>>`` for ``path``.

    RAML 0.8: the rightmost path segment. RAML 1.0: the rightmost segment
    that does not contain a URI parameter, falling back to the rightmost
    segment when every segment contains one.
    """
    segments = path.split("/")
    if raml_version == "1.0":
        plain = [s for s in segments if s and "{" not in s]
        if plain:
            return plain[-1]
    return segments[-1]


def substitute_parameters(data, param_data):
    """
    Returns named parameter ``data`` with ``<<parameter>>`` substituted
    with the desired ``param_data``
    """
    json_data = json.dumps(data)
    for key, value in list(param_data.items()):
        json_data = __replace_str_attr(key, value, json_data)
    if isinstance(json_data, str):
        json_data = json.loads(json_data, object_pairs_hook=OrderedDict)
    return json_data


#####
# Public helper functions for modules in ramlfications/utils
#####
def get_inherited_trait_data(attr, traits, name, root):
    """
    Returns trait data that should be assigned to a resource, method,
    or resource type.
    """
    names = []
    if not isinstance(name, list):
        names.append(name)
    else:
        for n in name:
            if isinstance(n, dict):
                n = list(n.keys())[0]
            names.append(n)

    if root.raml_version == "0.8":
        trait_raml = [t for t in traits if list(t.keys())[0] in names]
    else:
        trait_raml = [traits]
    trait_data = []
    for n in names:
        for t in trait_raml:
            t_raml = _get(t, n, {})
            attribute_data = _get(t_raml, attr, {})
            if not attribute_data:
                # optional properties (e.g. ``headers?``) are applied
                # when the trait is used (issue #43)
                attribute_data = _get(t_raml, attr + "?", {})
            trait_data.append({attr: attribute_data})
    return trait_data


def merge_dicts(child, parent, path=[]):
    """Merges parent data into child"""
    if path is None:
        path = []
    if not parent:
        return child
    if not isinstance(child, dict) or not isinstance(parent, dict):
        # scalars (e.g. ``description``): the nearer definition wins
        return child if child else parent
    for key in parent:
        if key in child:
            if isinstance(child[key], dict) and isinstance(parent[key], dict):
                merge_dicts(child[key], parent[key], path + [str(key)])
            elif child[key] == parent[key]:
                pass  # same leaf value
            # else:
                # hmm I feel like something should happen here...
                # print('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            child[key] = parent[key]
    return child


#####
# Private, module-level helper functions
#####
def __replace_str_attr(param, new_value, current_str):
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
        transformed_value = new_value
        if tag_func:
            tag_func = tag_func.strip("!")
            tag_func = tag_func.strip()
            func = getattr(tags, tag_func)
            if func:
                transformed_value = func(new_value)
        current_str = current_str.replace(
            to_replace, str(transformed_value), 1)
    return current_str


#####
# Private module-level helper functions for mapping `resolve_from` items
# to their respective helper parser functions within ramlfications/utils/
#####
def __get_inherited_res_type_data(attr, types, name, method, root,
                                  seen=None):
    res_level = [
        "baseUriParameters", "uriParameters", "uri_params", "base_uri_params"
    ]
    if isinstance(name, dict):
        name = list(name.keys())[0]
    # a ``type`` chain that refers back to itself contributes nothing more
    # (invalid list assignments are reported by validation, not here)
    seen = set(seen or ())
    if isinstance(name, str):
        if name in seen:
            return {}
        seen.add(name)
    if root.raml_version == "0.8":
        res_type_raml = [r for r in types if list(r.keys())[0] == name]
        # only need the first one
        # TODO: clean me up
        if res_type_raml:
            res_type_raml = res_type_raml[0]
    else:
        res_type_raml = types
    if attr == "uri_params":
        attr = "uriParameters"
    if res_type_raml:
        res_type_raml = _get(res_type_raml, name, {})
        raw = _get(res_type_raml, method, None)
        if not raw:
            if method:
                raw = _get(res_type_raml, method + "?", {})

        attribute_data = _get(raw, attr, {})
        if not attribute_data:
            # optional properties (e.g. ``headers?``) are inherited when
            # the resource defines the method (issue #43)
            attribute_data = _get(raw, attr + "?", {})
        if not attribute_data and attr in res_level:
            attribute_data = _get(res_type_raml, attr, {})
        if _get(res_type_raml, "type"):
            assigned = res_type_raml.get("type")
            inherited = __resource_type_data(attr, root, assigned,
                                             method, seen)
            # parameters this type passes to its own type, e.g.
            # ``type: {base: {thing: <<item>>}}``; ``<<item>>`` is filled
            # in later from the resource's own assignment
            if isinstance(assigned, dict) and inherited:
                values = list(assigned.values())[0]
                if isinstance(values, dict):
                    inherited = substitute_parameters(inherited, values)
            attribute_data = merge_dicts(attribute_data, inherited)
        return attribute_data
    return {}


def __resource_type_data(attr, root, res_type, method, seen=None):
    if not res_type:
        return {}
    raml = _get(root.raw, "resourceTypes")
    if raml:
        return __get_inherited_res_type_data(attr, raml, res_type,
                                             method, root, seen)


def __method_data(item, **kwargs):
    data = _get(kwargs, "data")
    return _get(data, item, {})


def __resource_data(item, **kwargs):
    data = kwargs.get("resource_data")
    data = _get(kwargs, "resource_data")
    return _get(data, item, {})


def __resource_type(item, **kwargs):
    root = _get(kwargs, "root")
    type_ = _get(kwargs, "type_")
    method = _get(kwargs, "method")

    if type_ and root:
        raml = _get(root.raw, "resourceTypes")
        if raml:
            return __get_inherited_res_type_data(item, raml, type_,
                                                 method, root)
    return {}


def __parent(item, **kwargs):
    data = _get(kwargs, "parent_data")
    return _get(data, item, {})


def __root(item, **kwargs):
    root = _get(kwargs, "root")
    return _get(root.raw, item, {})


# dict mapping resolve_from items -> helper functions
# used in ramlfications/utils/*
INH_FUNC_MAPPING = {
    "traits": None,  # to be set in respective utils module
    "types": __resource_type,
    "method": __method_data,
    "resource": __resource_data,
    "parent": __parent,
    "root": __root,
}


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
        "is": "is_",
        "type": "type",
        "documentation": "documentation",
        "usage": "usage",
    }[attribute]
