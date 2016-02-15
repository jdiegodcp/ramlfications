# -*- coding: utf-8 -*-
# Copyright (c) 2015 The Ramlfications developers

from ramlfications.raml import RootNodeDataType


def create_root_data_type(raml):
    """
    Creates a :py:class:`.raml.RootNodeDataType` based off of the RAML's root\
        section.

    :param RAMLDict raml: loaded RAML file
    :returns: :py:class:`.raml.RootNodeDataType` object with API root\
        attributes set
    """

    return RootNodeDataType(
        raml_obj=raml,
        raw=raml
    )
