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
    ramlfile = os.path.join(V020EXAMPLES, "inherited_resource_types.raml")
    loaded_raml = load_file(ramlfile)
    conffile = os.path.join(V020EXAMPLES, "test_config.ini")
    config = setup_config(conffile)
    return parse_raml(loaded_raml, config)


# sanity check
def test_resource_types(api):
    assert len(api.resource_types) == 2

    base = api.resource_types[0]
    assert base.name == "base"
    assert len(base.uri_params) == 1
    assert len(base.query_params) == 1
    assert len(base.headers) == 1
    assert len(base.body) == 1
    assert len(base.responses) == 1

    resp = base.responses[0]
    assert len(resp.headers) == 1
    assert len(resp.body) == 1

    inh = api.resource_types[1]
    assert inh.name == "inheritBase"
    assert len(inh.uri_params) == 1
    assert len(inh.query_params) == 1
    assert len(inh.form_params) == 1
    assert len(inh.body) == 2
    assert len(inh.responses) == 3


def test_get_widgets(api):
    res = api.resources[0]

    assert res.name == "/widgets"
    assert res.display_name == "several-widgets"
    assert res.method == "get"
    desc = "[Get Several Widgets](https://developer.example.com/widgets/)\n"
    assert res.description.raw == desc
    assert res.type == "inheritBase"
    assert len(res.headers) == 2
    assert len(res.body) == 2
    assert len(res.responses) == 3
    assert len(res.query_params) == 2
    assert len(res.form_params) == 1
    assert len(res.uri_params) == 1

    not_set = ["parent", "secured_by", "is_"]
    assert_not_set(res, not_set)

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
    assert h.name == "Accept"
    assert h.display_name == "Accept"
    assert h.description.raw == "An Acceptable header"
    assert h.method == "get"
    assert h.type == "string"
    not_set = [
        "example", "default", "min_length", "max_length", "minimum",
        "maximum", "enum", "repeat", "pattern", "required"
    ]
    assert_not_set(h, not_set)

    resp500 = res.responses[2]
    assert resp500.code == 500
    desc = "This should overwrite inheritBase's description"
    assert resp500.description.raw == desc

    assert len(resp500.headers) == 2

    h = resp500.headers[0]
    assert h.name == "X-Another-500-header"
    assert h.display_name == "X-Another-500-header"
    assert h.description.raw == "another header for 500 response"

    h = resp500.headers[1]
    assert h.name == "X-InheritBase-ServerError-Response-Header"
    assert h.display_name == "X-InheritBase-ServerError-Response-Header"
    assert h.description.raw == "A 500 error"
    assert h.required
    assert h.example == "fuuuuuu"
