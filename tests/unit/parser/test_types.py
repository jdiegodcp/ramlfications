# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB
from __future__ import absolute_import, division, print_function

import os
import pytest

from six import iterkeys

from ramlfications import parse


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
    assert list(iterkeys(t.properties)) == ["name"]

    p = t.properties.get("name")
    assert not p.default
    assert p.required
    assert p.type == "string"

    t = types[1]
    assert t.name == "Place"
    assert t.type == "object"
    assert t.display_name == t.name
    props = sorted(list(iterkeys(t.properties)))
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
