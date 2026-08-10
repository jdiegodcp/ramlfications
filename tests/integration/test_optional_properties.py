# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB

import os

import pytest

from ramlfications import parse

from tests.base import RAML_08


@pytest.fixture(scope="session")
def api():
    raml_file = os.path.join(
        RAML_08, "optional-properties-resource-types.raml"
    )
    return parse(raml_file)


def test_optional_headers_inherited(api):
    # Issue #43: optional non-method properties (headers?, etc.) declared
    # on a resource type should be inherited when the resource defines
    # the method.
    res = api.resources[0]
    assert res.path == "/gizmos"
    assert res.method == "get"
    header_names = [h.name for h in (res.headers or [])]
    assert "X-Inherited-Header" in header_names
    assert "X-Gizmo-Header" in header_names


def test_optional_query_params_inherited(api):
    res = api.resources[0]
    param_names = [q.name for q in (res.query_params or [])]
    assert "inheritedParam" in param_names


def test_optional_method_not_inherited(api):
    # The optional post? method is not defined by the resource, so it
    # must not leak into the parsed API.
    methods = [(r.path, r.method) for r in api.resources]
    assert ("/gizmos", "post") not in methods
    assert ("/gizmos", "post?") not in methods
