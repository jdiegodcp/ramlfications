#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function

__all__ = ["InvalidRamlFileError"]

import re
import os

from functools import wraps

from six import itervalues, iteritems, iterkeys

from .base_config import config


class InvalidRamlFileError(Exception):
    pass


#####
# Decorator functions
#####

def validate(func):
    """
    Validate item according to RAML spec.
    """
    @wraps(func)
    def func_wrapper(raml, *args, **kw):
        validate = os.environ.get('RAML_VALIDATE') == '1'
        if not validate:
            validate = config.get('main', 'validate') == 'True'
        if validate:
            __map_to_validate_func(func.__name__)(raml, *args, **kw)
        return func(raml, *args, **kw)
    return func_wrapper


def validate_property(func):
    """
    Validate property for Trait, ResourceType, or Resource according to
    RAML spec
    """
    @wraps(func)
    def func_wrapper(resource, property, *args, **kw):
        validate = os.environ.get('RAML_VALIDATE') == '1'
        if validate is False:
            validate = config.get('main', 'validate')
        if validate is True:
            __map_to_validate_prop(property)(resource, *args, **kw)
        return func(resource, property, *args, **kw)
    return func_wrapper


#####
# Helper/mapping functions
####
def __map_to_validate_func(func_name):
    return {
        '_set_base_uri': __base_uri,
        '_set_version': __version,
        '_raml_header': __raml_header,
        '_set_title': __api_title,
        '_set_docs': __documentation,
        '_set_base_uri_params': __base_uri_params,
        '_set_schemas': __schemas,
        '_set_protocols': __protocols,
        '_set_media_type': __media_type,
        '_parse_security_schemes': __security_schemes,
        '_set_uri_params': __uri_params,
        '__get_resource_type': __resource_type,
        '__set_settings_dict': __security_settings,
        '__get_secured_by': __secured_by,
        '__add_properties_to_resources': __has_resources
    }[func_name]


def __map_to_validate_prop(property):
    return {
        'responses': __responses,
        'queryParameters': __query_params,
        'uriParameters': __uri_params_resource,
        'formParameters': __form_params,
        'headers': __headers,
        'body': __body,
        'description': __description,
        'mediaType': __media_type,
        'baseUriParameters': __base_uri_params_resource
    }[property]


#####
# API Metadata Validation
#####

def __base_uri(raml):
    """Require a Base URI."""
    if not raml.get('baseUri'):
        msg = 'RAML File does not define the baseUri.'
        raise InvalidRamlFileError(msg)


def __version(raml, **kw):
    prod = kw.get('prod')
    """Require an API Version (e.g. api.foo.com/v1)."""
    v = raml.get('version')
    if prod and not v:
        msg = 'RAML File does not define an API version.'
        raise InvalidRamlFileError(msg)
    elif '{version}' in raml.get('baseUri') and not v:
        msg = ("RAML File's baseUri includes {version} parameter but no "
               "version is defined.")
        raise InvalidRamlFileError(msg)


def __raml_header(raml_file):
    """Validate Header of RAML File"""
    try:
        with open(raml_file, 'r') as r:
            # Returns None if empty file lines
            raml_header = r.readline().split('\n')[0]
            if not raml_header:
                msg = ("RAML header empty. Please make sure the first line "
                       "of the file contains a valid RAML file definition.")
                raise InvalidRamlFileError(msg)

            try:
                raml_def, version = raml_header.split()
            except ValueError:
                msg = ("Not a valid RAML header: {0}.".format(raml_header))
                raise InvalidRamlFileError(msg)

            if raml_def != "#%RAML":
                msg = "Not a valid RAML header: {0}.".format(raml_def)
                raise InvalidRamlFileError(msg)

            if version not in config.get('defaults', 'raml_versions'):
                msg = "Not a valid version of RAML: {0}.".format(version)
                raise InvalidRamlFileError(msg)
    except IOError as e:
        raise InvalidRamlFileError(e)


def __api_title(raml):
    if not raml.get('title'):
        msg = 'RAML File does not define an API title.'
        raise InvalidRamlFileError(msg)


def __documentation(raml):
    """
    Assert that if there is ``documentation`` defined in the root of the
    RAML file, that it contains a ``title`` and ``content``.
    """
    docs = raml.get('documentation')
    if docs:
        for d in docs:
            if not d.get('title'):
                msg = "API Documentation requires a title."
                raise InvalidRamlFileError(msg)
            if not d.get('content'):
                msg = "API Documentation requires content defined."
                raise InvalidRamlFileError(msg)


