#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

import os

import pytest

from ramlfications import parse
from ramlfications import parser as pw
from ramlfications.config import setup_config
from ramlfications.raml import RootNode, ResourceTypeNode, TraitNode
from ramlfications.utils import load_file

from tests.base import EXAMPLES


@pytest.fixture(scope="session")
def github_raml():
    raml_file = os.path.join(EXAMPLES, "github.raml")
    return load_file(raml_file)


def test_parse_raml(github_raml):
    config_file = os.path.join(EXAMPLES, "github-config.ini")
    config = setup_config(config_file)
    root = pw.parse_raml(github_raml, config)
    assert isinstance(root, RootNode)


@pytest.fixture(scope="session")
def root():
    raml_file = os.path.join(EXAMPLES, "github.raml")
    loaded_raml_file = load_file(raml_file)
    config_file = os.path.join(EXAMPLES, "github-config.ini")
    config = setup_config(config_file)
    return pw.create_root(loaded_raml_file, config)


def test_base_uri(root):
    expected = "https://api.github.com/"
    assert expected == root.base_uri


def test_protocols(root):
    expected = ["HTTPS"]
    assert expected == root.protocols


def test_docs(root):
    assert root.documentation is None


def test_base_uri_params(root):
    assert root.base_uri_params is None


def test_uri_params(root):
    assert root.uri_params is None


def test_title(root):
    assert root.title == "GitHub API"


def test_version(root):
    assert root.version == "v3"


def test_schemas(root):
    assert root.schemas is None


def test_media_type(root):
    assert root.media_type == "application/json"


#####
# Security Schemes
#####

@pytest.fixture(scope="session")
def sec_schemes():
    raml_file = os.path.join(EXAMPLES, "github.raml")
    config = os.path.join(EXAMPLES, "github-config.ini")
    api = parse(raml_file, config)
    return api.security_schemes


def test_create_security_schemes(sec_schemes):
    assert len(sec_schemes) == 2
    assert sec_schemes[0].name == "basic"
    assert sec_schemes[0].type == "Basic Authentication"

    assert sec_schemes[1].name == "oauth_2_0"
    assert sec_schemes[1].type == "OAuth 2.0"

    desc = ("OAuth2 is a protocol that lets external apps request "
            "authorization to private\ndetails in a user's GitHub "
            "account without getting their password. This is\npreferred "
            "over Basic Authentication because tokens can be limited to "
            "specific\ntypes of data, and can be revoked by users at "
            "any time.\n")
    assert sec_schemes[1].description.raw == desc

    assert len(sec_schemes[1].headers) == 1
    assert len(sec_schemes[1].query_params) == 1
    assert len(sec_schemes[1].responses) == 1

    assert sec_schemes[1].headers[0].name == "Authorization"
    assert sec_schemes[1].headers[0].type == "string"

    desc = ("Used to send a valid OAuth 2 access token. Do not use together "
            "with\nthe \"access_token\" query string parameter.\n")
    assert sec_schemes[1].headers[0].description.raw == desc

    assert sec_schemes[1].query_params[0].name == "access_token"
    assert sec_schemes[1].query_params[0].type == "string"

    desc = ("Used to send a valid OAuth 2 access token. Do not use "
            "together with\nthe \"Authorization\" header\n")
    assert sec_schemes[1].query_params[0].description.raw == desc

    assert sec_schemes[1].responses[0].code == 404
    assert sec_schemes[1].responses[0].description.raw == "Unauthorized"

    settings = {
        "authorizationUri": "https://github.com/login/oauth/authorize",
        "accessTokenUri": "https://github.com/login/oauth/access_token",
        "authorizationGrants": ["code"],
        "scopes": [
            "user",
            "user:email",
            "user:follow",
            "public_repo",
            "repo",
            "repo:status",
            "delete_repo",
            "notifications",
            "gist"
        ]
    }
    assert sec_schemes[1].settings == settings


