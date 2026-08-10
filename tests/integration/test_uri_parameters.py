# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB

import os

import pytest

from ramlfications import parse

from tests.base import RAML_08


@pytest.fixture(scope="session")
def api():
    raml_file = os.path.join(RAML_08, "implicit-uri-parameters.raml")
    return parse(raml_file)


def _resource(api, path):
    for res in api.resources:
        if res.path == path:
            return res
    raise AssertionError("resource {0} not found".format(path))


def test_implicit_uri_parameter_defaults_to_string(api):
    res = _resource(api, "/items/{id}")
    params = {p.name: p for p in res.uri_params}
    assert "id" in params
    assert params["id"].type == "string"


def test_explicit_uri_parameter_overrides_defaults(api):
    res = _resource(api, "/things/{thingId}")
    params = {p.name: p for p in res.uri_params}
    assert "thingId" in params
    assert params["thingId"].type == "integer"
    assert params["thingId"].description.raw == (
        "An explicitly declared URI parameter"
    )
