# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB

from __future__ import absolute_import, division, print_function

from ramlfications.errors import *  # NOQA

from .decorators import collecterrors


@collecterrors
def defined_schema(inst, attr, value):
    """
    Assert that either 'schema' _or_ 'properties' are defined, not both.
    """
    if value is not None:
        def_type = inst.raw.get("type")
        if def_type:
            msg = "Either 'schema' or 'type' may be defined, not both."
            raise DataTypeValidationError(msg)


# TODO: discriminator value *seems to be* valid in child objects
@collecterrors
def discriminator_value(inst, attr, value):
    if value is not None:
        discriminator = inst.raw.get("discriminator")
        if not discriminator:
            msg = ("Must define a 'discriminator' before setting a "
                   "'discriminatorValue'.")
            raise DataTypeValidationError(msg)
