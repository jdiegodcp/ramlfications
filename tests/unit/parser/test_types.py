# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB

import os
import pytest


from ramlfications import parse
from ramlfications.errors import InvalidRAMLStructureError


from tests.base import RAML_10, assert_not_set


@pytest.fixture(scope="session")
def root():
    data_types = os.path.join(RAML_10, "data_types")
    raml_file = os.path.join(data_types, "basic_types.raml")
    conf_file = os.path.join(RAML_10, "test-config.ini")
    return parse(raml_file, conf_file)


def test_parse_data_types(root):
    types = root.types
    assert len(types) == 3

    t = types[0]
    assert t.name == "Person"
    assert t.display_name == t.name
    assert t.type == "object"
    assert list(t.properties.keys()) == ["name"]

    p = t.properties.get("name")
    assert not p.default
    assert p.required
    assert p.type == "string"

    t = types[1]
    assert t.name == "Place"
    assert t.type == "object"
    assert t.display_name == t.name
    props = sorted(list(t.properties.keys()))
    assert props == ["city", "province", "state"]

    p = t.properties.get("city")
    assert not p.default
    assert p.required
    assert p.type == "string"

    p = t.properties.get("province")
    assert not p.default
    assert not p.required
    assert p.type == "string"

    p = t.properties.get("state")
    assert not p.default
    assert p.required
    assert p.type == "string"

    t = types[2]
    assert t.name == "Thing"
    assert t.display_name == t.name
    assert t.type == "string"
    assert not t.pattern
    assert t.min_length == 0
    assert t.max_length == 2147483647

    not_set = [
        "annotation", "default", "example", "examples", "facets",
        "schema", "xml"
    ]
    for t in types:
        assert_not_set(t, not_set)


def test_data_type_fragment_unknown_facet():
    # a ``#%RAML 1.0 DataType`` fragment declares ONE type; this file's body is
    # a map of two types, so ``Person``/``Employee`` are unknown facets.
    # Reported as a RAML error, not TypeError.
    raml_file = os.path.join(RAML_10, "data_types", "data_type_fragment.raml")
    conf_file = os.path.join(RAML_10, "test-config.ini")
    with pytest.raises(InvalidRAMLStructureError) as e:
        parse(raml_file, conf_file)
    msg = e.value.args[0]
    assert "person" in msg or "employee" in msg
