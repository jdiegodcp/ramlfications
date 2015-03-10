#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

import json
import os

import pytest

from ramlfications import loader
from ramlfications import parse
from ramlfications import parser as pw
from ramlfications.config import setup_config
from ramlfications.raml import (
    RootNode, ResourceTypeNode, TraitNode, ResourceNode
)
from tests.base import EXAMPLES


@pytest.fixture
def raml():
    raml_file = os.path.join(EXAMPLES + "twitter.raml")
    return loader.RAMLLoader().load(raml_file)


def test_parse_raml(raml):
    config = setup_config(EXAMPLES + "twitter-config.ini")
    root = pw.parse_raml(raml, config)
    assert isinstance(root, RootNode)


@pytest.fixture
def root(raml):
    config = setup_config(EXAMPLES + "twitter-config.ini")
    return pw.create_root(raml, config)


@pytest.fixture
def api(raml):
    config = setup_config(EXAMPLES + "twitter-config.ini")
    return pw.parse_raml(raml, config)


def test_base_uri(root):
    expected = "https://api.twitter.com/1.1"
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
    assert root.title == "Twitter API"


def test_version(root):
    assert root.version == "1.1"


def test_schemas(root):
    assert root.schemas is None


def test_media_type(root):
    assert root.media_type == "application/json"


#####
# Security Schemes
#####

@pytest.fixture
def sec_schemes(api):
    return api.security_schemes


def test_create_security_schemes(sec_schemes):
    assert len(sec_schemes) == 1
    assert sec_schemes[0].name == "oauth_1_0"
    assert sec_schemes[0].type == "OAuth 1.0"
    desc = ("Twitter offers applications the ability to issue authenticated "
            "requests on\nbehalf of the application itself (as opposed to "
            "on behalf of a specific user).\n")
    assert sec_schemes[0].description.raw == desc
    settings = {
        "requestTokenUri": "https://api.twitter.com/oauth/request_token",
        "authorizationUri": "https://api.twitter.com/oauth/authorize",
        "tokenCredentialsUri": "https://api.twitter.com/oauth/access_token"
    }
    assert sec_schemes[0].settings == settings


@pytest.fixture
def resource_types(api):
    return api.resource_types


def test_resource_types(resource_types):
    for r in resource_types:
        assert isinstance(r, ResourceTypeNode)
    assert len(resource_types) == 2

    get = resource_types[0]
    post = resource_types[1]

    assert get.name == "base"
    assert post.name == "base"
    assert len(get.uri_params) == 1
    assert len(post.uri_params) == 1

    assert get.uri_params[0].name == "mediaTypeExtension"
    assert get.uri_params[0].enum == [".json"]
    desc = "Use .json to specify application/json media type."
    assert get.uri_params[0].description.raw == desc

    assert post.uri_params[0].name == "mediaTypeExtension"
    assert post.uri_params[0].enum == [".json"]
    desc = "Use .json to specify application/json media type."
    assert post.uri_params[0].description.raw == desc

    assert len(get.responses) == 15
    assert len(post.responses) == 15

    resp = get.responses
    assert resp[0].code == 200
    assert resp[0].description.raw == "Success!"
    assert resp[1].code == 304
    assert resp[1].description.raw == "There was no new data to return."
    assert resp[2].code == 400
    desc = ("The request was invalid or cannot be otherwise served. An "
            "accompanying\nerror message will explain further. In API v1.1, "
            "requests withou\nauthentication are considered invalid and "
            "will yield this response.\n")
    assert resp[2].description.raw == desc
    assert resp[3].code == 401
    desc = "Authentication credentials were missing or incorrect."
    assert resp[3].description.raw == desc
    assert resp[4].code == 403
    desc = ("The request is understood, but it has been refused or access "
            "is no\nallowed. An accompanying error message will explain "
            "why. This code is\nused when requests are being denied due to "
            "update limits.\n")
    assert resp[5].code == 404
    desc = ("The URI requested is invalid or the resource requested, such as "
            "a user,\ndoes not exists. Also returned when the requested "
            "format is not supported\nby the requested method.\n")
    assert resp[5].description.raw == desc
    assert resp[6].code == 406
    desc = ("Returned by the Search API when an invalid format is specified "
            "in the\nrequest.\n")
    assert resp[6].description.raw == desc
    assert resp[7].code == 410
    desc = ("This resource is gone. Used to indicate that an API endpoint has "
            "been\nturned off. For example: \"The Twitter REST API v1 will "
            "soon stop\nfunctioning. Please migrate to API v1.1.\"\n")
    assert resp[7].description.raw == desc
    assert resp[8].code == 420
    desc = ("Returned by the version 1 Search and Trends APIs when you are "
            "being rate\nlimited.\n")
    assert resp[8].description.raw == desc
    assert resp[9].code == 422
    desc = ("Returned when an image uploaded to POST account/"
            "update_profile_banner is\nunable to be processed.\n")
    assert resp[9].description.raw == desc
    assert resp[10].code == 429
    desc = ("Returned in API v1.1 when a request cannot be served due to the\n"
            "application's rate limit having been exhausted for the resource. "
            "See Rate\nLimiting in API v1.1.\n")
    assert resp[10].description.raw == desc
    assert resp[11].code == 500
    desc = ("Something is broken. Please post to the group so the Twitter "
            "team can\ninvestigate.\n")
    assert resp[11].description.raw == desc
    assert resp[12].code == 502
    desc = ("Twitter is down or being upgraded.")
    assert resp[12].description.raw == desc
    assert resp[13].code == 503
    desc = ("The Twitter servers are up, but overloaded with requests. "
            "Try again later.\n")
    assert resp[13].description.raw == desc
    assert resp[14].code == 504
    desc = ("The Twitter servers are up, but the request couldn't be serviced "
            "due to\nsome failure within our stack. Try again later.\n")
    assert resp[14].description.raw == desc

    resp = post.responses
    assert resp[0].code == 200
    assert resp[0].description.raw == "Success!"
    assert resp[1].code == 304
    assert resp[1].description.raw == "There was no new data to return."
    assert resp[2].code == 400
    desc = ("The request was invalid or cannot be otherwise served. An "
            "accompanying\nerror message will explain further. In API v1.1, "
            "requests withou\nauthentication are considered invalid and "
            "will yield this response.\n")
    assert resp[2].description.raw == desc
    assert resp[3].code == 401
    desc = "Authentication credentials were missing or incorrect."
    assert resp[3].description.raw == desc
    assert resp[4].code == 403
    desc = ("The request is understood, but it has been refused or access "
            "is no\nallowed. An accompanying error message will explain "
            "why. This code is\nused when requests are being denied due to "
            "update limits.\n")
    assert resp[5].code == 404
    desc = ("The URI requested is invalid or the resource requested, such as "
            "a user,\ndoes not exists. Also returned when the requested "
            "format is not supported\nby the requested method.\n")
    assert resp[5].description.raw == desc
    assert resp[6].code == 406
    desc = ("Returned by the Search API when an invalid format is specified "
            "in the\nrequest.\n")
    assert resp[6].description.raw == desc
    assert resp[7].code == 410
    desc = ("This resource is gone. Used to indicate that an API endpoint has "
            "been\nturned off. For example: \"The Twitter REST API v1 will "
            "soon stop\nfunctioning. Please migrate to API v1.1.\"\n")
    assert resp[7].description.raw == desc
    assert resp[8].code == 420
    desc = ("Returned by the version 1 Search and Trends APIs when you are "
            "being rate\nlimited.\n")
    assert resp[8].description.raw == desc
    assert resp[9].code == 422
    desc = ("Returned when an image uploaded to POST account/"
            "update_profile_banner is\nunable to be processed.\n")
    assert resp[9].description.raw == desc
    assert resp[10].code == 429
    desc = ("Returned in API v1.1 when a request cannot be served due to the\n"
            "application's rate limit having been exhausted for the resource. "
            "See Rate\nLimiting in API v1.1.\n")
    assert resp[10].description.raw == desc
    assert resp[11].code == 500
    desc = ("Something is broken. Please post to the group so the Twitter "
            "team can\ninvestigate.\n")
    assert resp[11].description.raw == desc
    assert resp[12].code == 502
    desc = ("Twitter is down or being upgraded.")
    assert resp[12].description.raw == desc
    assert resp[13].code == 503
    desc = ("The Twitter servers are up, but overloaded with requests. "
            "Try again later.\n")
    assert resp[13].description.raw == desc
    assert resp[14].code == 504
    desc = ("The Twitter servers are up, but the request couldn't be serviced "
            "due to\nsome failure within our stack. Try again later.\n")
    assert resp[14].description.raw == desc

    assert get.headers is None
    assert post.headers is None
    assert get.body is None
    assert post.body is None
    assert get.query_params is None
    assert post.query_params is None
    assert get.form_params is None
    assert post.form_params is None
    assert get.method == "get"
    assert post.method == "post"


