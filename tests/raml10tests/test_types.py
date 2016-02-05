# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB
from __future__ import absolute_import, division, print_function

import os
import pytest

from ramlfications.parser import parse_raml
from ramlfications.config import setup_config
from ramlfications.utils import load_file
from ramlfications.types import (ObjectType, StringType, Property, IntegerType,
                                 NumberType)
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


def test_number_with_validation():
    datatype = loadapi("type-int.raml").type
    assert type(datatype) == IntegerType

    # correct value does not raise
    datatype.validate(4, "n")

    # not part of enum
    with pytest.raises(DataTypeValidationError) as e:
        datatype.validate(-19, "n")
    msg = ('n: should be one of 1, 3, 4, -4, 40, but got: -19')
    assert msg in e.value.args[0]

    # minimum
    with pytest.raises(DataTypeValidationError) as e:
        datatype.validate(-4, "n")
    msg = ('n: requires to be minimum -2, but got: -4')
    assert msg in e.value.args[0]

    # maximum
    with pytest.raises(DataTypeValidationError) as e:
        datatype.validate(40, "n")
    msg = ('n: requires to be maximum 9, but got: 40')
    assert msg in e.value.args[0]

    # multiple_of
    datatype = IntegerType("n", multiple_of=2)
    datatype.validate(4, "n")
    with pytest.raises(DataTypeValidationError) as e:
        datatype.validate(3, "n")
    msg = ('n: requires to be multiple of 2, but got: 3')
    assert msg in e.value.args[0]

    # not int
    datatype = IntegerType("n")
    with pytest.raises(DataTypeValidationError) as e:
        datatype.validate(2.1, "n")
    msg = ('n: requires an integer, but got: 2.1')
    assert msg in e.value.args[0]

    # not int
    datatype = NumberType("n")
    datatype.validate(2.1, "n")
    with pytest.raises(DataTypeValidationError) as e:
        datatype.validate('xx2.1', "n")
    msg = ('n: requires a number, but got: xx2.1')
    assert msg in e.value.args[0]
