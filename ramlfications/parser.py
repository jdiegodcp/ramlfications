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
import re

from six import iteritems, iterkeys


from .base_config import config
from .parameters import (
    SecurityScheme, QueryParameter, URIParameter, FormParameter,
    Header, Body, Response, Content, Documentation
)
from .raml import RAMLRoot, Trait, ResourceType, Resource, RAMLParserError
from .utils import fill_reserved_params
from .validate import validate
from .parse_traits import _parse_traits
from .parse_resource_types import _parse_resource_types


#####
# Main parser function from which __init__:parse calls
#####
def parse_raml(loaded_raml, production, parse):
    """
    Parses the given RAML file and creates a :py:class:`.raml.RAMLRoot` object.

    :param ramlfications.loader.RAMLDict loaded_raml: Loaded RAML file
    :return: Parsed RAML file
    :rtype: RAMLRoot
    :raises RAMLParserError: If error occurred during parsing of the
        RAML file.
    """
    raml = loaded_raml.data
    __raml_header(loaded_raml.raml_file)
    root = RAMLRoot(loaded_raml)
    root.base_uri = _set_base_uri(raml)
    root.base_uri_params = _set_base_uri_params(raml, root)
    root.protocols = _set_protocols(raml, root)
    root.version = _set_version(raml, production)
    root.title = _set_title(raml)
    root.documentation = _set_docs(raml)
    root.media_type = _set_media_type(raml)
    root.schemas = _set_schemas(raml)
    root.uri_params = _set_uri_params(raml, root)
    root.security_schemes = _parse_security_schemes(raml, root)
    root.traits = _parse_traits(raml, root)
    root.resource_types = _parse_resource_types(raml, root)
    root.resources = _parse_resources(raml, root)

    if not parse:
        return
    return root


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


def __pythonic_property_name(property):
    ret = ''

    for char in property:
        if char.islower():
            ret += char
        else:
            ret += '_'
            ret += char.lower()

    return ret


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


def __fill_params(string, key, value, resource):
    if key:
        string = string.replace("<<" + key + ">>", str(value))
    string = fill_reserved_params(resource, string)
    return string


#####
# API Metadata
#####
def __parse_metadata(raml):
    # TODO: add meta data functions here
    pass


@validate
def __raml_header(raml_file):
    pass


@validate
def _set_version(raml, production=False):
    return raml.get('version')


@validate
def _set_base_uri(raml):
    base_uri = raml.get('baseUri')
    if "{version}" in base_uri:
        base_uri = base_uri.replace('{version}', str(raml.get('version')))
    return base_uri


@validate
def _set_protocols(raml, root):
    explicit_protos = raml.get('protocols')

    implicit_protos = re.findall(r"(https|http)", root.base_uri)

    return explicit_protos or implicit_protos or None


@validate
def _set_title(raml):
    return raml.get('title')


@validate
def _set_docs(raml):
    d = raml.get('documentation', [])
    if not isinstance(d, list):
        msg = "Error parsing documentation"
        raise RAMLParserError(msg)
    docs = [Documentation(i.get('title'), i.get('content')) for i in d]
    return docs or None


@validate
def _set_base_uri_params(raml, root):
    base_uri_params = raml.get('baseUriParameters', {})
    uri_params = []
    for k, v in list(base_uri_params.items()):
        uri_params.append((URIParameter(k, v, root)))
    return uri_params or None


@validate
def _set_schemas(raml):
    return raml.get('schemas')


@validate
def _set_media_type(raml):
    return raml.get('mediaType')


@validate
def _set_uri_params(raml, root):
    uri_params = raml.get('uriParameters', {})
    params = []
    for k, v in list(uri_params.items()):
        params.append((URIParameter(k, v, root)))
    return params or None


#####
# RESOURCES
#####

# Logic for parsing of Resources/endpoints into Resource objects
def _parse_resources(raml, root):
    resource_stack = __yield_resources(raml, root)
    sorted_resources = __order_resources(resource_stack)
    resources = __add_properties_to_resources(sorted_resources, root)
    return resources


