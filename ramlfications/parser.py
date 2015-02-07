# ! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function


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
from .validate import validate, validate_item, validate_property


__all__ = ["RAMLParserError", "parse_raml"]


#####
# Main parser function from which __init__:parse calls
#####
def parse_raml(loaded_raml, production):
    """
    Parses the given RAML file and creates a :py:class:`.raml.RAMLRoot` object.

    :param ramlfications.loader.RAMLDict loaded_raml: Loaded RAML file
    :return: Parsed RAML file
    :rtype: RAMLRoot
    :raises RAMLParserError: If error occurred during parsing of the
        RAML file.
    """
    raml = loaded_raml.data
    root = RAMLRoot(loaded_raml)
    root = _parse_metadata(raml, root, production)
    root.security_schemes = _parse_security_schemes(raml, root)
    root.traits = _parse_traits(raml, root)
    root.resource_types = _parse_resource_types(raml, root)
    root.resources = _parse_resources(raml, root)

    return root


#####
# API Metadata
#####
# TODO: logic for production variable re: version
def _parse_metadata(raml, root, production=False):
    """Set Metadata for API"""
    @validate(raml)
    def base_uri():
        base_uri = raml.get('baseUri')
        if "{version}" in base_uri:
            base_uri = base_uri.replace('{version}', str(raml.get('version')))
        return base_uri

    @validate(raml)
    def protocols():
        explicit_protos = raml.get('protocols')

        implicit_protos = re.findall(r"(https|http)", root.base_uri)

        return explicit_protos or implicit_protos or None

    @validate(raml)
    def docs():
        d = raml.get('documentation', [])
        docs = [Documentation(i.get('title'), i.get('content')) for i in d]
        return docs or None

    @validate(raml)
    def base_uri_params():
        base_uri_params = raml.get('baseUriParameters', {})
        uri_params = []
        for k, v in list(base_uri_params.items()):
            uri_params.append((URIParameter(k, v, root)))
        return uri_params or None

    @validate(raml)
    def uri_params():
        uri_params = raml.get('uriParameters', {})
        params = []
        for k, v in list(uri_params.items()):
            params.append((URIParameter(k, v, root)))
        return params or None

    @validate(raml)
    def title():
        return raml.get('title')

    @validate(raml)
    def version():
        return raml.get('version')

    @validate(raml)
    def schemas():
        return raml.get('schemas')

    @validate(raml)
    def media_type():
        return raml.get('mediaType')

    @validate(root.raml_file)
    def __raml_header():
        pass

    @validate(raml)
    def __has_resources():
        pass

    __raml_header()
    __has_resources()
    root.title = title()
    root.base_uri = base_uri()
    root.version = version()
    root.base_uri_params = base_uri_params()
    root.protocols = protocols()
    root.documentation = docs()
    root.schemas = schemas()
    root.media_type = media_type()
    root.uri_params = uri_params()

    return root


#####
# RESOURCES
#####

# Logic for parsing of Resources/endpoints into Resource objects
def _parse_resources(raml, root):
    resources = __traverse(raml, [], root, parent=None)
    resources = __add_properties_to_resources(resources, root)
    return resources


def __traverse(node, resources, root, parent):
    for k, v in node.iteritems():
        if k.startswith("/"):
            avail = config.get('defaults', 'available_methods')
            methods = [m for m in avail if m in v.keys()]
            if methods:
                for m in methods:
                    child = Resource(name=k, data=v, method=m,
                                     parent=parent, api=root)
                    resources.append(child)
            else:
                child = Resource(name=k, data=v, method=None,
                                 parent=parent, api=root)
                resources.append(child)
            resources = __traverse(child.data, resources, root, child)
    return resources


