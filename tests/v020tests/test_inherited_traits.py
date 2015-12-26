# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB
from __future__ import absolute_import, division, print_function

import os

import pytest

from ramlfications.parser import parse_raml
from ramlfications.config import setup_config
from ramlfications.utils import load_file


from tests.base import V020EXAMPLES, assert_not_set


@pytest.fixture(scope="session")
def api():
    ramlfile = os.path.join(V020EXAMPLES, "inherited_traits.raml")
    loaded_raml = load_file(ramlfile)
    conffile = os.path.join(V020EXAMPLES, "test_config.ini")
    config = setup_config(conffile)
    return parse_raml(loaded_raml, config)


# sanity check
def test_traits(api):
    assert len(api.traits) == 1

    t = api.traits[0]
    assert t.name == "filterable"
    assert t.usage == "Some description about using filterable"
    assert len(t.query_params) == 1
    assert len(t.headers) == 1
    assert len(t.body) == 1
    assert len(t.responses) == 1

    not_set = [
        "uri_params", "form_params", "base_uri_params", "media_type",
        "protocols"
    ]
    assert_not_set(t, not_set)


def test_get_widgets(api):
    res = api.resources[0]

    assert res.name == "/widgets"
    assert res.display_name == "several-widgets"
    assert res.method == "get"
    desc = "[Get Several Widgets](https://developer.example.com/widgets/)\n"
    assert res.description.raw == desc
    assert res.is_ == ["filterable"]

    not_set = ["type", "parent", "form_params", "uri_params"]
    assert_not_set(res, not_set)

    assert len(res.headers) == 2
    assert len(res.body) == 1
    assert len(res.responses) == 2
    assert len(res.query_params) == 2

    h = res.headers[0]
    assert h.name == "X-Widgets-Header"
    assert h.display_name == "X-Widgets-Header"
    assert h.description.raw == "just an extra header for funsies"
    assert h.method == "get"
    assert h.type == "string"
    not_set = [
        "example", "default", "min_length", "max_length", "minimum",
        "maximum", "enum", "repeat", "pattern", "required"
    ]
    assert_not_set(h, not_set)

    h = res.headers[1]
    assert h.name == "X-example-header"
    assert h.display_name == "X-example-header"
    assert h.description.raw == "An example of a trait header"
    assert h.method == "get"
    assert h.type == "string"
    not_set = [
        "example", "default", "min_length", "max_length", "minimum",
        "maximum", "enum", "repeat", "pattern", "required"
    ]
    assert_not_set(h, not_set)

    resp200 = res.responses[0]
    assert resp200.code == 200
    assert resp200.description.raw == "Yay filterable!"

    resp500 = res.responses[1]
    assert resp500.code == 500
    desc = "This should overwrite inheritBase's description"
    assert resp500.description.raw == desc

    assert len(resp500.headers) == 1

    h = resp500.headers[0]
    assert h.name == "X-500-header"
    assert h.display_name == "X-500-header"
    assert h.description.raw == "a header for 500 response"

    q = res.query_params[0]
    assert q.name == "ids"
    assert q.display_name == "Example Widget IDs"
    assert q.description.raw == "A comma-separated list of IDs"
    assert q.required
    assert q.type == "string"

    q = res.query_params[1]
    assert q.name == "fields"
    assert q.display_name == "Fields"
    desc = "A comma-separated list of fields to filter query"
    assert q.description.raw == desc
    exp = "gizmos.items(added_by.id,gizmo(name,href,widget(name,href)))"
    assert q.example == exp

    b = res.body[0]
    assert b.mime_type == "application/json"
    assert b.schema == {"name": "string"}
    assert b.example == {"name": "example body for trait"}