def __order_resources(resource_stack):
    _resources = OrderedDict()
    for res in resource_stack:
        key_name = res.method + "-" + res.path
        _resources[key_name] = res

    resources = defaultdict(list)
    for k, v in iteritems(_resources):
        resources[v.path].append((v.method.upper(), v))
    sorted_dict = OrderedDict(sorted(iteritems(resources),
                                     key=lambda t: t[0]))
    sorted_list = []
    for item in sorted_dict.values():
        for i in item:
            sorted_list.append(i[1])
    return sorted_list


def __create_resource_stack(items, resource_stack, root):
    for k, v in iteritems(items):
        if k.startswith("/"):
            keys = items[k].keys()
            methods = [m for m in config.get('defaults',
                                             'available_methods') if m in keys]
            if methods:
                for m in config.get('defaults', 'available_methods'):
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
            for child_k, child_v in iteritems(current.data):
                if child_k.startswith("/"):
                    for method in config.get('defaults', 'available_methods'):
                        if method in current.data[child_k].keys():
                            child = Resource(name=child_k, data=child_v,
                                             method=method, parent=current,
                                             api=root)
                            resource_stack.append(child)


@validate
def __add_properties_to_resources(sorted_resources, root):

    def _is():  # TODO: pass thru validation
        resource_level = r.data.get('is', [])
        resource_method = r.data.get(r.method, [])
        if resource_method is not None:
            method_level = resource_method.get('is', [])
        else:
            method_level = []

        trait_names = []

        if isinstance(method_level, str):
            trait_names.append(method_level)
        elif isinstance(method_level, dict):
            trait_names.append(list(iterkeys(method_level)))
        elif isinstance(method_level, list):
            for t in method_level:
                trait_names.append(t)

        if isinstance(resource_level, str):
            trait_names.append(resource_level)
        elif isinstance(resource_level, dict):
            trait_names.append(list(iterkeys(resource_level)))
        elif isinstance(resource_level, list):
            for t in resource_level:
                trait_names.append(t)

        return trait_names or None

    # TODO: this only checks resource-level defined "is", not method-level
    # TODO: the "else" should actually be caught in _is()
    # TODO: pass thru validation
    def traits():
        method_level = r.data.get(r.method).get('is', [])
        resource_level = r.data.get('is', [])
        if not method_level and not resource_level:
            return
        if not root.traits:
            msg = ("No traits are defined in RAML file but '{0}' trait is "
                   "assigned to '{1}'.".format(r.is_, r.name))
            raise RAMLParserError(msg)

        trait_objects = []
        assigned_traits = method_level + resource_level
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
                dict_trait = __get_traits_dict(trait, root, r)
                trait_objects.append(dict_trait)
            else:
                msg = ("'{0}' needs to be a string referring to a trait, "
                       "or a dictionary mapping parameter values to a "
                       "trait".format(trait))
                raise RAMLParserError(msg)

        return trait_objects or None

    # TODO: pass thru validation
    def _type():
        resource_type = r.data.get('type')
        if resource_type:
            if isinstance(resource_type, dict):
                type_name = list(iterkeys(resource_type))[0]
            elif isinstance(resource_type, list):
                type_name = resource_type[0]
            else:
                type_name = resource_type

            defined = root.resource_types
            available_types = [t for t in defined if t.name == type_name]
            set_type = [t for t in available_types if t.method == r.method]
            if set_type:
                return resource_type
        return None

    def __map_resource_string():
        """
        Add'l logic for mapping of ResourceType objects to its Resource
        """
        api_resources = root.resource_types

        api_resources_names = [a.name for a in api_resources]
        if r.type not in api_resources_names:
            msg = "'{0}' is not defined in RAML's resourceTypes.".format(
                r.type)
            raise RAMLParserError(msg)

        for r_ in api_resources:
            if r_.name == r.type and r_.method == r.method:
                return r_
        return None

    def __map_resource_dict():
        """
        Add'l logic for mapping of ResourceType objects to its Resource
        """
        api_resources = root.resource_types or []

        _type = list(r.type.keys())[0]
        api_resources_names = [a.name for a in api_resources]
        if _type not in api_resources_names:
            msg = "'{0}' is not defined in API Root's resourceTypes.".format(
                _type)
            raise RAMLParserError(msg)

        for r_ in api_resources:
            if r_.name == _type and r_.method == r.method:
                _values = list(r.type.values())[0]
                data = json.dumps(r_.data)
                for k, v in iteritems(_values):
                    data = __fill_params(data, k, v, r)
                data = json.loads(data)
                return ResourceType(r_.name, data, r.method, root, r.type)
        return None

    # TODO: pass thru validation
    # TODO: move the RAMLParserError to validate (??)
    def resource_type():
        mapped_res_type = None
        if not r.type:
            return
        if not root.resource_types:
            msg = ("No Resource Types are defined in RAML file but '{0}' "
                   "type is assigned to '{1}'.".format(r.type, r.name))
            raise RAMLParserError(msg)

        if isinstance(r.type, str):
            mapped_res_type = __map_resource_string()

        elif isinstance(r.type, dict):
            mapped_res_type = __map_resource_dict()

        else:
            msg = "Error applying resource type '{0}'' to '{1}'.".format(
                r.type, r.name)
            raise RAMLParserError(msg)
        return mapped_res_type

    # TODO pass thru validation
    def security_schemes():
        """
        Mapping of securitySchemes to its Resource/Resource Type
        """
        if isinstance(r, ResourceType):
            method_level = r.data.get(r.orig_method, {}).get('securedBy')
        else:
            method_level = r.data.get(r.method, {}).get('securedBy')
        resource_level = r.data.get('securedBy', {})
        if not resource_level and not method_level:
            return

        if method_level:
            secured_by = method_level
        else:
            secured_by = resource_level

        _secured_by = []

        if secured_by is None:
            _secured_by.append(None)
        elif isinstance(secured_by, dict):
            sec_obj = __map_secured_by_dict(secured_by, root)
            _secured_by.append(sec_obj)
        elif isinstance(secured_by, list):
            sec_obj = __map_secured_by_list(secured_by, root)
            _secured_by.extend(sec_obj)
        elif isinstance(secured_by, str):
            sec_obj = __map_secured_by_str(secured_by, root)
            _secured_by.append(sec_obj)
        else:
            msg = "Error applying security scheme '{0}' to '{1}'.".format(
                secured_by, r.name)
            raise RAMLParserError(msg)

        return _secured_by

    # TODO pass thru validation
    def secured_by():
        resource_method = r.data.get(r.method)
        if resource_method is not None:
            method_sec = r.data.get(r.method, {}).get('securedBy')
            if method_sec:
                return method_sec
        resource_sec = r.data.get('securedBy')
        if resource_sec:
            return resource_sec
        if hasattr(r, 'parent'):
            if hasattr(r.parent, 'secured_by'):
                return r.parent.secured_by
        return None

    # TODO: pass thru validate property
    def set_properties(property, inherit=False):
        properties = []
        resource_method = r.data.get(r.method, {})
        if resource_method is not None:
            method = resource_method.get(property, {})
        else:
            method = {}
        if r.resource_type:
            if hasattr(r.resource_type, property):
                if getattr(r.resource_type, property) is not None:
                    properties.extend(getattr(r.resource_type, property))

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

    # TODO: pass thru validate property
    def body():
        body_objs = []
        if r.data.get(r.method) is not None:
            method = r.data.get(r.method, {}).get('body', {})
        else:
            method = {}
        resource = r.data.get('body', {})
        if r.resource_type:
            if hasattr(r.resource_type, 'body'):
                if getattr(r.resource_type, 'body') is not None:
                    body_objs.extend(getattr(r.resource_type, 'body'))

        items = dict(list(method.items()) + list(resource.items()))

        for k, v in iteritems(items):
            body_objs.append(Body(k, v, r))

        for p in body_objs:
            if p.mime_type in ["application/x-www-form-urlencoded",
                               "multipart/form-data"]:
                form_params = p.data.get('formParameters')
                if form_params:
                    params = []
                    for i, j in iteritems(form_params):
                        params.append(FormParameter(i, j, r))
                    if r.form_params:
                        r.form_params += params
                    else:
                        r.form_params = params

        return body_objs

    # TODO: pass thru validation
    def description():
        ret = None
        desc = __set_simple_property(r, 'description')
        if desc:
            if isinstance(desc, Content):
                assigned_desc = __fill_params(desc.raw, None, None, r)
            else:
                assigned_desc = __fill_params(desc, None, None, r)
            ret = Content(assigned_desc)
        return ret

    for r in sorted_resources:
        r.is_ = _is()
        r.traits = traits()
        r.type = _type()
        r.resource_type = resource_type()
        r.security_schemes = security_schemes()
        r.secured_by = secured_by()
        r.display_name = r.data.get('displayName', r.name)
        r.base_uri_params = set_properties('baseUriParameters', inherit=True)
        r.query_params = set_properties('queryParameters')
        r.uri_params = set_properties('uriParameters', inherit=True)
        r.form_params = set_properties('formParameters')
        r.headers = set_properties('headers')
        r.body = body()
        r.responses = set_properties('responses')
        r.protocols = __set_simple_property(r, 'protocols') or root.protocols
        r.media_types = __set_simple_property(r, 'body').keys() \
            or [root.media_type]
        r.description = description()

    return sorted_resources


