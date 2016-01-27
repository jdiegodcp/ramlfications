# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB
from __future__ import absolute_import, division, print_function

import os
import pytest

from ramlfications.parser import parse_raml
from ramlfications.config import setup_config
from ramlfications.utils import load_file
from ramlfications.types import (ObjectType, StringType, Property)
from ramlfications.errors import DataTypeValidationError

from tests.base import RAML10EXAMPLES


# Security scheme properties:
# name, raw, type, described_by, desc, settings, config, errors


# as much as possible, those tests are implementing the spec
# the filenames are mapped against
def loadapi(fn):
    ramlfile = os.path.join(RAML10EXAMPLES, fn)
    loaded_raml = load_file(ramlfile)
    conffile = os.path.join(RAML10EXAMPLES, "test_config.ini")
    config = setup_config(conffile)
    return parse_raml(loaded_raml, config)


def test_object():
    api = loadapi("raml-10-spec-object-types.raml")
    exp = (
        "[ObjectType(name='Person', properties="
        "o{'name': Property(data_type=StringType(name=None))})]")
    assert repr(api.types) == exp


def test_string_with_validation():
    datatype = loadapi("type-string-with-pattern.raml").type
    assert type(datatype) == ObjectType
    assert type(datatype.properties['name']) == Property
    assert type(datatype.properties['name'].data_type) == StringType
    assert (datatype.properties['name'].data_type.pattern.pattern ==
            '[A-Z][a-z]+')

    with pytest.raises(DataTypeValidationError) as e:
        datatype.validate(dict(name="foo"))

    msg = ("object.name: requires a string matching pattern [A-Z][a-z]+,"
           " but got: foo")
    assert msg in e.value.args[0]

    with pytest.raises(DataTypeValidationError) as e:
        datatype.validate(dict(name2="foo"))

    msg = "object.name: should be specified, but got: None"
    assert msg in e.value.args[0]

    with pytest.raises(DataTypeValidationError) as e:
        datatype.validate(dict(name="Oo"))

    msg = ("object.name: requires a string with length greater than 3,"
           " but got: Oo")
    assert msg in e.value.args[0]

    with pytest.raises(DataTypeValidationError) as e:
        datatype.validate(dict(name="Oo" * 10))

    msg = ("object.name: requires a string with length smaller than 5,"
           " but got: OoOoOoOoOoOoOoOoOoOo")
    assert msg in e.value.args[0]