def __add_properties_to_resources(resources, root):

    validation = "resource"

    @validate_property(validation)
    def _is():
        resource_level = r.data.get('is', [])
        resource_method = r.data.get(r.method, [])
        if resource_method:
            method_level = resource_method.get('is', [])
        else:
            method_level = []

        trait_names = []

        all_is = resource_level + method_level

        for item in all_is:
            if isinstance(item, str):
                trait_names.append(item)
            elif isinstance(item, dict):
                trait_names.append(list(iterkeys(item))[0])
            elif isinstance(item, list):
                for t in item:
                    trait_names.append(t)

        return trait_names or None

    # TODO: this only checks resource-level defined "is", not method-level
    # TODO: the "else" should actually be caught in _is()
    @validate_property(validation)
    def traits():
        try:
            method_level = r.data.get(r.method).get('is', [])
        except AttributeError:
            method_level = None
        resource_level = r.data.get('is', [])
        if not method_level and not resource_level:
            return
        if root.traits is None:
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
                str_trait = __map_item_str(root.traits, trait)
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

    @validate_property(validation)
    def _type():
        resource_type = r.data.get('type')
        if resource_type:
            if isinstance(resource_type, dict):
                type_name = list(iterkeys(resource_type))[0]
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

        for r_ in api_resources:
            if r_.name == _type and r_.method == r.method:
                _values = list(r.type.values())[0]
                data = json.dumps(r_.data)
                for k, v in iteritems(_values):
                    data = __fill_params(data, k, v, r)
                data = json.loads(data)
                return ResourceType(r_.name, data, r.method, root, r.type)
        return None

    # TODO: move the RAMLParserError to validate (??)
    @validate_property(validation)
    def resource_type():
        mapped_res_type = None
        if not r.type:
            return

        if isinstance(r.type, str):
            mapped_res_type = __map_resource_string()

        elif isinstance(r.type, dict):
            mapped_res_type = __map_resource_dict()

        else:
            msg = "Error applying resource type '{0}'' to '{1}'.".format(
                r.type, r.name)
            raise RAMLParserError(msg)
        return mapped_res_type

    def __get_union(resource, inherited_resource):
        """
        Return the union of a particular :py:class:`raml.ResourceType`
        and its inherited :py:class:`raml.ResourceType`.
        """
        if inherited_resource is {}:
            return resource
        union = {}
        if not resource:
            return inherited_resource
        for k, v in iteritems(inherited_resource):
            if k not in resource.data.keys():
                union[k] = v
            else:
                resource_values = resource.data.get(k)
                inherited_values = inherited_resource.get(k, {})
                union[k] = dict(iteritems(inherited_values) +
                                iteritems(resource_values))
        for k, v in iteritems(resource.data):
            if k not in inherited_resource.keys():
                union[k] = v
        return union

    def __get_inherited_resource(res_name, raml):
        """
        Helper function to return data dict of particular resourceType
        """
        res_types = raml.get('resourceTypes')
        for t in res_types:
            if list(iterkeys(t))[0] == res_name:
                return t
        return None

    def __map_inherited_resource_types(root, resource, inherited, raml):
        """
        Grab elements if :py:class:`raml.ResourceType` inherits from
        another resource type.
        """
        resources = []
        inherited_res = __get_inherited_resource(inherited, raml)
        for k, v in iteritems(resource.data):
            if k in config.get('defaults', 'http_methods'):
                data = __get_union(resource,
                                   inherited_res.values()[0].get(k, {}))
                resources.append(Resource(resource.name, data, k, root))
        return resources

    def __map_secured_by_dict(secured):
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

    def __map_secured_by_list(secured):
        sec_objs = []
        for s in secured:
            if isinstance(s, str):
                sec_objs.append(__map_item_str(root.security_schemes, s))
            elif isinstance(s, dict):
                sec_objs.append(__map_secured_by_dict(s))
            elif s is None:
                sec_objs.append(None)
            else:
                msg = "Error applying security scheme '{0}'.".format(secured)
                raise RAMLParserError(msg)

            return sec_objs

    @validate_property(validation)
    def security_schemes():
        """
        Mapping of securitySchemes to its Resource/Resource Type
        """
        try:
            method_level = r.data.get(r.method, {}).get('securedBy', {})
        except AttributeError:
            method_level = None
        resource_level = r.data.get('securedBy', {})
        if not resource_level and not method_level:
            return

        if method_level:
            secured = method_level
        else:
            secured = resource_level

        _secured = []

        if secured is None:
            _secured.append(None)
        elif isinstance(secured, dict):
            sec_obj = __map_secured_by_dict(secured)
            _secured.append(sec_obj)
        elif isinstance(secured, list):
            sec_obj = __map_secured_by_list(secured)
            _secured.extend(sec_obj)
        elif isinstance(secured, str):
            sec_obj = __map_item_str(root.security_schemes, secured)
            _secured.append(sec_obj)
        else:
            msg = "Error applying security scheme '{0}' to '{1}'.".format(
                secured, r.name)
            raise RAMLParserError(msg)

        return _secured

    @validate_property(validation)
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

    @validate_item
    def set_properties(r, property, inherit=False):
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

    # TODO: improve @validate_item since i'm pasing in r & property
    # and I think it's unnecessary
    @validate_item
    def body(r, property):
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
    @validate_item
    def description(r, property):
        ret = None
        desc = __set_simple_property(r, 'description')
        if desc:
            if isinstance(desc, Content):
                assigned_desc = __fill_params(desc.raw, None, None, r)
            else:
                assigned_desc = __fill_params(desc, None, None, r)
            ret = Content(assigned_desc)
        return ret

    def wrap(r):
        r.is_ = _is()
        r.traits = traits()
        r.type = _type()
        r.resource_type = resource_type()
        r.secured_by = secured_by()
        r.security_schemes = security_schemes()
        r.display_name = r.data.get('displayName', r.name)
        r.base_uri_params = set_properties(r,
                                           'baseUriParameters',
                                           inherit=True)
        r.query_params = set_properties(r, 'queryParameters')
        r.uri_params = set_properties(r, 'uriParameters', inherit=True)
        r.form_params = set_properties(r, 'formParameters')
        r.headers = set_properties(r, 'headers')
        r.body = body(r, 'body')
        r.responses = set_properties(r, 'responses')
        r.protocols = __set_simple_property(r, 'protocols') or root.protocols
        r.media_types = __set_simple_property(r, 'body').keys() \
            or [root.media_type]
        r.description = description(r, 'description')

        return r

    def __union_is(r):
        if r.resource_type.is_:
            return list(set(r.is_ + r.resource_type.is_))

    def __union_base_uri_params(r):
        if r.resource_type.base_uri_params:
            return list(set(r.base_uri_params +
                        r.resource_type.base_uri_params))

    def __union(r, attr):
        if getattr(r.resource_type, attr):
            if not getattr(r, attr):
                return getattr(r.resource_type, attr)
            r_attr = getattr(r, attr)
            r_type_attr = getattr(r.resource_type, attr)
            return list(set(r_attr + r_type_attr))

    def wrap_res_types(r):
        if r.resource_type:
            # r.is_ = __union_is(r)
            # r.base_uri_params = __union_base_uri_params(r)
            # r.body += r.resource_type.body
            # r.data = __get_union(r, r.resource_type)
            # r.description += r.resource_type.description
            # r.form_params += r.resource_type.form_params
            # r.headers += r.resource_type.headers
            # r.media_types += r.resource_type.media_types
            # r.protocols = set(r.protocols + r.resource_type.protocols)
            # r.query_params += r.resource_type.query_params
            # r.responses += r.resource_type.responses
            # r.secured_by += r.resource_type.secured_by
            # r.security_schemes += r.resource_type.security_schemes
            # r.traits += r.resource_type.traits
            # r.headers = __union(r, 'headers')
            r.uri_params = __union(r, 'uri_params')
            # r.responses = __union(r, 'responses')

        return r

    res = [wrap(r) for r in resources]
    updated_res = [wrap_res_types(r) for r in res]

    return updated_res


