#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function

import attr

from .validate import *  # NOQA

HTTP_METHODS = [
    "get", "post", "put", "delete", "patch", "options",
    "head", "trace", "connect"
]


@attr.s(repr=False)
class BaseParameter(object):
    name = attr.ib(repr=True)
    raw = attr.ib(validator=attr.validators.instance_of(dict))
    description = attr.ib()
    display_name = attr.ib()
    min_length = attr.ib(validator=string_type_parameter)
    max_length = attr.ib(validator=string_type_parameter)
    minimum = attr.ib(validator=integer_number_type_parameter)
    maximum = attr.ib(validator=integer_number_type_parameter)
    example = attr.ib()
    default = attr.ib()
    repeat = attr.ib(default=False)
    pattern = attr.ib(default=None, validator=string_type_parameter)
    enum = attr.ib(default=None, validator=string_type_parameter)
    param_type = attr.ib(default="string")

    def _map_type(self, param_type, name, raw):
        return {
            'string': "string",
            'integer': "integer",
            'number': "number",
            'boolean': "bool",
            'date': "date",
            'file': "file"
        }[param_type]

    @property
    def type(self):
        return self._map_type(self.param_type, self.name, raw=self.raw)


@attr.s(repr=False)
class URIParameter(BaseParameter):
    required = attr.ib(default=True)


@attr.s(repr=False)
class QueryParameter(BaseParameter):
    required = attr.ib(default=False)


@attr.s(repr=False)
class FormParameter(BaseParameter):
    required = attr.ib(default=False)


@attr.s()
class Documentation(object):
    title = attr.ib()
    content = attr.ib(repr=False)


@attr.s(repr=False)
class Header(object):
    name = attr.ib()
    display_name = attr.ib(repr=True)
    raw = attr.ib(validator=attr.validators.instance_of(dict))
    param_type = attr.ib(validator=header_type)
    description = attr.ib()
    example = attr.ib()
    default = attr.ib()
    min_length = attr.ib(validator=string_type_parameter)
    max_length = attr.ib(validator=string_type_parameter)
    minimum = attr.ib(validator=integer_number_type_parameter)
    maximum = attr.ib(validator=integer_number_type_parameter)
    enum = attr.ib(default=None, validator=string_type_parameter)
    repeat = attr.ib(default=False)
    pattern = attr.ib(default=None, validator=string_type_parameter)
    method = attr.ib(default=None)
    required = attr.ib(default=False)

    def _map_type(self, param_type, name, raw):
        return {
            'string': "string",
            'integer': "integer",
            'number': "number",
            'boolean': "bool",
            'date': "date",
            'file': "file"
        }[param_type]

    @property
    def type(self):
        return self._map_type(self.param_type, self.name, raw=self.raw)


@attr.s(repr=False)
class Body(object):
    mime_type = attr.ib(repr=True, init=True, validator=body_mime_type)
    raw = attr.ib(init=True, validator=attr.validators.instance_of(dict))
    schema = attr.ib(validator=body_schema)
    example = attr.ib(validator=body_example)
    form_params = attr.ib(validator=body_form)


@attr.s(repr=False)
class Response(object):
    code = attr.ib(repr=True, validator=response_code)
    raw = attr.ib(validator=attr.validators.instance_of(dict))
    description = attr.ib()
    headers = attr.ib()
    body = attr.ib()
    method = attr.ib(default=None)


@attr.s(repr=False)
class SecurityScheme(object):
    name = attr.ib(repr=True)
    raw = attr.ib(validator=attr.validators.instance_of(dict))
    type = attr.ib()
    described_by = attr.ib(validator=attr.validators.instance_of(dict))
    description = attr.ib()
    settings = attr.ib(validator=attr.validators.instance_of(dict))
