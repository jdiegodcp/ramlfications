# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB


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
    """
    Require a Base URI where the RAML spec does: RAML 0.8 once the API is
    implemented (config ``production``, true unless set to false); never
    for RAML 1.0, where ``baseUri`` is OPTIONAL.
    """
    if value or inst.raml_version == "1.0":
        return
    production = (inst.config or {}).get("production", True)
    if str(production).strip().lower() == "false":
        return
    msg = "RAML File does not define the baseUri."
    raise InvalidRootNodeError(msg)


@collecterrors
def root_base_uri_params(inst, attr, value):
    """
    Require that Base URI parameters are required. Any named-parameter type
    is allowed (RAML 0.8 "Named Parameters").
    """
    if value:
        for v in value:
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
    if not value:
        return
    # RAML 1.0 allows a list of default media types
    media_types = value if isinstance(value, list) else [value]
    for media_type in media_types:
        match = validate_mime_type(media_type)
        if media_type not in inst.config.get("media_types") and not match:
            msg = "Unsupported MIME Media Type: '{0}'.".format(media_type)
            raise InvalidRootNodeError(msg)


@collecterrors
def root_secured_by(inst, attr, value):
    pass


RAML10_ROOT_CONSTRUCTS = ("types", "annotationTypes", "uses")


@collecterrors
def root_version_constructs(inst, attr, value):
    """
    Apply the rule set matching the detected RAML version: reject
    1.0-only root constructs in 0.8 documents, and 0.8-style root
    ``schemas`` used alongside 1.0 ``types``.
    """
    raw = value or {}
    if inst.raml_version == "0.8":
        invalid = [k for k in RAML10_ROOT_CONSTRUCTS if k in raw]
        if invalid:
            msg = ("The following are RAML 1.0 constructs and are not "
                   "valid in a RAML 0.8 document: {0}.".format(
                       ", ".join(invalid)))
            raise InvalidRootNodeError(msg)
    elif inst.raml_version == "1.0":
        if "schemas" in raw and "types" in raw:
            msg = ("A RAML 1.0 document cannot declare both 'schemas' "
                   "(RAML 0.8) and 'types'; declare only 'types'.")
            raise InvalidRootNodeError(msg)


#####
# RAML1.0 validators
#####

# TODO: finish
@collecterrors
def root_types(inst, attr, value):
    pass
