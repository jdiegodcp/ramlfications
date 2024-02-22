# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function

from six import iterkeys, string_types

from ramlfications.errors import *  # NOQA

from .decorators import collecterrors


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
                elif isinstance(v, string_types):
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
