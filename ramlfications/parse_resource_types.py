# ! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function

import json

from six import iteritems, iterkeys

from .base_config import config
from .parameters import (
    QueryParameter, URIParameter, FormParameter, Header, Body, Response,
    Content
)
from .raml import Resource, ResourceType, Trait, RAMLParserError
from .utils import fill_reserved_params
from .validate import validate_property, validate


# Logic for parsing of resourceTypes into ResourceType objects
def _parse_resource_types(raml, root):
    resource_types = raml.get('resourceTypes', [])
    resources = []
    for resource in resource_types:
        for k, v in iteritems(resource):
            # first parse out if it inherits another resourceType
            if 'type' in list(iterkeys(v)):
                r = __map_inherited_resource_types(root, resource,
                                                   v.get('type'),
                                                   raml)
                resources.extend(r)
            # else just create a ResourceType
            else:
                for i in list(iterkeys(v)):
                    if i in config.get('defaults', 'http_methods'):
                        resources.append(ResourceType(k, v, i, root))

    resources = __add_properties_to_resource_types(resources, root)
    return resources or None


def __add_properties_to_resource_types(resources, root):
    _s = __set_resource_type_properties
    for r in resources:
        r.is_ = __set_resource_type_is(r, root)
        r.traits = __set_traits(r, root)
        r.security_schemes = __get_secured_by(r, root)
        r.secured_by = __set_secured_by_resource_type(r, root)
        r.usage = __set_usage(r)
        r.query_params = _s(r, 'queryParameters')
        r.uri_params = _s(r, 'uriParameters')
        r.base_uri_params = _s(r, 'baseUriParameters')
        r.form_params = _s(r, 'formParameters')
        r.headers = _s(r, 'headers')
        r.body = _s(r, 'body')
        r.responses = _s(r, 'responses')
        r.protocols = __set_simple_property(r, 'protocols') or root.protocols
        r.media_types = __set_simple_property(r, 'body').keys() or None

        desc = __set_simple_property(r, 'description')
        if desc:
            r.description = Content(desc)
        else:
            r.description = None
    return resources


# Setting properties to ResourceType object
def __set_usage(resource):
    return resource.data.get('usage')


# Allow resource(types) to add/replace resource type properties if
# explicitly defined
def __get_union(resource, inherited_resource):
    if inherited_resource is {}:
        return resource
    union = {}
    if not resource:
        return inherited_resource
    for k, v in iteritems(inherited_resource):
        if k not in resource.keys():
            union[k] = v
        else:
            resource_values = resource.get(k)
            inherited_values = inherited_resource.get(k, {})
            union[k] = dict(iteritems(inherited_values) +
                            iteritems(resource_values))
    for k, v in iteritems(resource):
        if k not in inherited_resource.keys():
            union[k] = v
    return union


# Returns data dict of particular resourceType
def __get_inherited_resource(res_name, raml):
    res_types = raml.get('resourceTypes')
    for t in res_types:
        if list(iterkeys(t))[0] == res_name:
            return t
    return None


# If resource type inherits another resource type, grab elements
def __map_inherited_resource_types(root, resource, inherited, raml):
    resources = []
    inherited_res = __get_inherited_resource(inherited, raml)
    for k, v in iteritems(resource):
        for i in v.keys():
            if i in config.get('defaults', 'http_methods'):
                data = __get_union(resource,
                                   inherited_res.get(i, {}))
                resources.append(ResourceType(k, data, i, root,
                                              type=inherited))
    return resources


def __set_secured_by_resource_type(resource, root):
    method_sec = resource.data.get(resource.orig_method, {}).get('securedBy')
    if method_sec:
        return method_sec
    resource_sec = resource.data.get('securedBy')
    if resource_sec:
        return resource_sec
    if hasattr(resource, 'parent'):
        if hasattr(resource.parent, 'secured_by'):
            return resource.parent.secured_by
    return None


@validate_property
def __set_resource_type_properties(r, property, inherit=False):
    properties = []

    method = r.data.get(r.orig_method, {}).get(property, {})
    resource = r.data.get(property, {})
    items = dict(list(method.items()) + list(resource.items()))

    for k, v in iteritems(items):
        obj = __map_obj(property)
        properties.append(obj(k, v, r))

    if r.traits:
        for t in r.traits:
            item = __map_item_type(property)
            if hasattr(t, item):
                if getattr(t, item) is not None:
                    properties.extend(getattr(t, item))

    if inherit:
        item = __map_item_type(property)
        if hasattr(r.parent, item):
            if getattr(r.parent, item) is not None:
                properties.extend(getattr(r.parent, item))

    return properties or None