#####
# Traits
#####

@pytest.fixture(scope="session")
def traits():
    raml_file = os.path.join(EXAMPLES, "github.raml")
    config = os.path.join(EXAMPLES, "github-config.ini")
    api = parse(raml_file, config)
    return api.traits


def test_create_traits(traits):
    for trait in traits:
        assert isinstance(trait, TraitNode)

    assert len(traits) == 2


def test_trait_historical(traits):
    trait = traits[0]

    assert trait.form_params is None
    assert trait.uri_params is None
    assert trait.headers is None
    assert trait.body is None
    assert trait.responses is None
    assert len(trait.query_params) == 1

    assert trait.name == "historical"
    assert trait.query_params[0].name == "since"
    assert trait.query_params[0].type == "string"

    desc = ("Timestamp in ISO 8601 format YYYY-MM-DDTHH:MM:SSZ.\n"
            "Only gists updated at or after this time are returned.\n")
    assert trait.query_params[0].description.raw == desc


def test_trait_filterable(traits):
    trait = traits[1]

    assert trait.name == "filterable"
    assert trait.form_params is None
    assert trait.uri_params is None
    assert trait.headers is None
    assert trait.body is None
    assert trait.responses is None

    assert len(trait.query_params) == 6

    filter_ = trait.query_params[0]
    assert filter_.name == "filter"
    assert filter_.enum == [
        "assigned", "created", "mentioned", "subscribed", "all"
    ]
    assert filter_.default == "all"
    assert filter_.required
    assert filter_.type == "string"
    desc = ("Issues assigned to you / created by you / mentioning you / "
            "you're\nsubscribed to updates for / All issues the authenticated "
            "user can see\n")
    assert filter_.description.raw == desc

    state = trait.query_params[1]
    assert state.name == "state"
    assert state.enum == ["open", "closed"]
    assert state.default == "open"
    assert state.required
    assert state.type == "string"
    assert state.description is None
    assert not hasattr(state.description, "raw")
    assert not hasattr(state.description, "html")

    label = trait.query_params[2]
    assert label.name == "labels"
    assert label.type == "string"
    assert label.required
    desc = ("String list of comma separated Label names. Example - "
            "bug,ui,@high.")
    assert label.description.raw == desc

    sort = trait.query_params[3]
    assert sort.name == "sort"
    assert sort.enum == ["created", "updated", "comments"]
    assert sort.default == "created"
    assert sort.required
    assert sort.type == "string"
    assert sort.description is None
    assert not hasattr(sort.description, "raw")
    assert not hasattr(sort.description, "html")

    direction = trait.query_params[4]
    assert direction.name == "direction"
    assert direction.enum == ["asc", "desc"]
    assert direction.default == "desc"
    assert direction.required
    assert direction.description is None
    assert not hasattr(direction.description, "raw")
    assert not hasattr(direction.description, "html")

    since = trait.query_params[5]
    assert since.name == "since"
    assert since.type == "string"
    desc = ("Optional string of a timestamp in ISO 8601 format: "
            "YYYY-MM-DDTHH:MM:SSZ.\nOnly issues updated at or after this "
            "time are returned.\n")
    assert since.description.raw == desc


#####
# Resource Types
#####

@pytest.fixture(scope="session")
def resource_types():
    raml_file = os.path.join(EXAMPLES, "github.raml")
    config = os.path.join(EXAMPLES, "github-config.ini")
    api = parse(raml_file, config)
    return api.resource_types


def test_create_resource_types(resource_types):
    for r in resource_types:
        assert isinstance(r, ResourceTypeNode)

    assert len(resource_types) == 12


