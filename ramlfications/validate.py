#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function

__all__ = ["validate_raml", "InvalidRamlFileError"]

from .parser import APIRoot


VALID_RAML_VERSIONS = ["0.8"]


class InvalidRamlFileError(Exception):
    pass


# As valdiation does not require saved state, it's probably better
# to get rid of the class and just have a validate function.
class ValidateRAML(object):
    """
    Validate a particular RAML file based off of http://raml.org/spec.html
    """
    def __init__(self, load_object):
        # Document exceptions or even better change the code to not throw
        # Exceptions in the constructor.
        self.raml_file = load_object.raml_file
        self.api = APIRoot(load_object)

    def raml_header(self):
        """Validate Header of RAML File"""
        # Line below throws IOException which is neither caught nor
        # documented.
        # LR: The load_object will raise an error if there is no RAML file
        with open(self.raml_file, 'r') as r:
            # Line below might crash on empty files without any lines.
            raml_header = r.readline().split('\n')[0]
            raml_def, version = raml_header.split()
            if raml_def != "#%RAML":
                msg = "Not a valid RAML header: {0}.".format(raml_def)
                raise InvalidRamlFileError(msg)
            if version not in VALID_RAML_VERSIONS:
                msg = "Not a valid version of RAML: {0}.".format(version)
                raise InvalidRamlFileError(msg)

    def api_title(self):
        """Require an API Title."""
        title = self.api.title
        if not title:
            msg = 'RAML File does not define an API title.'
            raise InvalidRamlFileError(msg)

    # Is this function useful or are missing versions
    # already be caught in raml_header?
    def api_version(self):
        # TODO: require version for production; optional for development
        """Require an API Version."""
        if not self.api.version:
            msg = 'RAML File does not define an API version.'
            raise InvalidRamlFileError(msg)

    def base_uri(self):
        """Require a Base URI"""
        base_uri = self.api.base_uri
        if not base_uri:
            msg = 'RAML File does not define the baseUri.'
            raise InvalidRamlFileError(msg)

    def base_uri_params(self):
        """
        Require that Base URI Parameters have a `default` parameter set.
        """
        base_uri_params = self.api.base_uri_parameters
        if base_uri_params:
            for param in base_uri_params:
                if not param.default:
                    msg = "'{0}' needs a default parameter.".format(param.name)
                    raise InvalidRamlFileError(msg)

    def resource_response(self):
        resources = self.api.resources
        valid_keys = ['body', 'headers', 'description']
        for resource in list(resources.values()):
            responses = resource.responses
            for resp in responses:
                for key in list(resp.data.keys()):
                    if key not in valid_keys:
                        msg = "'{0}' not a valid Response parameter.".format(
                            key)
                        raise InvalidRamlFileError(msg)

    def root_documentation(self):
        docs = self.api.documentation
        if docs:
            for d in docs:
                if not d.title:
                    msg = "API Documentation requires a title."
                    raise InvalidRamlFileError(msg)
                if not d.content_raw:
                    msg = "API Documentation requires content defined."
                    raise InvalidRamlFileError(msg)

    def security_schemes(self):
        # QUESTION: Need to validate "other" schemas somehow? e.g. is
        # 'describedBy' for x-foo-auth needed?
        valid = ['OAuth 1.0',
                 'OAuth 2.0',
                 'Basic Authentication',
                 'Digest Authentication']
        schemes = self.api.security_schemes
        if schemes:
            for s in schemes:
                if s.type not in valid and not s.type.startswith("x-"):
                    msg = "'{0}' is not a valid Security Scheme.".format(
                        s.type)
                    raise InvalidRamlFileError(msg)

    def validate(self):
        """Validates RAML elements according to RAML specification"""
        self.raml_header()
        self.api_title()
        self.api_version()
        self.base_uri()
        self.base_uri_params()
        self.resource_response()
        self.root_documentation()
        self.security_schemes()


def validate(load_object):
    ValidateRAML(load_object).validate()
