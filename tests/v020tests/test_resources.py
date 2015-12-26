# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB
from __future__ import absolute_import, division, print_function

import os

import pytest

from ramlfications.parser import parse_raml
from ramlfications.config import setup_config
from ramlfications.utils import load_file

from tests.base import V020EXAMPLES, assert_not_set, assert_not_set_raises


@pytest.fixture(scope="session")
def api():
    ramlfile = os.path.join(V020EXAMPLES, "resources.raml")
    loaded_raml = load_file(ramlfile)
    conffile = os.path.join(V020EXAMPLES, "test_config.ini")
    config = setup_config(conffile)
    return parse_raml(loaded_raml, config)


def test_create_resources(api):
    res = api.resources
    assert len(res) == 6


def test_get_widgets(api):
    res = api.resources[0]

    assert res.name == "/widgets"
    assert res.display_name == "several-widgets"
    assert res.method == "get"
    desc = "[Get Several Widgets](https://developer.example.com/widgets/)\n"
    assert res.description.raw == desc
    assert res.protocols == ["HTTPS"]
    assert res.path == "/widgets"
    uri = "https://{subDomain}.example.com/v1/{external_party}/widgets"
    assert res.absolute_uri == uri
    assert res.media_type == "application/json"
    assert len(res.base_uri_params) == 1
    not_set = [
        "body", "parent", "traits", "is_", "responses", "secured_by"
    ]
    assert_not_set(res, not_set)


def test_post_gizmos(api):
    res = api.resources[1]

    assert res.name == "/gizmos"
    assert res.display_name == "several-gizmos"
    assert res.method == "post"
    assert res.description.raw == "Post several gizmos"
    assert res.protocols == ["HTTPS"]
    assert res.media_type == "application/json"
    assert res.path == "/gizmos"
    uri = "https://{subDomain}.example.com/v1/{external_party}/gizmos"
    assert res.absolute_uri == uri
    assert res.secured_by == ["oauth_2_0"]

    not_set = [
        "body", "parent", "traits", "is_", "responses", "query_params"
    ]
    assert_not_set(res, not_set)


def test_post_thingys(api):
    res = api.resources[2]

    assert res.name == "/thingys"
    assert res.display_name == "several-thingys"
    assert res.method == "post"
    assert res.description.raw == "Post several thingys"
    assert res.protocols == ["HTTPS"]
    assert res.media_type == "application/json"
    assert res.path == "/thingys"
    uri = "https://{subDomain}.example.com/v1/{external_party}/thingys"
    assert res.absolute_uri == uri
    assert len(res.base_uri_params) == 1
    assert len(res.uri_params) == 1

    not_set = [
        "parent", "traits", "is_", "responses", "query_params", "form_params",
        "secured_by"
    ]
    assert_not_set(res, not_set)


def test_put_thingy_gizmos(api):
    res = api.resources[3]

    assert res.name == "/thingy-gizmos"
    assert res.display_name == "several-thingy-gizmos"
    assert res.method == "put"
    assert res.description.raw == "Put several thingy gizmos"
    assert res.protocols == ["HTTPS"]
    assert res.media_type == "application/json"
    assert res.path == "/thingy-gizmos"
    uri = "https://{subDomain}.example.com/v1/{external_party}/thingy-gizmos"
    assert res.absolute_uri == uri
    assert len(res.base_uri_params) == 1
    assert len(res.uri_params) == 1

    not_set = [
        "parent", "traits", "is_", "body", "query_params", "form_params",
        "secured_by"
    ]
    assert_not_set(res, not_set)


def test_get_thingy_gizmo_id(api):
    res = api.resources[4]

    assert res.name == "/{id}"
    assert res.display_name == "thingy-gizmo"
    assert res.method == "get"
    assert res.description.raw == "Get a single thingy gizmo"
    assert res.protocols == ["HTTPS"]
    assert res.media_type == "application/json"
    assert res.path == "/thingy-gizmos/{id}"
    uri = ("https://{subDomain}.example.com/v1/{external_party}"
           "/thingy-gizmos/{id}")
    assert res.absolute_uri == uri
    assert res.parent.name == "/thingy-gizmos"
    assert len(res.base_uri_params) == 1
    assert len(res.uri_params) == 2

    not_set = [
        "traits", "is_", "body", "query_params", "form_params", "secured_by"
    ]
    assert_not_set(res, not_set)


