# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function

import re

from six import itervalues, iterkeys, iteritems

try:
    from collections import OrderedDict
except ImportError:  # NOCOV
    from ordereddict import OrderedDict

from ramlfications.parameters import (
    Documentation, Header, Body, Response, URIParameter, QueryParameter,
    FormParameter, SecurityScheme
)
from ramlfications.utils import load_schema

from .common_utils import _get


#####
# parameters.py object creation
#####
# TODO: not sure I need this here ... I'm essentially creating another
#       object rather than inherit/assign, like with types & traits
def _get_scheme(item, root):
    schemes = root.raw.get("securitySchemes", [])
    for s in schemes:
        if isinstance(item, str):
            if item == list(iterkeys(s))[0]:
                return s
        elif isinstance(item, dict):
            if list(iterkeys(item))[0] == list(iterkeys(s))[0]:
                return s

def security_schemes(secured, root):
    """Set resource's assigned security scheme objects."""
    if secured:
        secured_objs = []
        for item in secured:
            assigned_scheme = _get_scheme(item, root)
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


def create_body_objects(data, root):
    ret_objs = []
    for k, v in list(iteritems(data)):
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
        ret_objs.append(body)
    return ret_objs

#####
# General Helper Functions
#####
# preserve order of URI and Base URI parameters
# used for RootNode, ResourceNode
def _preserve_uri_order(path, param_objs, config, errors, declared=[]):
    # if this is hit, RAML shouldn't be valid anyways.
    if isinstance(path, list):
        path = path[0]

    sorted_params = []
    pattern = "\{(.*?)\}"
    params = re.findall(pattern, path)
    if not param_objs:
        param_objs = []
    # if there are URI parameters in the path but were not declared
    # inline, we should create them.
    # TODO: Probably shouldn't do it in this function, though...
    if len(params) > len(param_objs):
        if len(param_objs) > 0:
            param_names = [p.name for p in param_objs]
            missing = [p for p in params if p not in param_names]
        else:
            missing = params[::]
        # exclude any (base)uri params if already declared
        missing = [p for p in missing if p not in declared]
        for m in missing:
            # no need to create a URI param for version
            if m == "version":
                continue
            data = {"type": "string"}
            _param = URIParameter(name=m,
                                  raw={m: data},
                                  required=True,
                                  display_name=m,
                                  desc=_get(data, "description"),
                                  min_length=_get(data, "minLength"),
                                  max_length=_get(data, "maxLength"),
                                  minimum=_get(data, "minimum"),
                                  maximum=_get(data, "maximum"),
                                  default=_get(data, "default"),
                                  enum=_get(data, "enum"),
                                  example=_get(data, "example"),
                                  repeat=_get(data, "repeat", False),
                                  pattern=_get(data, "pattern"),
                                  type=_get(data, "type", "string"),
                                  config=config,
                                  errors=errors)
            param_objs.append(_param)
    for p in params:
        _param = [i for i in param_objs if i.name == p]
        if _param:
            sorted_params.append(_param[0])
    return sorted_params or None


def _lookup_resource_type(assigned, root):
    """
    Returns ``ResourceType`` object

    :param str assigned: The string name of the assigned resource type
    :param root: RAML root object
    """
    res_types = root.resource_types
    if res_types:
        res_type_obj = [r for r in res_types if r.name == assigned]
        if res_type_obj:
            return res_type_obj[0]


# used for traits & resource nodes
def _map_param_unparsed_str_obj(param):
    return {
        "queryParameters": QueryParameter,
        "uriParameters": URIParameter,
        "formParameters": FormParameter,
        "baseUriParameters": URIParameter,
        "headers": Header
    }[param]


# TODO: refactor - this ain't pretty
# Note: this is only used in `create_node`
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
# Creating Named Parameter-like Objects
#####

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


# helper func for below
def __find_set_object(params, name, root, method=None):
    param_obj = _map_param_unparsed_str_obj(name)
    return _create_base_param_obj(params, param_obj, root.config, root.errors, method=method)


# set uri, form, query, header objects for Trait Nodes, Security Scheme Nodes
def _set_param_trait_object(param_data, param_name, root):
    params = _get(param_data, param_name, {})
    return __find_set_object(params, param_name, root)


def __get_inherited_type_params(data, attribute, params, resource_types):
    inherited = __get_inherited_type_data(data, resource_types)
    inherited_params = _get(inherited, attribute, {})

    return dict(list(iteritems(params)) +
                list(iteritems(inherited_params)))


def __get_inherited_type_data(data, resource_types):
    inherited = __get_inherited_resource(data.get("type"), resource_types)
    return _get(inherited, data.get("type"))


