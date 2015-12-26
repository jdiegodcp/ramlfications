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
    ramlfile = os.path.join(V020EXAMPLES, "traits.raml")
    loaded_raml = load_file(ramlfile)
    conffile = os.path.join(V020EXAMPLES, "test_config.ini")
    config = setup_config(conffile)
    return parse_raml(loaded_raml, config)


def test_create_traits(api):
    traits = api.traits
    assert len(traits) == 7

    exp = [
        "filterable", "queryParamsTrait", "formTrait", "baseUriTrait",
        "uriParamsTrait", "protocolTrait", "parameterTrait"
    ]
    assert exp == [t.name for t in traits]


def test_filterable_trait(api):
    t = api.traits[0]

    assert t.name == "filterable"
    assert t.usage == "Some description about using filterable"
    assert not t.description.raw
    assert len(t.query_params) == 1
    assert len(t.headers) == 1
    assert len(t.body) == 1
    assert len(t.responses) == 1

    not_set = [
        "uri_params", "form_params", "base_uri_params", "media_type"
    ]
    assert_not_set(t, not_set)

    q = t.query_params[0]
    assert q.name == "fields"
    assert q.display_name == "Fields"
    desc = "A comma-separated list of fields to filter query"
    assert q.description.raw == desc
    assert q.type == "string"
    exp = "gizmos.items(added_by.id,gizmo(name,href,widget(name,href)))"
    assert q.example == exp

    not_set = [
        "default", "enum", "max_length", "maximum", "min_length", "minimum",
        "pattern", "repeat", "required"
    ]
    assert_not_set(q, not_set)

    h = t.headers[0]
    assert h.name == "X-example-header"
    assert h.display_name == "X-example-header"
    assert h.type == "string"
    desc = "An example of a trait header"
    assert h.description.raw == desc

    not_set = [
        "method", "default", "enum", "example", "max_length", "maximum",
        "min_length", "minimum", "pattern", "repeat", "required"
    ]
    assert_not_set(h, not_set)

    b = t.body[0]
    assert b.mime_type == "application/json"
    assert b.schema == {"name": "string"}
    assert b.example == {"name": "example body for trait"}
    assert not b.form_params

    r = t.responses[0]
    assert r.code == 200
    assert r.description.raw == "Yay filterable!"

    not_set = ["method", "headers", "body"]
    assert_not_set(r, not_set)


def test_query_params_trait(api):
    t = api.traits[1]

    assert t.name == "queryParamsTrait"
    assert t.description.raw == "A description of the paged trait"
    assert t.media_type == "application/xml"
    assert len(t.query_params) == 2

    not_set = [
        "uri_params", "form_params", "base_uri_params", "protocols",
        "body", "headers", "responses", "usage"
    ]
    assert_not_set(t, not_set)

    q = t.query_params[0]
    assert q.name == "limit"
    assert q.display_name == "Limit"
    desc = "The maximum number of gizmo objects to return"
    assert q.description.raw == desc
    assert q.type == "integer"
    assert q.example == 10
    assert q.minimum == 0
    assert q.default == 20
    assert q.maximum == 50

    not_set = [
        "enum", "max_length", "min_length", "required", "repeat", "pattern"
    ]
    assert_not_set(q, not_set)

    q = t.query_params[1]
    assert q.name == "offset"
    assert q.display_name == "Offset"
    desc = "The index of the first gizmo to return"
    assert q.description.raw == desc
    assert q.type == "integer"
    assert q.example == 5
    assert q.default == 0

    not_set = [
        "enum", "max_length", "min_length", "required", "minimum", "maximum",
        "repeat", "pattern"
    ]
    assert_not_set(q, not_set)


def test_form_param_trait(api):
    t = api.traits[2]

    assert t.name == "formTrait"
    assert t.description.raw == "A description of a trait with form parameters"
    assert t.media_type == "application/x-www-form-urlencoded"
    assert len(t.form_params) == 1

    not_set = [
        "query_params", "uri_params", "base_uri_params", "body", "headers",
        "responses", "protocols", "usage"
    ]
    assert_not_set(t, not_set)

    f = t.form_params[0]
    assert f.name == "foo"
    assert f.display_name == "Foo"
    assert f.description.raw == "The Foo Form Field"
    assert f.type == "string"
    assert f.min_length == 5
    assert f.max_length == 50
    assert f.default == "bar"

    not_set = [
        "enum", "example", "minimum", "maximum", "repeat", "required",
        "pattern"
    ]
    assert_not_set(f, not_set)


def test_base_uri_trait(api):
    t = api.traits[3]

    assert t.name == "baseUriTrait"
    desc = "A description of a trait with base URI parameters"
    assert t.description.raw == desc
    assert len(t.base_uri_params) == 1

    not_set = [
        "uri_params", "form_params", "query_params", "usage", "headers",
        "body", "responses", "media_type", "protocols"
    ]
    assert_not_set(t, not_set)

    u = t.base_uri_params[0]
    assert u.name == "communityPath"
    assert u.display_name == "Community Path trait"
    assert u.description.raw == "The community path base URI trait"
    assert u.type == "string"
    assert u.example == "baz-community"
    assert u.required

    not_set = [
        "enum", "default", "minimum", "maximum", "min_length", "max_length",
        "repeat", "pattern"
    ]
    assert_not_set(u, not_set)


def test_uri_trait(api):
    t = api.traits[4]

    assert t.name == "uriParamsTrait"
    desc = "A description of a trait with URI parameters"
    assert t.description.raw == desc
    assert len(t.uri_params) == 1

    not_set = [
        "base_uri_params", "form_params", "query_params", "headers",
        "body", "responses", "usage", "media_type", "protocols"
    ]
    assert_not_set(t, not_set)

    u = t.uri_params[0]
    assert u.name == "communityPath"
    assert u.display_name == "Community Path trait"
    assert u.description.raw == "The community path URI params trait"
    assert u.type == "string"
    assert u.example == "baz-community"
    assert u.required

    not_set = [
        "enum", "default", "minimum", "maximum", "min_length", "max_length",
        "repeat", "pattern"
    ]
    assert_not_set(u, not_set)


def test_protocol_trait(api):
    t = api.traits[5]

    assert t.name == "protocolTrait"
    assert t.description.raw == "A trait to assign a protocol"
    assert t.protocols == ["HTTP"]

    not_set = [
        "uri_params", "base_uri_params", "form_params", "query_params",
        "body", "responses", "media_type", "usage"
    ]
    assert_not_set(t, not_set)


def test_parameter_trait(api):
    t = api.traits[6]

    assert t.name == "parameterTrait"
    assert len(t.query_params) == 1
    assert not t.description.raw

    not_set = [
        "desc", "uri_params", "base_uri_params", "form_params", "body",
        "responses", "media_type", "usage", "protocols"
    ]
    assert_not_set(t, not_set)

    q = t.query_params[0]
    assert q.name == "<<tokenName>>"
    assert q.description.raw == "A valid <<tokenName>> is required"
    assert q.type == "string"

    not_set = [
        "default", "enum", "example", "min_length", "max_length", "minimum",
        "maximum", "required", "repeat", "pattern"
    ]
    assert_not_set(q, not_set)