#####
# RESOURCE TYPES
#####
def _parse_resource_types(raml, root):
    """
    Parsing of resourceTypes into ResourceType objects
    """
    validation = "resource_types"

    @validate_property(validation)
    def _is():
        """
        Return trait names associated with :py:class:`ResourceType` object
        """
        resource_traits = r.data.get('is', [])
        method_traits = r.data.get(r.orig_method, {}).get('is', [])

        traits = resource_traits + method_traits
        if traits:
            defined_traits = root.traits
            available_traits = [t for t in defined_traits if t.name in traits]

            if available_traits:
                return traits
        return None

    # TODO: I don't think this works properly...
    @validate_property(validation)
    def traits():
        """
        Return :py:class:`raml.Trait` objects associated with
        :py:class:`raml.ResourceType` object
        """

        resource_level = r.data.get('is', [])
        method_level = r.data.get(r.orig_method, {}).get('is', [])
        if not resource_level and not method_level:
            return

        if not root.traits:
            msg = ("No traits are defined in RAML file but '{0}' trait is "
                   "assigned to '{1}'.".format((resource_level, method_level),
                                               r.name))
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
                str_trait = __map_item_str(root.traits, trait)
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

    @validate_item
    def set_property(r, property, inherit=False):
        """
        Set property to :py:class:`raml.ResourceType`
        """
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

    @validate_property(validation)
    def type_secured_by():
        """
        Return string name of security scheme
        """
        method_sec = r.data.get(r.orig_method, {}).get('securedBy')
        if method_sec:
            return method_sec
        resource_sec = r.data.get('securedBy')
        if resource_sec:
            return resource_sec
        if hasattr(r, 'parent'):
            if hasattr(r.parent, 'secured_by'):
                return r.parent.secured_by
        return None

    @validate_property(validation)
    def security_schemes():
        """
        Return :py:class:`parameters.SecurityScheme` objects
        """
        if not r.data.get('securedBy'):
            return

        _secured_by = []
        for secured in r.data.get('securedBy'):
            if secured is None:
                _secured_by.append(None)
            elif isinstance(secured, list) or \
                isinstance(secured, dict) or \
                    isinstance(secured, str):
                    _secured_by.append(secured)
            else:
                msg = "Error applying security scheme '{0}' to '{1}'.".format(
                    secured, r.name)
                raise RAMLParserError(msg)

        return _secured_by

    def __get_union(resource, method, inherited_resource):
        """
        Return the union of a particular :py:class:`raml.ResourceType`
        and its inherited :py:class:`raml.ResourceType`.
        """
        if inherited_resource is {}:
            return resource
        union = {}
        if not resource:
            return inherited_resource
        for key, value in iteritems(inherited_resource):
            keys = resource.get(i, [])
            if keys is not None and key not in keys:
                union[key] = value
            else:
                resource_values = resource.get(i, {}).get(key, {})
                inherited_values = inherited_resource.get(key, {})
                union[key] = dict(inherited_values.items() +
                                  resource_values.items())
        for key, val in iteritems(resource):
            if key not in inherited_resource.keys():
                union[key] = value
        return union

    def __get_inherited_resource(res_name, raml):
        """
        Helper function to return data dict of particular resourceType
        """
        res_types = raml.get('resourceTypes')
        for t in res_types:
            if list(iterkeys(t))[0] == res_name:
                return t
        return None

    def __map_inherited_resource_types(root, resource, inherited, raml):
        """
        Grab elements if :py:class:`raml.ResourceType` inherits from
        another resource type.
        """
        resources = []
        inherited_res = __get_inherited_resource(inherited, raml)
        for k, v in iteritems(resource):
            for i in v.keys():
                if i in config.get('defaults', 'http_methods'):
                    data = __get_union(v, i,
                                       inherited_res.values()[0].get(i, {}))
                    resources.append(ResourceType(k, data, i, root,
                                                  type=inherited))
        return resources

    def wrap(r):
        """
        Set attrs to :py:class:`ResourceType`
        """
        r.is_ = _is()
        r.traits = traits()
        r.security_schemes = security_schemes()
        r.secured_by = type_secured_by()
        r.usage = r.data.get('usage')
        r.query_params = set_property(r, 'queryParameters')
        r.uri_params = set_property(r, 'uriParameters')
        r.base_uri_params = set_property(r, 'baseUriParameters')
        r.form_params = set_property(r, 'formParameters')
        r.headers = set_property(r, 'headers')
        r.body = set_property(r, 'body')
        r.responses = set_property(r, 'responses')
        r.protocols = __set_simple_property(r, 'protocols') or root.protocols
        r.media_types = __set_simple_property(r, 'body').keys() or None

        desc = __set_simple_property(r, 'description')
        if desc:
            r.description = Content(desc)
        else:
            r.description = None

        return r

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

    return [wrap(r) for r in resources] or None