def __set_resource_type_is(resource, root):
    resource_traits = resource.data.get('is', [])
    method_traits = resource.data.get(resource.orig_method, {}).get('is', [])

    traits = resource_traits + method_traits
    if traits:
        defined_traits = root.traits
        available_traits = [t for t in defined_traits if t.name in traits]

        if available_traits:
            return traits
    return None


def __set_traits(resource, root):
    resource_level = resource.data.get('is')
    method_level = resource.data.get(resource.orig_method, {}).get('is')
    if not resource_level and not method_level:
        return

    if not root.traits:
        msg = ("No traits are defined in RAML file but '{0}' trait is "
               "assigned to '{1}'.".format((resource_level, method_level),
                                           resource.name))
        raise RAMLParserError(msg)

    assigned_traits = resource_level + method_level
    trait_objects = []
    trait_names = [t.name for t in root.traits]

    for trait in assigned_traits:
        if isinstance(trait, str) or isinstance(trait, list):
            if trait not in trait_names:
                msg = "'{0}' not defined under traits in RAML.".format(
                    trait)
                raise RAMLParserError(msg)
            str_trait = __get_traits_str(trait, root)
            trait_objects.append(str_trait)
        elif isinstance(trait, dict):
            if list(iterkeys(trait))[0] not in trait_names:
                msg = "'{0}' not defined under traits in RAML.".format(
                    trait)
                raise RAMLParserError(msg)
            dict_trait = __get_traits_dict(trait, root, resource)
            trait_objects.append(dict_trait)
        else:
            msg = ("'{0}' needs to be a string referring to a trait, "
                   "or a dictionary mapping parameter values to a "
                   "trait".format(trait))
            raise RAMLParserError(msg)

    return trait_objects or None


@validate
def __get_secured_by(resource, root):
    if not resource.data.get('securedBy'):
        return

    _secured_by = []
    for secured in resource.data.get('securedBy'):
        if secured is None:
            _secured_by.append(None)
        elif isinstance(secured, list) or \
            isinstance(secured, dict) or \
                isinstance(secured, str):
                _secured_by.append(secured)
        else:
            msg = "Error applying security scheme '{0}' to '{1}'.".format(
                secured, resource.name)
            raise RAMLParserError(msg)

    return _secured_by


def __set_simple_property(r, property):
    if isinstance(r, ResourceType):
        method = r.data.get(r.orig_method, {}).get(property, None)
    elif isinstance(r, Resource):
        if r.data.get(r.method) is not None:
            method = r.data.get(r.method, {}).get(property, None)
        else:
            method = None
    else:
        method = None

    if method:
        return method

    resource_property = r.data.get(property)

    if resource_property:
        return resource_property

    if isinstance(r, Resource):
        if r.resource_type:
            if hasattr(r.resource_type, property):
                if getattr(r.resource_type, property) is not None:
                    return getattr(r.resource_type, property)
    return {}


# Add'l logic for mapping of Trait properties to its Resource/ResourceType
def __get_traits_str(trait, root):
    api_traits = root.traits

    api_traits_names = [a.name for a in api_traits]
    if trait not in api_traits_names:
        msg = "'{0}' is not defined in API Root's resourceTypes."
        raise RAMLParserError(msg)

    for t in api_traits:
        if t.name == trait:
            return t
    return None


def __get_traits_dict(trait, root, resource):
    api_traits = root.traits or []

    _trait = list(trait.keys())[0]
    api_trait_names = [a.name for a in api_traits]
    if _trait not in api_trait_names:
        msg = "'{0}' is not defined in API Root's traits.".format(_trait)
        raise RAMLParserError(msg)

    for t in api_traits:
        if t.name == _trait:
            _values = list(trait.values())[0]
            data = json.dumps(t.data)
            for k, v in iteritems(_values):
                data = __fill_params(data, k, v, resource)
            data = json.loads(data)
            return Trait(t.name, data, root)
    return None


#####
# Util functions
#####

def __map_obj(property):
    return {
        'headers': Header,
        'body': Body,
        'responses': Response,
        'queryParameters': QueryParameter,
        'uriParameters': URIParameter,
        'formParameters': FormParameter,
        'baseUriParameters': URIParameter,
    }[property]


def __map_item_type(item):
    return {
        'headers': 'headers',
        'body': 'body',
        'responses': 'responses',
        'queryParameters': 'query_params',
        'uriParameters': 'uri_params',
        'formParameters': 'form_params',
        'baseUriParameters': 'base_uri_params',
    }[item]


def __fill_params(string, key, value, resource):
    if key:
        string = string.replace("<<" + key + ">>", str(value))
    string = fill_reserved_params(resource, string)
    return string
