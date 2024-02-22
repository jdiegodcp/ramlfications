# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB

from __future__ import absolute_import, division, print_function


from ramlfications.errors import *  # NOQA

from .decorators import collecterrors
from .utils import validate_mime_type


#####
# Parameter Validators
#####
@collecterrors
def header_type(inst, attr, value):
    """Supported header type"""
    if value and value not in inst.config.get("prim_types"):
        msg = "'{0}' is not a valid primative parameter type".format(value)
        raise InvalidParameterError(msg, "header")


@collecterrors
def body_mime_type(inst, attr, value):
    """Supported MIME media type for request/response"""
    if value:
        match = validate_mime_type(value)
        if value not in inst.config.get("media_types") and not match:
            msg = "Unsupported MIME Media Type: '{0}'.".format(value)
            raise InvalidParameterError(msg, "body")


@collecterrors
def body_schema(inst, attr, value):
    """
    Assert no ``schema`` is defined if body as a form-related MIME media type
    """
    form_types = ["multipart/form-data", "application/x-www-form-urlencoded"]
    if inst.mime_type in form_types and value:
        msg = "Body must define formParameters, not schema/example."
        raise InvalidParameterError(msg, "body")


@collecterrors
def body_example(inst, attr, value):
    """
    Assert no ``example`` is defined if body as a form-related MIME media type
    """
    form_types = ["multipart/form-data", "application/x-www-form-urlencoded"]
    if inst.mime_type in form_types and value:
        msg = "Body must define formParameters, not schema/example."
        raise InvalidParameterError(msg, "body")


@collecterrors
def body_form(inst, attr, value):
    """
    Assert ``formParameters`` are defined if body has a form-related
    MIME type.
    """
    form_types = ["multipart/form-data", "application/x-www-form-urlencoded"]
    if inst.mime_type in form_types and not value:
        msg = "Body with mime_type '{0}' requires formParameters.".format(
            inst.mime_type)
        raise InvalidParameterError(msg, "body")


@collecterrors
def response_code(inst, attr, value):
    """
    Assert a valid response code.
    """
    if not isinstance(value, int):
        msg = ("Response code '{0}' must be an integer representing an "
               "HTTP code.".format(value))
        raise InvalidParameterError(msg, "response")
    if value not in inst.config.get("resp_codes"):
        msg = "'{0}' not a valid HTTP response code.".format(value)
        raise InvalidParameterError(msg, "response")


#####
# Primative Validators
#####
@collecterrors
def integer_number_type_parameter(inst, attr, value):
    """
    Assert correct parameter attributes for ``integer`` or ``number``
    primative parameter types.
    """
    if value is not None:
        param_types = ["integer", "number"]
        if inst.type not in param_types:
            msg = ("{0} must be either a number or integer to have {1} "
                   "attribute set, not '{2}'.".format(inst.name, attr.name,
                                                      inst.type))
            raise InvalidParameterError(msg, "BaseParameter")


@collecterrors
def string_type_parameter(inst, attr, value):
    """
    Assert correct parameter attributes for ``string`` primative parameter
    types.
    """
    if value:
        if inst.type != "string":
            msg = ("{0} must be a string type to have {1} "
                   "attribute set, not '{2}'.".format(inst.name, attr.name,
                                                      inst.type))
            raise InvalidParameterError(msg, "BaseParameter")
