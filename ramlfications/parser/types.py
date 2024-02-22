# -*- coding: utf-8 -*-
# Copyright (c) 2015 The Ramlfications developers

from ramlfications.models import DataTypeNode

from ramlfications.utils.types import parse_type


def create_root_data_type(raml, root, name=None):
    """
    Creates a :py:class:`.raml.RootNodeDataType` based off of the RAML's root\
        section.

    :param RAMLDict raml: loaded RAML file
    :returns: :py:class:`.raml.RootNodeDataType` object with API root\
        attributes set
    """

    return DataTypeNode(
        raw=raml,
        raml_version=raml._raml_version,
        type=parse_type(name, raml, root)
    )