def test_get_widget_thingys(api):
    res = api.resources[5]

    assert res.name == "/widget-thingys"
    assert res.display_name == "several-widget-thingys"
    assert res.method == "get"
    assert res.description.raw == "Get several filterable widget thingys"
    assert res.protocols == ["HTTPS"]
    assert res.media_type == "application/json"
    assert res.path == "/widget-thingys"
    uri = "https://{subDomain}.example.com/v1/{external_party}/widget-thingys"
    assert res.absolute_uri == uri
    assert len(res.base_uri_params) == 1
    assert len(res.uri_params) == 1
    assert len(res.traits) == 1
    assert res.is_ == ["filterable"]

    not_set = ["parent", "form_params", "secured_by"]
    assert_not_set(res, not_set)


def test_headers(api):
    # get /widgets
    res = api.resources[0]
    assert len(res.headers) == 2

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
    assert h.description.raw == "An Acceptable header for get method"
    assert h.method == "get"
    assert h.type == "string"
    not_set = [
        "example", "default", "min_length", "max_length", "minimum",
        "maximum", "enum", "repeat", "pattern", "required"
    ]
    assert_not_set(h, not_set)


def test_query_params(api):
    # get /widgets
    res = api.resources[0]
    assert len(res.query_params) == 1

    q = res.query_params[0]
    assert q.name == "ids"
    assert q.display_name == "Example Widget IDs"
    assert q.description.raw == "A comma-separated list of IDs"
    assert q.required
    assert q.type == "string"
    assert q.example == "widget1,widget2,widget3"
    not_set = [
        "default", "min_length", "max_length", "minimum",
        "maximum", "enum", "repeat", "pattern"
    ]
    assert_not_set(q, not_set)


def test_form_params(api):
    # post /gizmos
    res = api.resources[1]
    assert len(res.form_params) == 1

    ids = res.form_params[0]
    assert ids.name == "ids"
    assert ids.display_name == "Example Gizmo IDs"
    assert ids.type == "string"
    assert ids.description.raw == "A comma-separated list of IDs"
    assert ids.required
    assert ids.example == "gizmo1,gizmo2,gizmo3"
    not_set = [
        "default", "min_length", "max_length", "minimum",
        "maximum", "enum", "repeat", "pattern"
    ]
    assert_not_set(ids, not_set)


def test_body(api):
    # post /thingys
    res = api.resources[2]
    assert len(res.body) == 3

    json = res.body[0]
    assert json.mime_type == "application/json"
    assert json.schema == {"name": "string"}
    assert json.example == {"name": "Example Name"}

    xml = res.body[1]
    assert xml.mime_type == "application/xml"
    exp_xml = {
        u'xs:schema': {
            u'@attributeFormDefault': u'unqualified',
            u'@elementFormDefault': u'qualified',
            u'@xmlns:xs': u'http://www.w3.org/2001/XMLSchema',
            u'xs:element': {
                u'@name': u'thingy',
                u'@type': u'thingyType'
            },
            u'xs:complexType': {
                u'@name': u'thingyType',
                u'xs:sequence': {
                    u'xs:element': {
                        u'@type': u'xs:string',
                        u'@name': u'name',
                        u'@minOccurs': u'1',
                        u'@maxOccurs': u'1'
                    }
                }
            }
        }
    }

    assert xml.schema == exp_xml

    form = res.body[2]
    assert form.mime_type == "application/x-www-form-urlencoded"
    assert len(form.form_params) == 1

    f = form.form_params[0]
    assert f.name == "foo"
    assert f.display_name == "Foo"
    assert f.type == "string"
    assert f.description.raw == "The Foo Form Field"
    assert f.min_length == 5
    assert f.max_length == 50
    assert f.default == "foobar"
    not_set = [
        "minimum", "maximum", "enum", "repeat", "pattern", "required"
    ]
    assert_not_set(f, not_set)


def test_responses(api):
    # put /thingy-gizmos
    res = api.resources[3]
    assert len(res.responses) == 1

    resp = res.responses[0]
    assert resp.code == 200
    assert resp.method == "put"
    assert resp.description.raw == "A 200 response"
    assert len(resp.headers) == 1
    assert len(resp.body) == 1

    h = resp.headers[0]
    assert h.name == "X-Success-Response-Header"
    assert h.display_name == "X-Success-Response-Header"
    assert h.description.raw == "A 200 header"
    assert h.method == "put"
    assert h.type == "string"
    assert h.required
    assert h.example == "f00bAr"
    not_set = [
        "default", "min_length", "max_length", "minimum", "maximum",
        "enum", "repeat", "pattern"
    ]
    assert_not_set(h, not_set)

    b = resp.body[0]
    assert b.mime_type == "application/json"
    assert b.schema == {"name": "a schema body"}
    assert b.example == {"name": "an example body"}
    assert not b.form_params