@pytest.fixture
def traits(api):
    return api.traits


def test_traits(traits):
    assert len(traits) == 2
    for t in traits:
        assert isinstance(t, TraitNode)

    nest = traits[0]
    assert nest.name == "nestedable"
    assert len(nest.query_params) == 1
    assert nest.query_params[0].name == "include_entities"
    assert nest.query_params[0].enum == [0, 1, True, False, None, "f"]
    desc = "The entities node will not be included when set to false."
    assert nest.query_params[0].description.raw == desc
    assert nest.form_params is None
    assert nest.uri_params is None
    assert nest.headers is None
    assert nest.responses is None
    assert nest.body is None

    trim = traits[1]
    assert trim.name == "trimmable"
    assert len(trim.query_params) == 1
    assert trim.query_params[0].name == "trim_user"
    assert trim.query_params[0].enum == [0, 1, True, False, None, "f"]
    desc = ("When set to either true, t or 1, each tweet returned in a "
            "timeline will\ninclude a user object including only the status "
            "authors numerical ID.\nOmit this parameter to receive the "
            "complete user object.\n")
    assert trim.query_params[0].description.raw == desc
    assert trim.form_params is None
    assert trim.uri_params is None
    assert trim.headers is None
    assert trim.body is None
    assert trim.responses is None


@pytest.fixture
def resources(api):
    return api.resources


def test_resources(resources):
    assert len(resources) == 109
    for r in resources:
        assert isinstance(r, ResourceNode)


def test_resources_statuses(resources):
    res = resources[0]

    assert res.method is None
    assert res.name == "/statuses"
    assert res.display_name == "/statuses"
    assert res.type is None
    assert res.traits is None
    assert res.is_ is None
    assert res.resource_type is None
    assert res.description.raw is None
    assert res.headers is None
    assert res.body is None
    assert res.responses is None
    assert res.uri_params is None
    assert res.query_params is None
    assert res.form_params is None
    assert res.parent is None
    # assert res.media_type == "application/json"
    assert res.absolute_uri == "https://api.twitter.com/1.1/statuses"
    assert res.path == "/statuses"
    assert res.protocols == ["HTTPS"]
    # assert res.secured_by == ["oauth_1_0"]
    # assert len(res.security_schemes) == 1