# set parameter objects for Resource Type Nodes
def _set_param_type_object(data, name, raw_data, res_type, root, inherit=False):
    m_data, r_data = _get_res_type_attribute(raw_data, data, name)
    param_data = dict(list(iteritems(m_data)) + list(iteritems(r_data)))
    if inherit:
        if _get(raw_data, "type"):
            param_data = __get_inherited_type_params(raw_data, name,
                                                     param_data, res_type)
    return __find_set_object(param_data, name, root)


# just parsing raw data, no objects
def __get_inherited_resource(res_name, resource_types):
    for resource in resource_types:
        if res_name == list(iterkeys(resource))[0]:
            return resource


def _get_inherited_item(current_items, item_name, res_types, method, data):
    resource = __get_inherited_type_data(data, res_types)
    res_data = _get(resource, method, {})

    method_ = _get(resource, method, {})
    m_data, r_data = _get_res_type_attribute(res_data, method_, item_name)
    items = dict(
        list(iteritems(current_items)) +
        list(iteritems(r_data)) +
        list(iteritems(m_data))
    )
    return items


def _get_res_type_attribute(res_data, method_data, item, default={}):
    method_level = _get(method_data, item, default)
    resource_level = _get(res_data, item, default)
    return method_level, resource_level


#####
# Set Query, Form, URI params for Resource Nodes
#####
# <--[query, base uri, form]-->
def __check_if_exists(param, ret_list):
    if isinstance(param, Body):
        param_name_list = [p.mime_type for p in ret_list]
        if param.mime_type not in param_name_list:
            ret_list.append(param)
            param_name_list.append(param.mime_type)

    else:
        param_name_list = [p.name for p in ret_list]
        if param.name not in param_name_list:
            ret_list.append(param)
            param_name_list.append(param.name)
    return ret_list


# TODO: refactor - this ain't pretty
def __remove_duplicates(to_clean):
    # order: resource, inherited, parent, root
    ret = []

    for param_set in to_clean:
        if param_set:
            for p in param_set:
                ret = __check_if_exists(p, ret)
    return ret or None


def __map_parsed_str(parsed):
    name = parsed.split("_")[:-1]
    name.append("parameters")
    name = [n.capitalize() for n in name]
    name = "".join(name)
    return name[0].lower() + name[1:]


def _set_params(data, attr_name, root, inherit=False, **kw):
    params, param_objs, parent_params, root_params = [], [], [], []

    unparsed = __map_parsed_str(attr_name)
    param_class = _map_param_unparsed_str_obj(unparsed)

    _params = _get_attribute(unparsed, kw.get("method"), data)

    params = _create_base_param_obj(_params, param_class, root.config,
                                    root.errors)

    if params is None:
        params = []

    if inherit:
        inherit_objs = _get_inherited_attribute(attr_name, root,
                                                kw.get("type"),
                                                kw.get("method"),
                                                kw.get("traits"))

    if kw.get("parent"):
        parent_params = getattr(kw.get("parent"), attr_name, [])
    if root:
        root_params = getattr(root, attr_name, [])

    to_clean = (params, inherit_objs, parent_params, root_params)
    return __remove_duplicates(to_clean)
# </--[query, base uri, form]-->


#####
# Ineloquently handling Trait & Resource Type parameter inheritance
#####

# <---[._get_attribute helpers]--->
def __get_method(attribute, method, raw_data):
    """Returns ``attribute`` defined at the method level, or ``None``."""
    ret = _get(raw_data, method, {})
    ret = _get(ret, attribute, {})
    return ret


def __get_resource(attribute, raw_data):
    """Returns ``attribute`` defined at the resource level, or ``None``."""
    return raw_data.get(attribute, {})
# </---[._get_attribute helpers]--->


# <---[parser.create_node]--->
def _get_attribute(attribute, method, raw_data):
    """
    Returns raw data of desired named parameter object, e.g. \
    ``headers``, for both the resource-level data as well as
    method-level data.
    """
    method_level = __get_method(attribute, method, raw_data)
    resource_level = __get_resource(attribute, raw_data)
    return OrderedDict(list(iteritems(method_level)) +
                       list(iteritems(resource_level)))


def _get_inherited_attribute(attribute, root, type_, method, is_):
    type_objects = __get_resource_type(attribute, root, type_, method)
    trait_objects = __get_trait(attribute, root, is_)
    return type_objects + trait_objects