def test_base_uri_params(api):
    # get /widgets
    res = api.resources[0]
    assert len(res.base_uri_params) == 1

    u = res.base_uri_params[0]
    assert u.name == "subDomain"
    assert u.display_name == "subDomain"
    assert u.description.raw == "subdomain of API server"
    assert u.example == "sjc"
    assert u.type == "string"
    assert u.required
    not_set = [
        "default", "min_length", "max_length", "minimum", "maximum",
        "enum", "repeat", "pattern"
    ]
    assert_not_set(u, not_set)


def test_uri_params(api):
    # get /widgets
    res = api.resources[0]
    assert len(res.uri_params) == 1

    u = res.uri_params[0]
    assert u.name == "external_party"
    assert u.display_name == "external_party"
    assert u.description.raw == "code of third-party partner"
    assert u.example == "gizmo_co"
    assert u.type == "string"
    assert u.required
    not_set = [
        "default", "min_length", "max_length", "minimum", "maximum",
        "enum", "repeat", "pattern"
    ]
    assert_not_set(u, not_set)

    # get /thingy-gizmos/{id}
    res = api.resources[4]

    u = res.uri_params[1]
    assert u.name == "external_party"
    assert u.display_name == "external_party"
    assert u.description.raw == "code of third-party partner"
    assert u.example == "gizmo_co"
    assert u.type == "string"
    assert u.required
    not_set = [
        "default", "min_length", "max_length", "minimum", "maximum",
        "enum", "repeat", "pattern"
    ]
    assert_not_set(u, not_set)

    u = res.uri_params[0]
    assert u.name == "id"
    assert u.display_name == "id"
    assert u.description.raw == "The thingy gizmo id"
    assert u.example == "thingygizmo123"
    assert u.type == "string"
    assert u.required
    not_set = [
        "default", "min_length", "max_length", "minimum", "maximum",
        "enum", "repeat", "pattern"
    ]
    assert_not_set(u, not_set)


def test_inherit_traits(api):
    # testing both inherited objects from trait as well as the
    # referred-to trait object itself
    # get /widget-thingys
    res = api.resources[5]

    assert len(res.traits) == 1
    trait = res.traits[0]

    assert len(res.query_params) == 1
    assert len(res.headers) == 1
    assert len(res.body) == 1
    assert len(res.responses) == 1
    # just making sure a 'usage' isn't set
    assert_not_set_raises(res, ["usage"])

    assert len(trait.query_params) == 1
    assert len(trait.headers) == 1
    assert len(trait.body) == 1
    assert len(trait.responses) == 1
    assert trait.usage == "Some description about using filterable"

    q = res.query_params[0]
    assert q.name == "fields"
    assert q.display_name == "Fields"
    desc = "A comma-separated list of fields to filter query"
    assert q.description.raw == desc
    assert q.type == "string"
    exp = "gizmos.items(added_by.id,gizmo(name,href,widget(name,href)))"
    assert q.example == exp
    not_set = [
        "default", "min_length", "max_length", "minimum",
        "maximum", "enum", "repeat", "pattern", "required"
    ]
    assert_not_set(q, not_set)

    q = trait.query_params[0]
    assert q.name == "fields"
    assert q.display_name == "Fields"
    desc = "A comma-separated list of fields to filter query"
    assert q.description.raw == desc
    assert q.type == "string"
    exp = "gizmos.items(added_by.id,gizmo(name,href,widget(name,href)))"
    assert q.example == exp
    not_set = [
        "default", "min_length", "max_length", "minimum",
        "maximum", "enum", "repeat", "pattern", "required"
    ]
    assert_not_set(q, not_set)

    h = res.headers[0]
    assert h.name == "X-example-header"
    assert h.display_name == "X-example-header"
    assert h.description.raw == "An example of a trait header"
    assert h.type == "string"
    not_set = [
        "default", "min_length", "max_length", "minimum",
        "maximum", "enum", "repeat", "pattern", "required",
        "example"
    ]
    assert_not_set(h, not_set)

    h = trait.headers[0]
    assert h.name == "X-example-header"
    assert h.display_name == "X-example-header"
    assert h.description.raw == "An example of a trait header"
    assert h.type == "string"
    not_set = [
        "default", "min_length", "max_length", "minimum",
        "maximum", "enum", "repeat", "pattern", "required",
        "example"
    ]
    assert_not_set(h, not_set)

    b = res.body[0]
    assert b.mime_type == "application/json"
    assert b.schema == {"name": "string"}
    assert b.example == {"name": "example body for trait"}
    assert not b.form_params

    b = trait.body[0]
    assert b.mime_type == "application/json"
    assert b.schema == {"name": "string"}
    assert b.example == {"name": "example body for trait"}
    assert not b.form_params

    r = res.responses[0]
    assert r.code == 200
    assert r.description.raw == "Yay filterable!"
    assert not r.headers
    assert not r.body

    r = trait.responses[0]
    assert r.code == 200
    assert r.description.raw == "Yay filterable!"
    assert not r.headers
    assert not r.body


