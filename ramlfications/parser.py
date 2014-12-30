# ! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function

__all__ = ["RAMLParserError", "parse_raml"]

from collections import defaultdict

try:
    from collections import OrderedDict
except ImportError:  # pragma: no cover
    from ordereddict import OrderedDict

import json

from six import iteritems

from .parameters import SecurityScheme, Oauth2Scheme, Oauth1Scheme
from .raml import RAMLRoot, Trait, ResourceType, Resource, RAMLParserError
from .utils import fill_reserved_params

AVAILABLE_METHODS = ['get', 'post', 'put', 'delete', 'patch', 'head',
                     'options', 'trace', 'connect']
HTTP_METHODS = [
    "get", "post", "put", "delete", "patch", "options",
    "head", "trace", "connect", "get?", "post?", "put?", "delete?",
    "patch?", "options?", "head?", "trace?", "connect?"
]


#####
# Main parser function from which __init__:parse calls
#####
def parse_raml(loaded_raml):
    """
    Parses the given RAML file and creates a RAMLRoot object.

    :param ramlfications.loader.RAMLDict loaded_raml: Loaded RAML file
    :return: Parsed RAML file
    :rtype: RAMLRoot
    :raises RAMLParserError: If error occurred during parsing of the
        RAML file.
    """
    raml = loaded_raml.data

    root = RAMLRoot(loaded_raml)
    root.security_schemes = _parse_security_schemes(raml, root)
    root.traits = _parse_traits(raml, root)
    root.resource_types = _parse_resource_types(raml, root)
    root.resources = _parse_resources(raml, root)

    return root


####
# Logic for parsing of Resources/endpoints into Resource objects
####
def _parse_resources(raml, root):
    resource_stack = __yield_resources(raml, root)
    sorted_resources = __order_resources(resource_stack)
    resources = __add_properties_to_resources(sorted_resources, root)
    return resources


def __add_properties_to_resources(sorted_resources, root):
    for r in sorted_resources:
        r.traits = __get_traits(r, root)
        r.resource_type = __get_resource_type(r, root)
        r.security_schemes = __get_secured_by(r, root)
    return sorted_resources


def __order_resources(resource_stack):
    _resources = OrderedDict()
    for res in resource_stack:
        key_name = res.method + "-" + res.path
        _resources[key_name] = res

    resources = defaultdict(list)
    for k, v in list(_resources.items()):
        resources[v.path].append((v.method.upper(), v))
    sorted_dict = OrderedDict(sorted(resources.items(), key=lambda t: t[0]))
    sorted_list = []
    for item in sorted_dict.values():
        for i in item:
            sorted_list.append(i[1])
    return sorted_list


def __create_resource_stack(items, resource_stack, root):
    for k, v in list(items.items()):
        if k.startswith("/"):
            keys = items[k].keys()
            methods = [m for m in AVAILABLE_METHODS if m in keys]
            if methods:
                for m in AVAILABLE_METHODS:
                    if m in items[k].keys():
                        node = Resource(name=k, data=v,
                                        method=m, api=root)
                        resource_stack.append(node)
            else:
                for item in keys:
                    if item.startswith("/"):
                        _item = {}
                        _item[k + item] = items.get(k).get(item)
                        resource_stack = __create_resource_stack(
                            _item, resource_stack, root)

    return resource_stack


def __yield_resources(raml, root):
    resource_stack = __create_resource_stack(raml, [], root)
    while resource_stack:
        current = resource_stack.pop(0)
        yield current
        if current.data:
            for child_k, child_v in list(current.data.items()):
                if child_k.startswith("/"):
                    for method in AVAILABLE_METHODS:
                        if method in current.data[child_k].keys():
                            child = Resource(name=child_k, data=child_v,
                                             method=method, parent=current,
                                             api=root)
                            resource_stack.append(child)


#####
# Logic for parsing of resourceTypes into ResourceType objects
#####
def __get_union(resource, inherited_resource):
    if inherited_resource is {}:
        return resource
    union = {}
    if not resource:
        return inherited_resource
    for k, v in list(inherited_resource.items()):
        if k not in resource.keys():
            union[k] = v
        else:
            resource_values = resource.get(k)
            inherited_values = inherited_resource.get(k, {})
            union[k] = dict(inherited_values.items() +
                            resource_values.items())
    for k, v in list(resource.items()):
        if k not in inherited_resource.keys():
            union[k] = v
    return union


# Returns data dict of particular resourceType
def __get_inherited_resource(res_name, resource_types):
    for r in resource_types:
        if res_name == r.keys()[0]:
            return dict(r.values()[0].items())


def __map_inherited_resource_types(root, resource, inherited, types):
    resources = []
    inherited_res = __get_inherited_resource(inherited, types)
    for k, v in list(resource.items()):
        for i in v.keys():
            if i in HTTP_METHODS:
                data = __get_union(v.get(i, {}),
                                   inherited_res.get(i, {}))
                resources.append(ResourceType(k, data, i, root,
                                              type=inherited))
    return resources


def _parse_resource_types(raml, root):
    resource_types = raml.get('resourceTypes', [])
    resources = []
    for resource in resource_types:
        for k, v in list(resource.items()):
            # first parse out if it inherits another resourceType
            if 'type' in v.keys():
                r = __map_inherited_resource_types(root, resource,
                                                   v.get('type'),
                                                   resource_types)
                resources.extend(r)
            # else just create a ResourceType
            else:
                for i in v.keys():
                    if i in HTTP_METHODS:
                        resources.append(ResourceType(k, v, i, root))

    for r in resources:
        r.traits = __get_traits(r, root)
        r.security_schemes = __get_secured_by(r, root)
    return resources or None


