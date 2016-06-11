# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB
from __future__ import absolute_import, division, print_function

import os

import pytest

from ramlfications import validate

from ramlfications.errors import InvalidRAMLError, DataTypeValidationError
from ramlfications.validate.data_types import *  # NOQA

from tests.base import V020VALIDATE


raises = pytest.raises(InvalidRAMLError)


# Search a list of errors for a specific error
def _error_exists(error_list, error_type, error_msg):
    for e in error_list:
        if isinstance(e, error_type) and e.args == error_msg:
            return True

    return False


@pytest.fixture(scope="session")
def raml():
    return os.path.join(V020VALIDATE, "data_types/schema_and_type.raml")


@pytest.fixture(scope="session")
def conf():
    return os.path.join(V020VALIDATE, "test_config.ini")


#####
# Validation error messages to test
#####
TEST_ERRORS = [
    # defined_schema
    ("Either 'schema' or 'type' may be defined, not both.",),
    # discriminator_value
    ("Must define a 'discriminator' before setting a 'discriminatorValue'.",)
]


def test_validate_data_types(raml, conf):
    with raises as e:
        validate(raml, conf)

    for msg in TEST_ERRORS:
        assert _error_exists(e.value.errors, DataTypeValidationError, msg)