def test_inherited_type(api):
    # get /widgets
    res = api.resources[0]

    assert res.type == "headerType"
    # test_headers already tests for the inherited headers


def test_security_schemes(api):
    # post /gizmos
    res = api.resources[1]
    assert len(res.security_schemes) == 1

    s = res.security_schemes[0]
    assert s.name == "oauth_2_0"
    assert s.type == "OAuth 2.0"
    desc = ("Example API supports OAuth 2.0 for authenticating all API "
            "requests.\n")
    assert s.description.raw == desc
    assert isinstance(s.described_by, dict)
    assert isinstance(s.settings, dict)
    assert len(s.headers) == 2
    assert len(s.responses) == 2

    not_set = [
        "usage", "body", "form_params", "uri_params", "query_params",
        "media_type", "protocols", "documentation"
    ]

    assert_not_set_raises(s, not_set)

    st = s.settings
    exp_st = dict(authorizationUri="https://accounts.example.com/authorize",
                  accessTokenUri="https://accounts.example.com/api/token",
                  authorizationGrants=["code", "token"],
                  scopes=["user-public-profile", "user-email",
                          "user-activity", "nsa-level-privacy"])
    assert st == exp_st

    db = s.described_by
    exp_db = {
        "headers": {
            "Authorization": {
                "description": "Used to send a valid OAuth 2 access token.\n",
                "type": "string"
            },
            "X-Foo-Header": {
                "description": "a foo header",
                "type": "string"
            }
        },
        "responses": {
            401: {
                "description": ("Bad or expired token. This can happen if the "
                                "user revoked a token or\nthe access token "
                                "has expired. You should re-authenticate the "
                                "user.\n")
            },
            403: {
                "description": ("Bad OAuth request (wrong consumer key, bad "
                                "nonce, expired\ntimestamp...). Unfortunately,"
                                " re-authenticating the user won't help "
                                "here.\n")
            }
        }
    }
    assert db == exp_db

    auth = s.headers[0]
    assert auth.name == "Authorization"
    assert auth.display_name == "Authorization"
    desc = "Used to send a valid OAuth 2 access token.\n"
    assert auth.description.raw == desc
    assert auth.type == "string"

    not_set = [
        "example", "min_length", "max_length", "minimum", "maximum",
        "default", "repeat", "pattern", "method", "required"
    ]
    assert_not_set(auth, not_set)

    foo = s.headers[1]
    assert foo.name == "X-Foo-Header"
    assert foo.display_name == "X-Foo-Header"
    assert foo.description.raw == "a foo header"
    assert foo.type == "string"

    not_set = [
        "example", "min_length", "max_length", "minimum", "maximum",
        "default", "repeat", "pattern", "method", "required"
    ]
    assert_not_set(foo, not_set)

    resp401 = s.responses[0]
    assert resp401.code == 401
    desc = ("Bad or expired token. This can happen if the user revoked a "
            "token or\nthe access token has expired. You should "
            "re-authenticate the user.\n")
    assert resp401.description.raw == desc

    not_set = ["headers", "body", "method"]
    assert_not_set(resp401, not_set)

    resp403 = s.responses[1]
    assert resp403.code == 403
    desc = ("Bad OAuth request (wrong consumer key, bad nonce, expired\n"
            "timestamp...). Unfortunately, re-authenticating the user won't "
            "help here.\n")

    not_set = ["headers", "body", "method"]
    assert_not_set(resp403, not_set)
