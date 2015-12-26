# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function

import re

from six import iterkeys

from .utils._decorators import collecterrors

from .errors import *  # NOQA


#####
# RAMLRoot validators
#####

@collecterrors
def root_version(inst, attr, value):
    """Require an API Version (e.g. api.foo.com/v1)."""
    base_uri = inst.raml_obj.get("baseUri")
    if base_uri and "{version}" in base_uri and not value:
        msg = ("RAML File's baseUri includes {version} parameter but no "
               "version is defined.")
        raise InvalidRootNodeError(msg)


@collecterrors
def root_base_uri(inst, attr, value):
    """Require a Base URI."""
    if not value:
        msg = "RAML File does not define the baseUri."
        raise InvalidRootNodeError(msg)


@collecterrors
def root_base_uri_params(inst, attr, value):
    """
    Require that Base URI parameters have a ``default`` parameter set.
    """
    if value:
        for v in value:
            if v.type != "string":
                msg = ("baseUriParameter '{0}' must be a "
                       "string".format(v.name))
                raise InvalidRootNodeError(msg)
            if v.required is False:
                msg = ("baseUriParameter '{0}' must be "
                       "required".format(v.name))
                raise InvalidRootNodeError(msg)


@collecterrors
def root_uri_params(inst, attr, value):
    """
    Assert that where is no ``version`` parameter in the regular URI parameters
    """
    if value:
        for v in value:
            if v.name == "version":
                msg = "'version' can only be defined in baseUriParameters."
                raise InvalidRootNodeError(msg)


@collecterrors
def root_protocols(inst, attr, value):
    """
    Only support HTTP/S plus what is defined in user-config
    """
    if value:
        for p in value:
            if p.upper() not in inst.config.get("protocols"):
                msg = ("'{0}' not a valid protocol for a RAML-defined "
                       "API.".format(p))
                raise InvalidRootNodeError(msg)


@collecterrors
def root_title(inst, attr, value):
    """
    Require a title for the defined API.
    """
    if not value:
        msg = "RAML File does not define an API title."
        raise InvalidRootNodeError(msg)


@collecterrors
def root_docs(inst, attr, value):
    """
    Assert that if there is ``documentation`` defined in the root of the
    RAML file, that it contains a ``title`` and ``content``.
    """
    if value:
        for d in value:
            if d.title.raw is None:
                msg = "API Documentation requires a title."
                raise InvalidRootNodeError(msg)
            if d.content.raw is None:
                msg = "API Documentation requires content defined."
                raise InvalidRootNodeError(msg)


# TODO: finish
@collecterrors
def root_schemas(inst, attr, value):
    pass


@collecterrors
def root_media_type(inst, attr, value):
    """
    Only support media types based on config and regex
    """
    if value:
        match = validate_mime_type(value)
        if value not in inst.config.get("media_types") and not match:
            msg = "Unsupported MIME Media Type: '{0}'.".format(value)
            raise InvalidRootNodeError(msg)


@collecterrors
def root_resources(inst, attr, value):
    if not value:
        msg = "API does not define any resources."
        raise InvalidRootNodeError(msg)


@collecterrors
def root_secured_by(inst, attr, value):
    pass


#####
# Security Scheme Validators
#####
@collecterrors
def defined_sec_scheme_settings(inst, attr, value):
    """Assert that ``settings`` are defined/not an empty map."""
    if not value:
        msg = ("'settings' for security scheme '{0}' require "
               "definition.".format(inst.name))
        raise InvalidSecuritySchemeError(msg)


#####
# ResourceType validators
#####
@collecterrors
def defined_resource_type(inst, attr, value):
    """
    Assert that a resource type is defined (e.g. not an empty map) or is
    inherited from a defined resource type.
    """
    if not inst.type:
        if not value:
            msg = ("The resourceType '{0}' requires "
                   "definition.".format(inst.name))
            raise InvalidResourceNodeError(msg)


#####
# Trait validators
#####
@collecterrors
def defined_trait(inst, attr, value):
    """Assert that a trait is defined (e.g. not an empty map)."""
    if not value:
        msg = "The trait '{0}' requires definition.".format(inst.name)
        raise InvalidResourceNodeError(msg)


#####
# Shared Validators for Resource & Resource Type Node
#####
@collecterrors
def assigned_traits(inst, attr, value):
    """
    Assert assigned traits are defined in the RAML Root and correctly
    represented in the RAML.
    """
    if value:
        traits = inst.root.raw.get("traits", {})
        if not traits:
            msg = ("Trying to assign traits that are not defined"
                   "in the root of the API.")
            raise InvalidResourceNodeError(msg)
        trait_names = [list(iterkeys(i))[0] for i in traits]
        if not isinstance(value, list):
            msg = ("The assigned traits, '{0}', needs to be either an array "
                   "of strings or dictionaries mapping parameter values to "
                   "the trait".format(value))
            raise InvalidResourceNodeError(msg)
        if isinstance(value, list):
            for v in value:
                if isinstance(v, dict):
                    if list(iterkeys(v))[0] not in trait_names:  # NOCOV
                        msg = (
                            "Trait '{0}' is assigned to '{1}' but is not def"
                            "ined in the root of the API.".format(v, inst.path)
                        )
                        raise InvalidResourceNodeError(msg)
                    if not isinstance(list(iterkeys(v))[0], str):  # NOCOV
                        msg = ("'{0}' needs to be a string referring to a "
                               "trait, or a dictionary mapping parameter "
                               "values to a trait".format(v))
                        raise InvalidResourceNodeError(msg)
                elif isinstance(v, str):
                    if v not in trait_names:
                        msg = (
                            "Trait '{0}' is assigned to '{1}' but is not "
                            "defined in the root of the API.".format(v,
                                                                     inst.path)
                        )
                        raise InvalidResourceNodeError(msg)
                else:
                    msg = ("'{0}' needs to be a string referring to a "
                           "trait, or a dictionary mapping parameter "
                           "values to a trait".format(v))
                    raise InvalidResourceNodeError(msg)


@collecterrors
def assigned_res_type(inst, attr, value):
    """
    Assert only one (or none) assigned resource type is defined in the RAML
    Root and correctly represented in the RAML.
    """
    if value:
        if isinstance(value, tuple([dict, list])) and len(value) > 1:
            msg = "Too many resource types applied to '{0}'.".format(
                inst.display_name
            )
            raise InvalidResourceNodeError(msg)

        res_types = inst.root.raw.get("resourceTypes", {})
        res_type_names = [list(iterkeys(i))[0] for i in res_types]
        if isinstance(value, list):
            item = value[0]  # NOCOV
        elif isinstance(value, dict):
            item = list(iterkeys(value))[0]  # NOCOV
        else:
            item = value
        if item not in res_type_names:
            msg = ("Resource Type '{0}' is assigned to '{1}' but is not "
                   "defined in the root of the API.".format(value,
                                                            inst.display_name))
            raise InvalidResourceNodeError(msg)


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


#####
# Util/common functions
#####


def validate_mime_type(value):
    """
    Assert a valid MIME media type for request/response body.
    """
    regex_str = re.compile(r"application\/[A-Za-z.-0-1]*?(json|xml)")
    match = re.search(regex_str, value)
    return match
