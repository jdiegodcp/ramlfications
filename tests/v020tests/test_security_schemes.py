# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB
from __future__ import absolute_import, division, print_function

import os

import pytest

from ramlfications.parser import parse_raml
from ramlfications.config import setup_config
from ramlfications.utils import load_file


from tests.base import V020EXAMPLES, assert_not_set, assert_not_set_raises


# Security scheme properties:
# name, raw, type, described_by, desc, settings, config, errors


@pytest.fixture(scope="session")
def api():
    ramlfile = os.path.join(V020EXAMPLES, "security_schemes.raml")
    loaded_raml = load_file(ramlfile)
    conffile = os.path.join(V020EXAMPLES, "test_config.ini")
    config = setup_config(conffile)
    return parse_raml(loaded_raml, config)


def test_create_sec_schemes(api):
    schemes = api.security_schemes
    assert len(schemes) == 5

    exp = [
        "oauth_2_0", "oauth_1_0", "basic", "digest", "custom_auth"
    ]
    assert exp == [s.name for s in schemes]


def test_oauth_2_0_scheme(api):
    s = api.security_schemes[0]

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


def test_oauth_1_0_scheme(api):
    s = api.security_schemes[1]

    assert s.name == "oauth_1_0"
    assert s.type == "OAuth 1.0"
    assert s.description.raw == "Example API support OAuth 1.0"
    assert len(s.headers) == 1
    assert len(s.responses) == 1
    assert isinstance(s.described_by, dict)
    assert isinstance(s.settings, dict)

    not_set = [
        "usage", "body", "form_params", "uri_params", "query_params",
        "media_type", "protocols", "documentation"
    ]

    assert_not_set_raises(s, not_set)

    h = s.headers[0]
    assert h.name == "Authorization"
    assert h.display_name == "Authorization"
    assert h.description.raw == "Used to send a valid OAuth 1 auth info"
    assert h.type == "string"

    not_set = [
        "example", "min_length", "max_length", "minimum", "maximum",
        "default", "repeat", "pattern", "method", "required"
    ]
    assert_not_set(h, not_set)

    resp200 = s.responses[0]
    assert resp200.code == 200
    assert resp200.description.raw == "yay authenticated!"
    assert len(resp200.headers) == 1
    not_set = ["body", "method"]
    assert_not_set(resp200, not_set)

    rh = resp200.headers[0]
    assert rh.name == "WWW-Authenticate"
    assert rh.display_name == "WWW-Authenticate"
    assert rh.type == "string"
    desc = "Authentication protocols that the server supports"
    assert rh.description.raw == desc
    not_set = [
        "example", "min_length", "max_length", "minimum", "maximum",
        "default", "repeat", "pattern", "method", "required"
    ]
    assert_not_set(rh, not_set)

    st = s.settings
    exp_st = dict(requestTokenUri="https://accounts.example.com/request",
                  authorizationUri="https://accounts.example.com/auth",
                  tokenCredentialsUri="https://accounts.example.com/token")
    assert st == exp_st


def test_basic(api):
    s = api.security_schemes[2]

    assert s.name == "basic"
    assert s.type == "Basic Authentication"
    assert isinstance(s.described_by, dict)
    assert not s.settings
    assert len(s.headers) == 1

    not_set = [
        "usage", "body", "form_params", "uri_params", "query_params",
        "media_type", "protocols", "documentation", "responses"
    ]

    assert_not_set_raises(s, not_set)

    h = s.headers[0]
    assert h.name == "Authorization"
    assert h.display_name == "Authorization"
    assert h.description.raw == "Used to send base64-encoded credentials"
    assert h.type == "string"

    not_set = [
        "example", "min_length", "max_length", "minimum", "maximum",
        "default", "repeat", "pattern", "method", "required"
    ]
    assert_not_set(h, not_set)


def test_digest(api):
    s = api.security_schemes[3]

    assert s.name == "digest"
    assert s.type == "Digest Authentication"
    assert isinstance(s.described_by, dict)
    assert not s.settings
    assert len(s.headers) == 1

    not_set = [
        "usage", "body", "form_params", "uri_params", "query_params",
        "media_type", "protocols", "documentation", "responses"
    ]

    assert_not_set_raises(s, not_set)

    h = s.headers[0]
    assert h.name == "Authorization"
    assert h.display_name == "Authorization"
    assert h.description.raw == "Used to send digest authentication"
    assert h.type == "string"

    not_set = [
        "example", "min_length", "max_length", "minimum", "maximum",
        "default", "repeat", "pattern", "method", "required"
    ]
    assert_not_set(h, not_set)


def test_custom(api):
    s = api.security_schemes[4]

    assert s.name == "custom_auth"
    assert s.type == "X-custom-auth"
    assert s.description.raw == "custom auth for testing"
    assert s.media_type == "application/x-www-form-urlencode"
    assert s.usage == "Some usage description"
    assert s.protocols == ["HTTPS"]
    assert len(s.documentation) == 1
    assert len(s.query_params) == 1
    assert len(s.uri_params) == 1
    assert len(s.form_params) == 1
    assert len(s.body) == 1
    assert isinstance(s.settings, dict)
    assert isinstance(s.described_by, dict)

    assert_not_set_raises(s, ["responses"])

    d = s.documentation[0]
    assert d.title.raw == "foo docs"
    assert d.content.raw == "foo content"

    q = s.query_params[0]
    assert q.name == "fooQParam"
    assert q.display_name == "fooQParam"
    assert q.description.raw == "A foo Query parameter"
    assert q.type == "string"
    not_set = [
        "example", "min_length", "max_length", "minimum", "maximum",
        "default", "repeat", "pattern", "required", "enum"
    ]
    assert_not_set(q, not_set)

    u = s.uri_params[0]
    assert u.name == "subDomain"
    assert u.display_name == "subDomain"
    assert u.description.raw == "subdomain of auth"
    assert u.default == "fooauth"
    assert u.type == "string"
    assert u.required
    not_set = [
        "example", "min_length", "max_length", "minimum", "maximum",
        "repeat", "pattern", "enum"
    ]
    assert_not_set(u, not_set)

    f = s.form_params[0]
    assert f.name == "fooFormParam"
    assert f.display_name == "fooFormParam"
    assert f.description.raw == "A foo form parameter"
    assert f.type == "string"
    not_set = [
        "example", "min_length", "max_length", "minimum", "maximum",
        "repeat", "pattern", "enum", "required", "default"
    ]
    assert_not_set(f, not_set)

    b = s.body[0]
    assert b.mime_type == "application/x-www-form-urlencoded"
    assert len(b.form_params) == 1
    not_set = ["schema", "example"]
    assert_not_set(b, not_set)

    f = b.form_params[0]
    assert f.name == "anotherFormParam"
    assert f.display_name == "anotherFormParam"
    assert f.description.raw == "another form parameter"
    assert f.type == "string"
    not_set = [
        "example", "min_length", "max_length", "minimum", "maximum",
        "repeat", "pattern", "enum", "required", "default"
    ]
    assert_not_set(f, not_set)

    st = s.settings
    exp_st = {"foo": "bar"}
    assert st == exp_st
