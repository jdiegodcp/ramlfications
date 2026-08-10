# -*- coding: utf-8 -*-
"""
Tests for RAML 1.0 security scheme parsing: OAuth 2.0 grant values per
1.0, the `Pass Through` scheme type, and `null` securedBy semantics
for optional security.
"""

import os

import pytest

from ramlfications import parse

from tests.base import RAML_10


@pytest.fixture(scope="session")
def api():
    ramlfile = os.path.join(RAML_10, "optional_security.raml")
    return parse(ramlfile)


def test_schemes_declared(api):
    names = [s.name for s in api.security_schemes]
    assert names == ["oauth_2_0", "passthrough"]


def test_oauth2_scheme_with_10_grants(api):
    oauth = api.security_schemes.filter_by(name="oauth_2_0").one()
    assert oauth.type == "OAuth 2.0"
    grants = oauth.settings.get("authorizationGrants")
    # RAML 1.0 grant names (0.8 used code/token/owner/credentials)
    assert grants == ["authorization_code", "implicit"]
    assert oauth.settings.get("scopes") == ["profile"]


def test_oauth2_described_by(api):
    oauth = api.security_schemes.filter_by(name="oauth_2_0").one()
    header = oauth.headers[0]
    assert header.name == "Authorization"
    response = oauth.responses[0]
    assert response.code == 401


def test_pass_through_scheme(api):
    passthrough = api.security_schemes.filter_by(name="passthrough").one()
    assert passthrough.type == "Pass Through"
    assert passthrough.query_params[0].name == "access_token"


def test_optional_security_with_null(api):
    get_users = api.resources.filter_by(method="get", path="/users").one()
    # null + named scheme: accessible anonymously and via the scheme
    assert get_users.secured_by == [None, "oauth_2_0"]
    schemes = [s.name for s in get_users.security_schemes]
    assert schemes == ["oauth_2_0"]


def test_required_security(api):
    post_users = api.resources.filter_by(method="post", path="/users").one()
    assert post_users.secured_by == ["oauth_2_0"]
    schemes = [s.name for s in post_users.security_schemes]
    assert schemes == ["oauth_2_0"]


def test_only_null_security(api):
    public = api.resources.filter_by(path="/public").one()
    assert public.secured_by == [None]
    assert public.security_schemes is None