def __base_uri_params(raml, *args, **kw):
    """
    Require that Base URI Parameters have a ``default`` parameter set.
    """
    base_uri_params = raml.get('baseUriParameters', {})
    for k, v in iteritems(base_uri_params):
        values = list(itervalues(v))
        if 'default' not in values:
            msg = ("The 'default' parameter is not set for base URI "
                   "parameter '{0}'".format(k))
            raise InvalidRamlFileError(msg)


def __schemas(raml):
    pass


def __protocols(raml, *args, **kw):
    protocols = raml.get('protocols')
    if protocols:
        for p in protocols:
            if p not in config.get('defaults', 'protocols'):
                msg = "'{0}' not a valid protocol for a RAML-defined API."
                raise InvalidRamlFileError(msg)


def __media_type(raml):
    media_type = raml.get('mediaType')
    if media_type:
        if media_type in config.get('defaults', 'media_types'):
            return
        regex_str = re.compile(r"application\/[A-Za-z.-0-1]*?(json|xml)")
        match = re.search(regex_str, media_type)
        if match:
            return
        else:
            msg = "Unsupported MIME Media Type: '{0}'.".format(media_type)
            raise InvalidRamlFileError(msg)


def __security_schemes(raml, *args, **kw):
    """
    Assert only valid Security Schemes are used.
    """

    schemes = raml.get('securitySchemes', {})
    schemes = [s.keys()[0] for s in schemes]
    if schemes:
        for s in schemes:
            if s not in config.get('custom', 'auth_schemes') and not s.startswith("x-"):
                msg = "'{0}' is not a valid Security Scheme.".format(s)
                raise InvalidRamlFileError(msg)


def __uri_params(raml, *args, **kw):
    uri_params = raml.get('uriParameters', {})
    for k in list(iterkeys(uri_params)):
        if k.lower() == 'version':
            msg = "'version' can only be defined in baseUriParameters."
            raise InvalidRamlFileError(msg)


#####
# Trait, ResourceType, and Resource validation
#####


def __responses(resource, *args, **kw):
    if hasattr(resource, 'method'):
        resp = resource.data.get(resource.method, {}).get('responses', {})
    elif hasattr(resource, 'orig_method'):
        resp = resource.data.get(resource.orig_method, {}).get('responses', {})
    else:
        resp = resource.data.get('responses', {})

    codes = list(iterkeys(resp))
    for code in codes:
        if code not in config.get('custom', 'resp_codes'):
            msg = "'{0}' not a valid response code.".format(code)
            raise InvalidRamlFileError(msg)
    for item in list(itervalues(resp)):
        body = item.get('body', {})
        __body_media_type(body)


def __query_params(resource, *args, **kw):
    resource_params = resource.data.get('queryParameters', {})
    if hasattr(resource, 'orig_method'):
        method_params = resource.data.get(resource.orig_method, {}).get(
            'queryParameters', {})
    elif hasattr(resource, 'method'):
        method_params = resource.data.get(resource.method, {}).get(
            'queryParameters', {})
    else:
        method_params = {}

    params = dict(list(method_params.items()) + resource_params.items())

    if params:
        __primative_parameter(params)


def __uri_params_resource(resource, *args, **kw):
    resource_params = resource.data.get('uriParameters', {})
    if hasattr(resource, 'orig_method'):
        method_params = resource.data.get(resource.orig_method, {}).get(
            'uriParameters', {})
    elif hasattr(resource, 'method'):
        method_params = resource.data.get(resource.method, {}).get(
            'uriParameters', {})
    else:
        method_params = {}

    params = dict(list(method_params.items()) + resource_params.items())

    if params:
        __primative_parameter(params)


def __form_params(resource, *args, **kw):
    resource_params = resource.data.get('formParameters', {})
    if hasattr(resource, 'orig_method'):
        method_params = resource.data.get(resource.orig_method, {}).get(
            'formParameters', {})
    elif hasattr(resource, 'method'):
        method_params = resource.data.get(resource.method, {}).get(
            'formParameters', {})
    else:
        method_params = {}

    params = dict(list(method_params.items()) + resource_params.items())

    if params:
        __primative_parameter(params)


def __headers(resource, *args, **kw):
    pass


def __body(resource, *args, **kw):
    if hasattr(resource, 'method'):  # resource
        body = resource.data.get(resource.method, {}).get('body', {})
    elif hasattr(resource, 'orig_method'):  # resource type
        body = resource.data.get(resource.orig_method, {}).get('body', {})
    else:  # trait
        body = resource.data.get('body', {})

    __body_media_type(body)


def __description(resource, *args, **kw):
    pass