#####
# Logic for parsing of traits into Trait objects
#####
def _parse_traits(raml, root):
    traits = raml.get('traits')
    if traits:
        return [Trait(t.keys()[0], t.values()[0], root) for t in traits]
    return None


#####
# Logic for parsing of security schemes into SecurityScheme objects
#####
def _parse_security_schemes(raml, root):
    schemes = raml.get('securitySchemes')
    if schemes:
        return [SecurityScheme(s.keys()[0], s.values()[0]) for s in schemes]
    return None


#####
# Logic for mapping of Trait properties to its Resource/ResourceType
#####
def __fill_params(string, key, value, resource):
    if key in string:
        string = string.replace("<<" + key + ">>", str(value))
    string = fill_reserved_params(resource, string)
    return string


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
        msg = "'{0}' is not defined in API Root's traits."
        raise RAMLParserError(msg)

    for t in api_traits:
        if t.name == _trait:
            _values = list(trait.values())[0]
            data = json.dumps(t.data)
            for k, v in list(_values.items()):
                data = __fill_params(data, k, v, resource)
            data = json.loads(data)
            return Trait(t.name, data, root)
    return None


def __get_traits(resource, root):
    if not resource.is_:
        return
    if not root.traits:
        msg = ("No traits are defined in RAML file but '{0}' trait is "
               "assigned to '{1}'.".format(resource.is_, resource.name))
        raise RAMLParserError(msg)

    trait_objects = []
    for trait in resource.is_:
        trait_names = [t.name for t in root.traits]
        if isinstance(trait, str):
            if trait not in trait_names:
                msg = "'{0}' not defined under traits in RAML.".format(
                    trait)
                raise RAMLParserError(msg)
            str_trait = __get_traits_str(trait, root)
            trait_objects.append(str_trait)
        elif isinstance(trait, dict):
            if trait.keys()[0] not in trait_names:
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


#####
# Logic for mapping of ResourceType objects to its Resource
#####
def __map_resource_string(resource, root):
    api_resources = root.resource_types

    api_resources_names = [a.name for a in api_resources]
    if resource.type not in api_resources_names:
        msg = "'{0}' is not defined in RAML's resourceTypes.".format(
            resource.type)
        raise RAMLParserError(msg)

    for r in api_resources:
        if r.name == resource.type and r.method == resource.method:
            return r
    return None


def __map_resource_dict(resource, root):
    api_resources = root.resource_types or []

    _type = list(resource.type.keys())[0]
    api_resources_names = [a.name for a in api_resources]
    if _type not in api_resources_names:
        msg = "'{0}' is not defined in API Root's resourceTypes.".format(_type)
        raise RAMLParserError(msg)

    for r in api_resources:
        if r.name == _type and r.method == resource.method:
            _values = list(resource.type.values())[0]
            data = json.dumps(r.data)
            for k, v in list(_values.items()):
                data = __fill_params(data, k, v, resource)
            data = json.loads(data)
            return ResourceType(r.name, data, resource.method,
                                root, resource.type)
    return None


def __get_resource_type(resource, root):
    mapped_res_type = None
    if not resource.type:
        return
    if not root.resource_types:
        msg = ("No Resource Types are defined in RAML file but '{0}' "
               "type is assigned to '{1}'.".format(resource.type,
                                                   resource.name))
        raise RAMLParserError(msg)

    if isinstance(resource.type, str):
        mapped_res_type = __map_resource_string(resource, root)

    elif isinstance(resource.type, dict):
        if len(resource.type.keys()) > 1:
            msg = "Too many resource types applied to one resource."
            raise RAMLParserError(msg)
        mapped_res_type = __map_resource_dict(resource, root)

    else:
        msg = "Error applying resource type '{0}'' to '{1}'.".format(
            resource.type, resource.name)
        raise RAMLParserError(msg)
    return mapped_res_type


#####
# Logic for mapping of securitySchemes to its Resource/Resource Type
#####
def __set_scheme(scheme):
    return {'oauth_2_0': Oauth2Scheme,
            'oauth_1_0': Oauth1Scheme}[scheme]


def __map_secured_by_str(secured, root):
    for s in root.security_schemes:
        if s.name == secured:
            return s


def __map_secured_by_dict(secured, root):
    scheme = list(secured.keys())[0]

    for s in root.security_schemes:
        if s.name == scheme:
            scheme_obj = __set_scheme(s.name)(s.data.get('settings'))

    for k, v in iteritems(secured.values()[0]):
        setattr(scheme_obj, k, v)

    return scheme_obj


def __get_secured_by(resource, root):
    if not resource.secured_by:
        return
    if not root.security_schemes:
        msg = ("No Security Schemes are defined in RAML file but '{0}' "
               "scheme is assigned to '{1}'.".format(resource.secured_by,
                                                     resource.name))
        raise RAMLParserError(msg)

    _secured_by = []
    for secured in resource.secured_by:
        if secured is None:
            _secured_by.append(None)
        elif isinstance(secured, dict):
            _secured_by.append(__map_secured_by_dict(secured, root))
        elif isinstance(secured, str):
            _secured_by.append(__map_secured_by_str(secured, root))
        elif isinstance(secured, list):
            for s in secured:
                _secured_by.append(__map_secured_by_str(s, root))
        else:
            msg = "Error applying security scheme '{0}' to '{1}'.".format(
                secured, resource.name)
            raise RAMLParserError(msg)

    return _secured_by
