#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function

__all__ = ["validate_raml", "InvalidRamlFileError"]

from .parser import APIRoot
from .loader import RAMLLoader


VALID_RAML_VERSIONS = ["0.8"]


class InvalidRamlFileError(Exception):
    pass


def validate_raml_header(raml_file):
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

            if version not in VALID_RAML_VERSIONS:
                msg = "Not a valid version of RAML: {0}.".format(version)
                raise InvalidRamlFileError(msg)
    except IOError as e:
        raise InvalidRamlFileError(e)


def validate_api_title(api):
    """Require an API Title."""
    if not api.title:
        msg = 'RAML File does not define an API title.'
        raise InvalidRamlFileError(msg)


def validate_api_version(api, prod=True):
    """Require an API Version (e.g. api.foo.com/v1)."""
    if prod and not api.version:
        msg = 'RAML File does not define an API version.'
        raise InvalidRamlFileError(msg)


def validate_base_uri(api):
    """Require a Base URI."""
    if not api.base_uri:
        msg = 'RAML File does not define the baseUri.'
        raise InvalidRamlFileError(msg)


def validate_base_uri_params(api):
    """
    Require that Base URI Parameters have a ``default`` parameter set.
    """
    base_uri_params = api.base_uri_parameters
    if base_uri_params:
        for param in base_uri_params:
            if not param.default:
                msg = "'{0}' needs a default parameter.".format(param.name)
                raise InvalidRamlFileError(msg)


def validate_resource_response(api):
    """
    Assert only ``body``, ``headers``, and ``description`` are keys
    defined for a ``Response``.
    """
    valid_keys = ['body', 'headers', 'description']
    for resource in list(api.resources.values()):
        for resp in resource.responses:
            for key in list(resp.data.keys()):
                if key not in valid_keys:
                    msg = "'{0}' not a valid Response parameter.".format(
                        key)
                    raise InvalidRamlFileError(msg)


def validate_root_documentation(api):
    """
    Assert that if there is ``documentation`` defined in the root of the
    RAML file, that it contains a ``title`` and ``content``.
    """
    docs = api.documentation
    if docs:
        for d in docs:
            if not d.title:
                msg = "API Documentation requires a title."
                raise InvalidRamlFileError(msg)
            if not d.content.raw:
                msg = "API Documentation requires content defined."
                raise InvalidRamlFileError(msg)


def validate_security_schemes(api):
    """
    Assert only valid Security Schemes are used.
    """
    valid = ['OAuth 1.0',
             'OAuth 2.0',
             'Basic Authentication',
             'Digest Authentication']
    schemes = api.security_schemes
    if schemes:
        for s in schemes:
            if s.type not in valid and not s.type.startswith("x-"):
                msg = "'{0}' is not a valid Security Scheme.".format(
                    s.type)
                raise InvalidRamlFileError(msg)


def validate_raml(raml_file, prod):
    validate_raml_header(raml_file)
    loader = RAMLLoader(raml_file)
    api = APIRoot(loader)
    validate_api_title(api)
    validate_api_version(api, prod)
    validate_base_uri(api)
    validate_base_uri_params(api)
    validate_resource_response(api)
    validate_root_documentation(api)
    validate_security_schemes(api)


## TODO:
#
# Resource validation:
#  - At least one resource *is* defined
#  - Body has valid Response Content Type keys
#  - Body has valid Schema