def __base_uri_params_resource(resource, *args, **kw):
    pass


def __body_media_type(body):
    def check_type(media_type):
        if media_type in config.get('defaults', 'media_types'):
            return
        regex_str = re.compile(r"application\/[A-Za-z.-0-1]*?(json|xml)")
        match = re.search(regex_str, media_type)
        if match:
            return
        else:
            msg = "Unsupported MIME Media Type: '{0}'.".format(media_type)
            raise InvalidRamlFileError(msg)

    for k, v in iteritems(body):
        check_type(k)
        if k in ['application/x-www-form-urlencoded', 'multipart/form-data']:
            props = list(iterkeys(k))
            if 'schema' in props:
                msg = ("'schema' may not be specified when the body's media "
                       "type is application/x-www-form-urlencoded or "
                       "multipart/form-data.")
                raise InvalidRamlFileError(msg)


def __resource_type(resource, *args, **kw):
    if not resource.type:
        return
    if isinstance(resource.type, dict) or isinstance(resource.type, list):
        if len(resource.type) > 1:
            msg = "Too many resource types applied to '{0}'.".format(
                resource.name)
            raise InvalidRamlFileError(msg)


def __secured_by(resource, *args, **kw):
    if not resource.secured_by:
        return

    root = args[0]
    if not root.security_schemes:
        msg = ("No Security Schemes are defined in RAML file but '{0}' "
               "scheme is assigned to '{1}'.".format(resource.secured_by,
                                                     resource.name))
        raise InvalidRamlFileError(msg)

    for s in resource.secured_by:
        if isinstance(s, dict):
            scheme = s.keys()[0]
        else:
            scheme = s
        scheme_names = [r.name for r in root.security_schemes]
        if scheme not in scheme_names:
            msg = ("'{0}' is applied to '{1}' but is not defined in "
                   "the securitySchemes".format(scheme, resource.name))
            raise InvalidRamlFileError(msg)


#####
# Security Scheme validation
#####
def __security_settings(scheme, *args, **kw):
    settings = scheme.data.get('settings')
    if not settings:
        return

    attrs = settings.keys()

    if scheme.type == 'OAuth 2.0':
        oauth2_attrs = [
            'authorizationUri', 'accessTokenUri', 'authorizationGrants',
            'scopes'
        ]
        for attr in oauth2_attrs:
            if attr not in attrs:
                msg = ("Need to defined '{0}' in securitySchemas settings "
                       "for a valid OAuth 2.0 scheme".format(attr))
                raise InvalidRamlFileError(msg)

    if scheme.type == 'OAuth 1.0':
        oauth1_attrs = [
            'requestTokenUri', 'authorizationUri', 'tokenCredentialsUri'
        ]
        for attr in oauth1_attrs:
            if attr not in attrs:
                msg = ("Need to defined '{0}' in securitySchemas settings "
                       "for a valid OAuth 1.0 scheme".format(attr))
                raise InvalidRamlFileError(msg)


#####
# Parameter validation (Query, URI, Form)
#####
def __primative_parameter(parameter, *args, **kw):
    prim_type = parameter.values()[0].get('type')
    if prim_type not in config.get('defaults', 'prim_types') and prim_type is not None:
        msg = "'{0}' is not a valid primative parameter type".format(prim_type)
        raise InvalidRamlFileError(msg)


def __has_resources(resources, *args, **kw):
    """
    Require that RAML actually *defines* at least one Resource.
    """
    if not resources or len(resources) < 1:
        msg = "No resources are defined."
        raise InvalidRamlFileError(msg)



# def validate_raml(raml_file, prod):
#     """
#     Helper function to validate required elements of a RAML file.

#     :param str raml_file: string representing the path to the RAML file
#     :param bool prod: True/False if want to assert API is in production;
#         use ``False`` if just testing
#     :raises InvalidRamlFileError: Error when validating the RAML file
#     """
#     __raml_header(raml_file)
#     loader = RAMLLoader().load(raml_file)
#     api = parse_raml(loader)
#     __api_title(api)
#     __api_version(api, prod)
#     __base_uri(api)
#     __base_uri_params(api)
#     __has_resources(api)
#     __resource_response(api)
#     __root_documentation(api)
#     __security_schemes(api)


## TODO:
#
# Resource validation:
#  - At least one resource *is* defined
#  - Body has valid Response Content Type keys
#  - Body has valid Schema
#  - Body has a valid MIME media key/type
#  - Body does not have a schema defined if form
#  - ResourceType: only "?" is allowed in non-scalar properties
#    (e.g. usage & displayName)