#####
# Traits
#####

def _parse_traits(raml, root):
    @validate_item
    def set_property(t, property, inherit=False):
        """
        Set property to :py:class:`raml.Trait`
        """
        properties = []

        resource = t.data.get(property, {})
        for k, v in iteritems(resource):
            obj = __map_obj(property)
            properties.append(obj(k, v, t))

        if inherit:
            item = __map_item_type(property)
            if hasattr(t.parent, item):
                if getattr(t.parent, item) is not None:
                    properties.extend(getattr(t.parent, item))

        return properties or None

    def wrap(t):
        """
        Set attrs to :py:class:`raml.Trait`
        """
        t.usage = t.data.get('usage')
        t.query_params = set_property(t, 'queryParameters')
        t.uri_params = set_property(t, 'uriParameters')
        t.form_params = set_property(t, 'formParameters')
        t.headers = set_property(t, 'headers')
        t.body = set_property(t, 'body')
        t.responses = set_property(t, 'responses')
        t.description = t.data.get('description')
        t.media_types = t.data.get('body')

        return t

    raw_traits = raml.get('traits')

    if raw_traits:
        traits = [Trait(list(t.keys())[0],
                        list(t.values())[0], root) for t in raw_traits]

        return [wrap(t) for t in traits]

    return None


#####
# SECURITY SCHEMES
#####
def _parse_security_schemes(raml, root):
    """
    Parsing of security schemes into SecurityScheme objects
    """
    validation = 'security_schemes'

    # TODO: validate
    def set_sec_property(k):
        """
        Return a list of RAML file-defined properties for a
        :py:class:`.parameters.SecurityScheme`
        """
        prop = scheme.data.get('describedBy', {}).get(k, {})
        properties = []

        for i, j in iteritems(prop):
            obj = __map_obj(k)
            properties.append(obj(i, j, scheme))

        return properties

    # TODO: validate
    def set_described_by():
        """
        Set describedBy attributes
        """
        data = scheme.data.get('describedBy', {})

        # TODO: move to validation
        if scheme.type.startswith('x-') and not data:
            msg = ("Custom Authentication '{0}' requires 'describedBy' "
                   "attributes to be defined".format(scheme.type))
            raise RAMLParserError(msg)

        properties = []

        for k in data.keys():
            props = set_sec_property(k)
            if props is not None:
                properties.extend(props)

        return properties or None

    @validate_property(validation)
    def set_settings_attrs(scheme):
        """
        Set properties to SecurityScheme object depending on settings defined
        """
        if not scheme.settings:
            return scheme

        for k, v in iteritems(scheme.settings):
            k = __pythonic_property_name(k)
            setattr(scheme, k, v)

        return scheme

    def wrap(scheme):
        """Add desc, type, settings, and described by attrs"""
        desc = __set_simple_property(scheme, 'description')
        if desc:
            scheme.description = Content(desc)
        else:
            scheme.description = None
        scheme.type = scheme.data.get('type')
        # TODO: add/pass thru validation
        scheme.settings = scheme.data.get('settings')
        scheme.described_by = set_described_by()
        scheme = set_settings_attrs(scheme)

        return scheme

    schemes = raml.get('securitySchemes', [])
    ret = []
    for s in schemes:
        scheme = SecurityScheme(list(s.keys())[0], list(s.values())[0])
        ret.append(wrap(scheme))

    return ret or None


