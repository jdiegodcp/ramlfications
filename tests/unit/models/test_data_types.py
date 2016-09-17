# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB
from __future__ import absolute_import, division, print_function

import mock
import pytest

from ramlfications.models.data_types import ArrayDataType, ObjectDataType

from tests.base import assert_not_set


@pytest.fixture
def base_data():
    data = {
        # RAMLDataType
        "annotation": None,
        "default": None,
        "example": None,
        "examples": None,
        "facets": None,
        "type": "object",
        "schema": None,
        "usage": "Some usage description",
        "xml": None,
        # DataTypeAttrs
        "raw": {},
        "raml_version": "1.0",
        "root": mock.MagicMock(),
        "errors": None,
        "config": {}
    }
    return data


@pytest.fixture
def object_data_type(base_data):
    base_data["name"] = "foo_object"
    base_data["display_name"] = "Foo Object"
    base_data["description"] = "**This** is a foo _object_ data type."
    base_data["properties"] = {
        "foo_name": {
            "required": True,
            "type": "string"
        }
    }
    base_data["min_properties"] = 0
    base_data["max_properties"] = None
    base_data["additional_properties"] = None
    base_data["discriminator"] = None
    base_data["discriminator_value"] = None

    return ObjectDataType(**base_data)


def test_object_data_type(object_data_type):
    odt = object_data_type
    assert odt.name == "foo_object"
    assert odt.display_name == "Foo Object"
    assert odt.usage == "Some usage description"
    assert odt.raml_version == "1.0"
    assert odt.raw == {}
    assert odt.config == {}
    assert odt.min_properties == 0

    desc = "<p><strong>This</strong> is a foo <em>object</em> data type.</p>\n"
    assert odt.description.html == desc

    not_set = [
        "example", "examples", "facets", "schema", "xml", "errors",
        "max_properties", "additional_properties", "discriminator",
        "discriminator_value"
    ]
    assert_not_set(odt, not_set)


@pytest.fixture
def array_data_type(base_data):
    base_data["name"] = "fooarray"
    base_data["display_name"] = "Foo Array"
    base_data["description"] = "This is a foo array data type."
    base_data["items"] = "Foo"
    base_data["unique_items"] = True
    base_data["min_items"] = 1
    base_data["max_items"] = 5

    return ArrayDataType(**base_data)


def test_array_data_type(array_data_type):
    adt = array_data_type

    assert adt.name == "fooarray"
    assert adt.display_name == "Foo Array"
    assert adt.usage == "Some usage description"
    assert adt.raml_version == "1.0"
    assert adt.raw == {}
    assert adt.config == {}
    assert adt.items == "Foo"
    assert adt.unique_items
    assert adt.min_items == 1
    assert adt.max_items == 5

    not_set = [
        "example", "examples", "facets", "schema", "xml", "errors"
    ]
    assert_not_set(adt, not_set)
