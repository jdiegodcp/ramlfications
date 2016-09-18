# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function


from ramlfications.errors import *  # NOQA

from .decorators import collecterrors
from .utils import validate_mime_type


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
            if not d.title.raw:
                msg = "API Documentation requires a title."
                raise InvalidRootNodeError(msg)
            if not d.content.raw:
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
# RAML1.0 validators
#####

# TODO: finish
@collecterrors
def root_types(inst, attr, value):
    pass