#####
# Util functions
#####

def __map_obj(property):
    """
    Map property name to appropriate RAML object.

    :param str property: property name
    :returns: property object
    """
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
    """
    Map RAML property item name to Python object property.

    :param str item: item name as set in RAML file
    :returns: item name as defined in appropriate Python object
    """
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
    """
    Return snake-case of a not-yet-known property name defined in RAML file.

    e.g. `fooBarBaz` will return `foo_bar_baz`

    :param str property: property name as set in RAML file
    :returns: snake-case of property name.
    """
    ret = ''

    for char in property:
        if char.islower():
            ret += char
        else:
            ret += '_'
            ret += char.lower()

    return ret


def __get_traits_dict(trait, root, resource):
    """
    Giving the string name of a trait, returns :py:class:`raml.Trait`
    object with parameters filled in.

    :param str trait: trait name
    :param RAMLRoot root: :py:class:`raml.RAMLRoot` object
    :param Resource resource: :py:class:`raml.Resource` object
    :returns: :py:class:`Trait` object or `None`
    """
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
    """
    Returns the value of a property.  Used when values are known to be
    strings

    :param r: Either :py:class:`raml.Resource`, \
        :py:class:`raml.ResourceType`, or :py:class:`raml.Trait`
    :returns: value of requested property
    :rtype: str
    """
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
    """
    Fill in parameters defined in RAML file
    :param str string: string to edit/replace with parameter
    :param str key: name of the parameter to replace
    :param str value: value to replace the key with
    :param Resource resource: :py:class:`Resource` object with which the
        `string` is associated

    :returns: edited string with filled-in params
    """
    if key:
        string = string.replace("<<" + key + ">>", str(value))
    string = fill_reserved_params(resource, string)
    return string


def __map_item_str(items, item):
    """
    Maps an item name to its associated Python object

    :param list items: list of Python objects
    :param str item: item name
    :returns: Python object of item
    """
    item_names = [i.name for i in items]

    if item not in item_names:
        msg = "'{0}' is not defined in its respective API Root."
        raise RAMLParserError(msg)

    for i in items:
        if i.name == item:
            return i

    return None
