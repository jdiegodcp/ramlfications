# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function

import attr

from ramlfications.errors import InvalidRAMLError
from ramlfications.errors import InvalidVersionError
from ramlfications.utils.common import _get

from .parser import RAMLParser
from .types import create_root_data_type
from .parser import RootParser

__all__ = ["parse_raml"]


def parse_raml(loaded_raml, config):
    """
    Parse loaded RAML file into RAML/Python objects.

    :param RAMLDict loaded_raml: OrderedDict of loaded RAML file
    :returns: :py:class:`.raml.RootNodeAPI08` object.
    :raises: :py:class:`.errors.InvalidRAMLError` when RAML file is invalid
    """
    validate = str(_get(config, "validate")).lower() == 'true'

    # Postpone validating the root node until the end; otherwise,
    # we end up with duplicate validation exceptions.
    attr.set_run_validators(False)
    raml_versions = config['raml_versions']
    if loaded_raml._raml_version not in raml_versions:
        raise InvalidVersionError(
            "RAML version not allowed in config {0}: allowed: {1}".format(
                loaded_raml._raml_version, ", ".join(raml_versions)
            ))
    root_parser = RootParser(loaded_raml, config)
    root = root_parser.create_node()
    attr.set_run_validators(validate)

    if loaded_raml._raml_fragment_type == 'Root':
        parser = RAMLParser(loaded_raml, config)
        root = parser.parse()
        attr.set_run_validators(validate)

        if validate:
            attr.validate(root)  # need to validate again for root node

            if root.errors:
                raise InvalidRAMLError(root.errors)
        return root

    if loaded_raml._raml_fragment_type == 'DataType':
        return create_root_data_type(loaded_raml, root)