def test_resource_type_get_base(resource_types):
    res = resource_types[0]

    assert res.method == "get"
    assert len(res.headers) == 6
    assert len(res.responses) == 1
    assert res.body is None
    assert res.query_params is None
    assert res.form_params is None
    assert res.uri_params is None
    assert res.optional

    header = res.headers[0]
    assert header.name == "X-GitHub-Media-Type"
    assert header.type == "string"
    desc = "You can check the current version of media type in responses.\n"
    assert header.description.raw == desc

    header = res.headers[1]
    assert header.name == "Accept"
    assert header.type == "string"
    assert header.description.raw == "Is used to set specified media type."

    header = res.headers[2]
    assert header.name == "X-RateLimit-Limit"
    assert header.type == "integer"

    header = res.headers[3]
    assert header.name == "X-RateLimit-Remaining"
    assert header.type == "integer"

    header = res.headers[4]
    assert header.name == "X-RateLimit-Reset"
    assert header.type == "integer"

    header = res.headers[5]
    assert header.name == "X-GitHub-Request-Id"
    assert header.type == "integer"

    assert res.responses[0].code == 403
    desc = ("API rate limit exceeded. "
            "See http://developer.github.com/v3/#rate-limiting\nfor "
            "details.\n")
    assert res.responses[0].description.raw == desc


def test_resource_type_post_base(resource_types):
    res = resource_types[1]

    assert res.method == "post"
    assert len(res.headers) == 6
    assert len(res.responses) == 1
    assert res.body is None
    assert res.query_params is None
    assert res.form_params is None
    assert res.uri_params is None
    assert res.optional

    header = res.headers[0]
    assert header.name == "X-GitHub-Media-Type"
    assert header.type == "string"
    desc = "You can check the current version of media type in responses.\n"
    assert header.description.raw == desc

    header = res.headers[1]
    assert header.name == "Accept"
    assert header.type == "string"
    assert header.description.raw == "Is used to set specified media type."

    header = res.headers[2]
    assert header.name == "X-RateLimit-Limit"
    assert header.type == "integer"

    header = res.headers[3]
    assert header.name == "X-RateLimit-Remaining"
    assert header.type == "integer"

    header = res.headers[4]
    assert header.name == "X-RateLimit-Reset"
    assert header.type == "integer"

    header = res.headers[5]
    assert header.name == "X-GitHub-Request-Id"
    assert header.type == "integer"

    assert res.responses[0].code == 403
    desc = ("API rate limit exceeded. "
            "See http://developer.github.com/v3/#rate-limiting\nfor "
            "details.\n")
    assert res.responses[0].description.raw == desc


def test_resource_type_patch_base(resource_types):
    res = resource_types[4]

    assert res.method == "patch"
    assert len(res.headers) == 6
    assert len(res.responses) == 1
    assert res.body is None
    assert res.query_params is None
    assert res.form_params is None
    assert res.uri_params is None
    assert res.optional

    header = res.headers[0]
    assert header.name == "X-GitHub-Media-Type"
    assert header.type == "string"
    desc = "You can check the current version of media type in responses.\n"
    assert header.description.raw == desc

    header = res.headers[1]
    assert header.name == "Accept"
    assert header.type == "string"
    assert header.description.raw == "Is used to set specified media type."

    header = res.headers[2]
    assert header.name == "X-RateLimit-Limit"
    assert header.type == "integer"

    header = res.headers[3]
    assert header.name == "X-RateLimit-Remaining"
    assert header.type == "integer"

    header = res.headers[4]
    assert header.name == "X-RateLimit-Reset"
    assert header.type == "integer"

    header = res.headers[5]
    assert header.name == "X-GitHub-Request-Id"
    assert header.type == "integer"

    assert res.responses[0].code == 403
    desc = ("API rate limit exceeded. "
            "See http://developer.github.com/v3/#rate-limiting\nfor "
            "details.\n")
    assert res.responses[0].description.raw == desc


