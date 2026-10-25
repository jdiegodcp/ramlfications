# -*- coding: utf-8 -*-
"""
Tests for RAML 1.0 root-level default mediaType applied to bodies
declared without an explicit media type.
"""

import os

import pytest

from ramlfications import parse
from ramlfications.models import data_types

from tests.base import RAML_10


@pytest.fixture(scope="session")
def api():
    ramlfile = os.path.join(RAML_10, "media_type_default.raml")
    return parse(ramlfile)


def _resource(api, path, method):
    for res in api.resources:
        if res.path == path and res.method == method:
            return res
    raise AssertionError("{0} {1} not found".format(method, path))


def test_response_body_uses_root_media_type(api):
    res = _resource(api, "/people", "get")
    body, = res.responses[0].body
    assert body.mime_type == "application/json"
    assert body.type == "Person"
    assert isinstance(body.data_type, data_types.ObjectDataType)


def test_request_body_uses_root_media_type(api):
    res = _resource(api, "/people", "post")
    body, = res.body
    assert body.mime_type == "application/json"
    assert body.type == "Person"
    assert isinstance(body.data_type, data_types.ObjectDataType)


def test_explicit_media_type_wins(api):
    res = _resource(api, "/people/explicit", "get")
    body, = res.responses[0].body
    assert body.mime_type == "application/xml"
