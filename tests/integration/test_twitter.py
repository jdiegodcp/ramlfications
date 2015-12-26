#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

import os

import pytest

from ramlfications import parser as pw
from ramlfications.config import setup_config
from ramlfications.raml import (
    RootNode, ResourceTypeNode, TraitNode, ResourceNode
)
from ramlfications.utils import load_file

from tests.base import EXAMPLES


@pytest.fixture(scope="session")
def raml():
    raml_file = os.path.join(EXAMPLES, "twitter.raml")
    return load_file(raml_file)


def test_parse_raml(raml):
    config_file = os.path.join(EXAMPLES, "twitter-config.ini")
    config = setup_config(config_file)
    root = pw.parse_raml(raml, config)
    assert isinstance(root, RootNode)


@pytest.fixture(scope="session")
def root(raml):
    config_file = os.path.join(EXAMPLES, "twitter-config.ini")
    config = setup_config(config_file)
    return pw.create_root(raml, config)


@pytest.fixture(scope="session")
def api(raml):
    config_file = os.path.join(EXAMPLES, "twitter-config.ini")
    config = setup_config(config_file)
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


def test_secured_by(root):
    assert root.secured_by == ["oauth_1_0"]


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


ATTRIBUTES = [
    "absolute_uri", "base_uri_params", "body", "description", "display_name",
    "form_params", "headers", "is_", "media_type", "method", "name", "parent",
    "path", "protocols", "query_params", "raw", "resource_type", "responses",
    "root", "secured_by", "security_schemes", "traits", "type", "uri_params"
]

STR_ATTRS = [
    "absolute_uri", "display_name", "media_type", "method", "name",
    "path", "type"
]

ABSOLUTE_URI = "https://api.twitter.com/1.1/"


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
    assert res.media_type is None
    assert res.absolute_uri == "https://api.twitter.com/1.1/statuses"
    assert res.path == "/statuses"
    assert res.protocols == ["HTTPS"]
    assert res.secured_by == ["oauth_1_0"]
    assert len(res.security_schemes) == 1