#####
# RESOURCE TYPES
#####

#####
# SECURITY SCHEMES
#####

@validate
def _parse_security_schemes(raml, root):
    """
    Parsing of security schemes into SecurityScheme objects
    """
    def set_described_by():
        """Set describedBy attributes"""
        data = _s.data.get('describedBy', {})

        # TODO: move to validation
        if _s.type.startswith('x-') and not data:
            msg = ("Custom Authentication '{0}' requires 'describedBy' "
                   "attributes to be defined".format(_s.type))
            raise RAMLParserError(msg)

        properties = []

        for k in data.keys():
            props = __set_sec_property(_s, k)
            if props is not None:
                properties.extend(props)

        return properties or None

    def set_settings_attrs():
        """
        Set properties to SecurityScheme object depending on settings defined
        """
        if not _s.settings:
            return _s

        for k, v in iteritems(_s.settings):
            k = __pythonic_property_name(k)
            setattr(_s, k, v)

        return _s

    def add_properties_to_security_scheme(_s):
        """Add desc, type, settings, and described by attrs"""
        desc = __set_simple_property(_s, 'description')
        if desc:
            _s.description = Content(desc)
        else:
            _s.description = None
        _s.type = _s.data.get('type')
        _s.settings = _s.data.get('settings')  # TODO: add/pass thru validation
        _s.described_by = set_described_by()
        _s = set_settings_attrs()

        return _s

    schemes = raml.get('securitySchemes', [])
    ret = []
    for s in schemes:
        _s = SecurityScheme(list(s.keys())[0], list(s.values())[0])
        ret.append(add_properties_to_security_scheme(_s))

    return ret or None


