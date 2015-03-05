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


@attr.s
class BaseParameter(object):
    name         = attr.ib()
    raw          = attr.ib(repr=False,
                           validator=attr.validators.instance_of(dict))
    description  = attr.ib(repr=False)
    display_name = attr.ib(repr=False)
    min_length   = attr.ib(repr=False, validator=string_type_parameter)
    max_length   = attr.ib(repr=False, validator=string_type_parameter)
    minimum      = attr.ib(repr=False, validator=integer_number_type_parameter)
    maximum      = attr.ib(repr=False, validator=integer_number_type_parameter)
    example      = attr.ib(repr=False)
    default      = attr.ib(repr=False)
    repeat       = attr.ib(repr=False, default=False)
    pattern      = attr.ib(repr=False, default=None,
                           validator=string_type_parameter)
    enum         = attr.ib(repr=False, default=None,
                           validator=string_type_parameter)
    type         = attr.ib(repr=False, default="string")


@attr.s
class URIParameter(BaseParameter):
    required = attr.ib(repr=False, default=True)


@attr.s
class QueryParameter(BaseParameter):
    required = attr.ib(repr=False, default=False)


@attr.s(repr=False)
class FormParameter(BaseParameter):
    required = attr.ib(repr=False, default=False)


@attr.s
class Documentation(object):
    title = attr.ib()
    content = attr.ib(repr=False)


@attr.s
class Header(object):
    name         = attr.ib(repr=False)
    display_name = attr.ib()
    raw          = attr.ib(repr=False,
                           validator=attr.validators.instance_of(dict))
    description  = attr.ib(repr=False)
    example      = attr.ib(repr=False)
    default      = attr.ib(repr=False)
    min_length   = attr.ib(repr=False, validator=string_type_parameter)
    max_length   = attr.ib(repr=False, validator=string_type_parameter)
    minimum      = attr.ib(repr=False, validator=integer_number_type_parameter)
    maximum      = attr.ib(repr=False, validator=integer_number_type_parameter)
    type         = attr.ib(repr=False, default="string", validator=header_type)
    enum         = attr.ib(repr=False, default=None,
                           validator=string_type_parameter)
    repeat       = attr.ib(repr=False, default=False)
    pattern      = attr.ib(repr=False, default=None,
                           validator=string_type_parameter)
    method       = attr.ib(repr=False, default=None)
    required     = attr.ib(repr=False, default=False)


@attr.s
class Body(object):
    mime_type   = attr.ib(init=True, validator=body_mime_type)
    raw         = attr.ib(repr=False, init=True,
                          validator=attr.validators.instance_of(dict))
    schema      = attr.ib(repr=False, validator=body_schema)
    example     = attr.ib(repr=False, validator=body_example)
    form_params = attr.ib(repr=False, validator=body_form)


@attr.s
class Response(object):
    code        = attr.ib(validator=response_code)
    raw         = attr.ib(repr=False, init=True,
                          validator=attr.validators.instance_of(dict))
    description = attr.ib(repr=False)
    headers     = attr.ib(repr=False)
    body        = attr.ib(repr=False)
    method      = attr.ib(default=None)


@attr.s
class SecurityScheme(object):
    name         = attr.ib()
    raw          = attr.ib(repr=False, init=True,
                           validator=attr.validators.instance_of(dict))
    type         = attr.ib(repr=False)
    described_by = attr.ib(repr=False,
                           validator=attr.validators.instance_of(dict))
    description  = attr.ib(repr=False)
    settings     = attr.ib(repr=False,
                           validator=attr.validators.instance_of(dict))
