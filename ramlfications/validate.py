#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from parser import APIRoot


VALID_RAML_VERSIONS = ["0.8"]


class RAMLValidationError(Exception):
    pass


class ValidateRAML(object):
    def __init__(self, raml_file):
        self.raml_file = raml_file
        self.api = APIRoot(raml_file)

    def raml_header(self):
        with open(self.raml_file, 'r') as r:
            raml_header = r.readline().split('\n')[0]
            raml_def, version = raml_header.split()
            if raml_def != "#%RAML":
                msg = "Not a valid RAML header: {0}.".format(raml_def)
                raise RAMLValidationError(msg)
            if version not in VALID_RAML_VERSIONS:
                msg = "Not a valid version of RAML: {0}.".format(version)
                raise RAMLValidationError(msg)

    def api_title(self):
        title = self.api.title
        if not title:
            msg = 'RAML File does not define an API title.'
            raise RAMLValidationError(msg)

    def base_uri(self):
        base_uri = self.api.base_uri
        if not base_uri:
            msg = 'RAML File does not define the baseUri.'
            raise RAMLValidationError(msg)

    def base_uri_params(self):
        base_uri_params = self.api.base_uri_parameters
        if base_uri_params:
            for param in base_uri_params:
                if not param.default:
                    msg = '{0} needs a default parameter.'.format(param.name)
                    raise RAMLValidationError(msg)

    def node_response(self):
        nodes = self.api.nodes
        valid_keys = ['body', 'headers', 'description']
        for node in list(nodes.values()):
            responses = node.responses
            for resp in responses:
                for key in list(resp.data.keys()):
                    if key not in valid_keys:
                        msg = "{0} not a valid Response parameter.".format(key)
                        raise RAMLValidationError(msg)

    def root_documentation(self):
        docs = self.api.documentation
        if docs:
            for d in docs:
                if not d.title:
                    msg = "API Documentation requires a title."
                    raise RAMLValidationError(msg)
                if not d.content:
                    msg = "API Documentation requires content defined."
                    raise RAMLValidationError(msg)

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
                    raise RAMLValidationError(msg)

    def validate(self):
        self.raml_header()
        self.api_title()
        self.base_uri()
        self.base_uri_params()
        self.node_response()
        self.root_documentation()
        self.security_schemes()


def validate(ramlfile):
    ValidateRAML(ramlfile).validate()