def test_resource_type_put_base(resource_types):
    res = resource_types[2]

    assert res.method == "put"
    assert len(res.headers) == 6
    assert len(res.responses) == 1
    assert res.body is None
    assert res.query_params is None
    assert res.form_params is None
    assert res.uri_params is None
    assert res.optional

    header = res.headers[0]
    assert header.name == "X-GitHub-Media-Type"
    assert header.type == "string"
    desc = "You can check the current version of media type in responses.\n"
    assert header.description.raw == desc

    header = res.headers[1]
    assert header.name == "Accept"
    assert header.type == "string"
    assert header.description.raw == "Is used to set specified media type."

    header = res.headers[2]
    assert header.name == "X-RateLimit-Limit"
    assert header.type == "integer"

    header = res.headers[3]
    assert header.name == "X-RateLimit-Remaining"
    assert header.type == "integer"

    header = res.headers[4]
    assert header.name == "X-RateLimit-Reset"
    assert header.type == "integer"

    header = res.headers[5]
    assert header.name == "X-GitHub-Request-Id"
    assert header.type == "integer"

    assert res.responses[0].code == 403
    desc = ("API rate limit exceeded. "
            "See http://developer.github.com/v3/#rate-limiting\nfor "
            "details.\n")
    assert res.responses[0].description.raw == desc


def test_resource_type_delete_base(resource_types):
    res = resource_types[3]

    assert res.method == "delete"
    assert len(res.headers) == 6
    assert len(res.responses) == 1
    assert res.body is None
    assert res.query_params is None
    assert res.form_params is None
    assert res.uri_params is None
    assert res.optional

    header = res.headers[0]
    assert header.name == "X-GitHub-Media-Type"
    assert header.type == "string"
    desc = "You can check the current version of media type in responses.\n"
    assert header.description.raw == desc

    header = res.headers[1]
    assert header.name == "Accept"
    assert header.type == "string"
    assert header.description.raw == "Is used to set specified media type."

    header = res.headers[2]
    assert header.name == "X-RateLimit-Limit"
    assert header.type == "integer"

    header = res.headers[3]
    assert header.name == "X-RateLimit-Remaining"
    assert header.type == "integer"

    header = res.headers[4]
    assert header.name == "X-RateLimit-Reset"
    assert header.type == "integer"

    header = res.headers[5]
    assert header.name == "X-GitHub-Request-Id"
    assert header.type == "integer"

    assert res.responses[0].code == 403
    desc = ("API rate limit exceeded. "
            "See http://developer.github.com/v3/#rate-limiting\nfor "
            "details.\n")
    assert res.responses[0].description.raw == desc


def test_resource_type_get_item(resource_types):
    res = [r for r in resource_types if r.name == "item"]
    res = [r for r in res if r.method == "get"][0]

    assert res.name == "item"
    assert res.type == "base"
    assert res.method == "get"
    assert len(res.headers) == 6
    assert len(res.responses) == 1
    assert res.body is None
    assert res.query_params is None
    assert res.form_params is None
    assert res.uri_params is None
    assert res.optional

    def _sort_headers(item):
        return item.name

    headers = sorted(res.headers, key=_sort_headers)

    header = headers[0]
    assert header.name == "Accept"
    assert header.type == "string"
    assert header.description.raw == "Is used to set specified media type."

    header = headers[1]
    assert header.name == "X-GitHub-Media-Type"
    assert header.type == "string"
    desc = "You can check the current version of media type in responses.\n"
    assert header.description.raw == desc

    header = headers[2]
    assert header.name == "X-GitHub-Request-Id"
    assert header.type == "integer"

    header = headers[3]
    assert header.name == "X-RateLimit-Limit"
    assert header.type == "integer"

    header = headers[4]
    assert header.name == "X-RateLimit-Remaining"
    assert header.type == "integer"

    header = headers[5]
    assert header.name == "X-RateLimit-Reset"
    assert header.type == "integer"

    assert res.responses[0].code == 403
    desc = ("API rate limit exceeded. "
            "See http://developer.github.com/v3/#rate-limiting\nfor "
            "details.\n")
    assert res.responses[0].description.raw == desc