def test_resources_statuses_mention_timeline(resources):
    res = resources[1]

    desc = ("Returns the 20 most recent mentions (tweets containing a users's "
            "@screen_name)\nfor the authenticating user.\nThe timeline "
            "returned is the equivalent of the one seen when you view your\n"
            "mentions on twitter.com.\nThis method can only return up to "
            "800 tweets.\n")

    exp_data = {
        "absolute_uri": ABSOLUTE_URI + "statuses/mentions_timeline{mediaTypeExtension}",  # NOQA
        "display_name": "/mentions_timeline{mediaTypeExtension}",
        "media_type": "application/json",
        "method": "get",
        "name": "/mentions_timeline{mediaTypeExtension}",
        "path": "/statuses/mentions_timeline{mediaTypeExtension}",
        "type": "base"
    }
    for key, value in exp_data.items():
        data = getattr(res, key)
        assert value == data

    assert res.description.raw == desc
    assert res.secured_by == ["oauth_1_0"]
    # actual sec scheme objects may be different since resource could
    # have certain scopes assigned.
    assert res.security_schemes[0].raw == res.root.security_schemes[0].raw
    assert res.protocols == ["HTTPS"]
    assert res.headers is None
    assert res.body is None
    assert res.form_params is None
    assert res.is_ == ["nestedable", "trimmable"]
    assert res.type == "base"

    assert len(res.traits) == 2
    assert res.traits[0] == res.root.traits[0]
    assert res.traits[1] == res.root.traits[1]

    assert res.resource_type == res.root.resource_types[0]

    assert len(res.uri_params) == 1
    assert res.uri_params[0].name == "mediaTypeExtension"
    assert res.uri_params[0].enum == [".json"]
    desc = "Use .json to specify application/json media type."
    assert res.uri_params[0].description.raw == desc

    assert len(res.query_params) == 6

    param = res.query_params[0]
    assert param.name == "count"
    assert param.type == "integer"
    assert param.maximum == 200
    desc = ("Specifies the number of tweets to try and retrieve, up to a "
            "maximum of\n200. The value of count is best thought of as a "
            "limit to the number of\ntweets to return because suspended or "
            "deleted content is removed after\nthe count has been applied. "
            "We include retweets in the count, even if\ninclude_rts is not "
            "supplied. It is recommended you always send include_rts=1\n"
            "when using this API method.\n")
    assert param.description.raw == desc

    param = res.query_params[1]
    assert param.name == "since_id"
    assert param.type == "integer"
    desc = ("Returns results with an ID greater than (that is, more recent "
            "than) the\nspecified ID. There are limits to the number of "
            "Tweets which can be accessed\nthrough the API. If the limit of "
            "Tweets has occured since the since_id, the\nsince_id will be "
            "forced to the oldest ID available.\n")
    assert param.description.raw == desc

    param = res.query_params[2]
    assert param.name == "max_id"
    assert param.type == "integer"
    desc = ("Returns results with an ID less than (that is, older than) or "
            "equal to\nthe specified ID.\n")
    assert param.description.raw == desc

    param = res.query_params[3]
    assert param.name == "contributor_details"
    assert param.type == "string"
    desc = ("This parameter enhances the contributors element of the status "
            "response\nto include the screen_name of the contributor. By "
            "default only the user_id\nof the contributor is included.\n")
    assert param.description.raw == desc

    param = res.query_params[4]
    assert param.name == "include_entities"
    assert param.enum == [0, 1, True, False, None, "f"]
    desc = "The entities node will not be included when set to false."
    assert param.description.raw == desc

    param = res.query_params[5]
    assert param.name == "trim_user"
    assert param.enum == [0, 1, True, False, None, "f"]
    desc = ("When set to either true, t or 1, each tweet returned in a "
            "timeline will\ninclude a user object including only the status "
            "authors numerical ID.\nOmit this parameter to receive the "
            "complete user object.\n")
    assert param.description.raw == desc

    assert len(res.responses) == 15

    r = res.responses[0]

    assert r.code == 200
    assert r.description.raw == "Success!"
    assert len(r.body) == 1
    assert r.body[0].schema is not None
    assert r.body[0].example is not None
    assert r.headers is None
    assert r.config is not None

    r = res.responses[1]

    assert r.code == 304
    desc = "There was no new data to return."
    assert r.description.raw == desc
    assert r.body is None
    assert r.headers is None
    assert r.config is not None

    r = res.responses[2]
    assert r.code == 400
    desc = ("The request was invalid or cannot be otherwise served. An "
            "accompanying\nerror message will explain further. In API v1.1, "
            "requests withou\nauthentication are considered invalid and will "
            "yield this response.\n")
    assert r.description.raw == desc
    assert r.body is None
    assert r.headers is None
    assert r.config is not None

    r = res.responses[3]
    assert r.code == 401
    desc = ("Authentication credentials were missing or incorrect.")
    assert r.description.raw == desc
    assert r.body is None
    assert r.headers is None
    assert r.config is not None

    r = res.responses[4]
    assert r.code == 403
    desc = ("The request is understood, but it has been refused or access "
            "is no\nallowed. An accompanying error message will explain why. "
            "This code is\nused when requests are being denied due to "
            "update limits.\n")
    assert r.description.raw == desc
    assert r.body is None
    assert r.headers is None
    assert r.config is not None

    r = res.responses[5]
    assert r.code == 404
    desc = ("The URI requested is invalid or the resource requested, such as "
            "a user,\ndoes not exists. Also returned when the requested "
            "format is not supported\nby the requested method.\n")
    assert r.description.raw == desc
    assert r.body is None
    assert r.headers is None
    assert r.config is not None

    r = res.responses[6]
    assert r.code == 406
    desc = ("Returned by the Search API when an invalid format is specified "
            "in the\nrequest.\n")
    assert r.description.raw == desc
    assert r.body is None
    assert r.headers is None
    assert r.config is not None

    r = res.responses[7]
    assert r.code == 410
    desc = ("This resource is gone. Used to indicate that an API endpoint "
            "has been\nturned off. For example: \"The Twitter REST API "
            "v1 will soon stop\nfunctioning. Please migrate to API v1.1.\"\n")
    assert r.description.raw == desc
    assert r.body is None
    assert r.headers is None
    assert r.config is not None

    r = res.responses[8]
    assert r.code == 420
    desc = ("Returned by the version 1 Search and Trends APIs when you are "
            "being rate\nlimited.\n")
    assert r.description.raw == desc
    assert r.body is None
    assert r.headers is None
    assert r.config is not None

    r = res.responses[9]
    assert r.code == 422
    desc = ("Returned when an image uploaded to POST account/update_profile"
            "_banner is\nunable to be processed.\n")
    assert r.description.raw == desc
    assert r.body is None
    assert r.headers is None
    assert r.config is not None

    r = res.responses[10]
    assert r.code == 429
    desc = ("Returned in API v1.1 when a request cannot be served due to the\n"
            "application's rate limit having been exhausted for the resource. "
            "See Rate\nLimiting in API v1.1.\n")
    assert r.description.raw == desc
    assert r.body is None
    assert r.headers is None
    assert r.config is not None

    r = res.responses[11]
    assert r.code == 500
    desc = ("Something is broken. Please post to the group so the Twitter "
            "team can\ninvestigate.\n")
    assert r.description.raw == desc
    assert r.body is None
    assert r.headers is None
    assert r.config is not None

    r = res.responses[12]
    assert r.code == 502
    desc = "Twitter is down or being upgraded."
    assert r.description.raw == desc
    assert r.body is None
    assert r.headers is None
    assert r.config is not None

    r = res.responses[13]
    assert r.code == 503
    desc = ("The Twitter servers are up, but overloaded with requests. Try "
            "again later.\n")
    assert r.description.raw == desc
    assert r.body is None
    assert r.headers is None
    assert r.config is not None

    r = res.responses[14]
    assert r.code == 504
    desc = ("The Twitter servers are up, but the request couldn't be "
            "serviced due to\nsome failure within our stack. Try again "
            "later.\n")
    assert r.description.raw == desc
    assert r.body is None
    assert r.headers is None
    assert r.config is not None


def test_resources_statuses_user_timeline(resources):
    res = resources[2]

    desc = ("Returns a collection of the most recent Tweets posted by the "
            "user indicated\nby the screen_name or user_id parameters.\n"
            "User timelines belonging to protected users may only be "
            "requested when the\nauthenticated user either \"owns\" the "
            "timeline or is an approved follower of\nthe owner.\n"
            "The timeline returned is the equivalent of the one seen when "
            "you view a user's\nprofile on twitter.com.\nThis method can only "
            "return up to 3,200 of a user's most recent Tweets. Native\n"
            "retweets of other statuses by the user is included in this "
            "total, regardless\nof whether include_rts is set to false "
            "when requesting this resource.\n")
    assert res.description.raw == desc