def __get_resource_type(attribute, root, type_, method):
    """Returns ``attribute`` defined in the resource type, or ``None``."""
    if type_ and root.resource_types:
        types = root.resource_types
        r_type = [r for r in types if r.name == type_]
        r_type = [r for r in r_type if r.method == method]
        if r_type:
            if hasattr(r_type[0], attribute):
                if getattr(r_type[0], attribute) is not None:
                    return getattr(r_type[0], attribute)
    return []


def __get_trait(attribute, root, is_):
    """Returns ``attribute`` defined in a trait, or ``None``."""

    if is_:
        traits = root.traits
        if traits:
            trait_objs = []
            for i in is_:
                trait = [t for t in traits if t.name == i]
                if trait:
                    if hasattr(trait[0], attribute):
                        if getattr(trait[0], attribute) is not None:
                            trait_objs.extend(getattr(trait[0], attribute))
            return trait_objs
    return []


#####
# Inheriting from Named Parameter Objects
# (attributes from already created objects)
####

def __map_inheritance(nodetype):
    return {
        "traits": __trait,
        "types": __resource_type,
        "method": __method,
        "resource": __resource,
        "parent": __parent,
        "root": __root
    }[nodetype]


def __map_attr(attribute):
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
        "description": "description"
    }[attribute]


def __get_parent(attribute, parent):
    if parent:
        return getattr(parent, attribute, {})
    return {}


def __trait(item, **kwargs):
    root = kwargs.get("root")
    is_ = kwargs.get("is_")
    return __get_trait(item, root, is_)


def __resource_type(item, **kwargs):
    root = kwargs.get("root")
    type_ = kwargs.get("type_")
    method = kwargs.get("method")
    item = __map_attr(item)
    return __get_resource_type(item, root, type_, method)


def __method(item, **kwargs):
    method = kwargs.get("method")
    data = kwargs.get("data")
    return __get_method(item, method, data)


def __resource(item, **kwargs):
    data = kwargs.get("data")
    return __get_resource(item, data)


def __parent(item, **kwargs):
    parent = kwargs.get("parent")
    return __get_parent(item, parent)


def __root(item, **kwargs):
    root = kwargs.get("root")
    item = __map_attr(item)
    return getattr(root, item, None)


def get_inherited(item, inherit_from=[], **kwargs):
    ret = {}
    for nodetype in inherit_from:
        inherit_func = __map_inheritance(nodetype)
        inherited = inherit_func(item, **kwargs)
        if inherited:
            return inherited
    return None


#####
# Merging inherited values so child takes precendence
####

# confession: had to look up set theory!

def __is_scalar(item):
    scalar_props = [
        "type", "enum", "pattern", "minLength", "maxLength",
        "minimum", "maximum", "example", "repeat", "required",
        "default", "description", "usage", "schema", "example",
        "displayName"
    ]
    return item in scalar_props


def __get_sets(child, parent):
    child_keys = []
    parent_keys = []
    if child:
        child_keys = list(iterkeys(child))
    if parent:
        parent_keys = list(iterkeys(parent))
    child_diff = list(set(child_keys) - set(parent_keys))
    parent_diff = list(set(parent_keys) - set(child_keys))
    intersection = list(set(child_keys).intersection(parent_keys))
    opt_inters = [i for i in child_keys if str(i) + "?" in parent_keys]
    intersection = intersection + opt_inters

    return child, parent, child_diff, parent_diff, intersection


def _get_data_union(child, parent):
    # FIXME: should bring this over from config, not hard code
    methods = [
        'get', 'post', 'put', 'delete', 'patch', 'head', 'options',
        'trace', 'connect', 'get?', 'post?', 'put?', 'delete?', 'patch?',
        'head?', 'options?', 'trace?', 'connect?'
    ]
    union = {}
    child, parent, c_diff, p_diff, inters = __get_sets(child, parent)

    for i in c_diff:
        union[i] = child.get(i)
    for i in p_diff:
        if i in methods and not i.endswith("?"):
                union[i] = parent.get(i)
        if i not in methods:
            union[i] = parent.get(i)
    for i in inters:
        if __is_scalar(i):
            union[i] = child.get(i)
        else:
            _child = child.get(i, {})
            _parent = parent.get(i, {})
            union[i] = _get_data_union(_child, _parent)
    return union


#####
# Traits
#####
# return list of traits if an assigned trait is a dictionary
def _parse_assigned_trait_dicts(traits):
    if not traits:
        return []
    trait_names = []
    for t in traits:
        if isinstance(t, str):
            trait_names.append(t)
        elif isinstance(t, dict):
            name = list(iterkeys(t))[0]
            trait_names.append(name)
    return trait_names