def __map_secured_by_dict(secured, root):
    schemes = root.security_schemes or []

    scheme_names = [s.name for s in schemes]
    secured_name = list(iterkeys(secured))[0]
    if secured_name not in scheme_names:
        msg = "'{0}' is not defined in API Root's resourceTypes.".format(
            secured_name)
        raise RAMLParserError(msg)

    for s in schemes:
        if s.name == secured_name:
            return s


def __map_secured_by_list(secured, root):
    sec_objs = []
    for s in secured:
        if isinstance(s, str):
            sec_objs.append(__map_secured_by_str(s, root))
        elif isinstance(s, dict):
            sec_objs.append(__map_secured_by_dict(s, root))
        elif s is None:
            sec_objs.append(None)
        else:
            msg = "Error applying security scheme '{0}'.".format(secured)
            raise RAMLParserError(msg)

        return sec_objs


def __map_secured_by_str(secured, root):
    schemes = root.security_schemes or []
    scheme_names = [s.name for s in schemes]

    if secured not in scheme_names:
        msg = "'{0}' is not defined in API Root's resourceTypes.".format(
            secured)
        raise RAMLParserError(msg)

    for s in schemes:
        if s.name == secured:
            return s


def __convert_items(items, obj, **kw):
    return [obj(k, v, **kw) for k, v in iteritems(items)]


def __set_sec_property(scheme, k):
    prop = scheme.data.get('describedBy', {}).get(k, {})
    properties = []

    for i, j in iteritems(prop):
        obj = __map_obj(k)
        properties.append(obj(i, j, scheme))

    return properties
