# -*- coding: utf-8 -*-
# Copyright (c) 2015 The Ramlfications developers

from ramlfications.raml import RootNodeDataType
from ramlfications.types import create_type


def create_root_data_type(raml):
    """
    Creates a :py:class:`.raml.RootNodeDataType` based off of the RAML's root\
        section.

    :param RAMLDict raml: loaded RAML file
    :returns: :py:class:`.raml.RootNodeDataType` object with API root\
        attributes set
    """

    return RootNodeDataType(
        raw=raml,
        raml_version=raml._raml_version,
        type=create_type(None, raml)
    )
