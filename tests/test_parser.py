#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

import json
import os

import pytest

from ramlfications import loader
from ramlfications import parser as pw
from ramlfications.raml import RootNode, ResourceTypeNode, TraitNode
from .base import EXAMPLES


@pytest.fixture
def loaded_raml():
    raml_file = os.path.join(EXAMPLES + "complete-valid-example.raml")
    return loader.RAMLLoader().load(raml_file)


@pytest.fixture
def root():
    raml_file = os.path.join(EXAMPLES + "complete-valid-example.raml")
    loaded_raml_file = loader.RAMLLoader().load(raml_file)
    return pw.create_root(loaded_raml_file)


def test_parse_raml(loaded_raml):
    root = pw.parse_raml(loaded_raml)
    assert isinstance(root, RootNode)


def test_create_root(root):
    assert isinstance(root, RootNode)


def test_base_uri(root):
    expected = "https://{subdomain}.spotify.com/v1/{communityPath}"
    assert expected == root.base_uri


def test_protocols(root):
    expected = ["HTTPS"]
    assert expected == root.protocols


def test_docs(root):
    exp_title = "Spotify Web API Docs"
    exp_content = ("Welcome to the _Spotify Web API_ demo specification. "
                   "This is *not* the complete API\nspecification, and is "
                   "meant for testing purposes within this RAML specification."
                   "\nFor more information about how to use the API, check "
                   "out [developer\n site]"
                   "(https://developer.spotify.com/web-api/).\n")

    assert exp_title == root.docs[0].title
    assert exp_content == root.docs[0].content


def test_base_uri_params(root):
    exp_name = "subdomain"
    exp_desc = "subdomain of API"
    exp_default = "api"

    assert exp_name == root.base_uri_params[0].name
    assert exp_desc == root.base_uri_params[0].description
    assert exp_default == root.base_uri_params[0].default


def test_uri_params(root):
    assert root.uri_params[0].name == "communityPath"
    assert root.uri_params[0].display_name == "Community Path"
    assert root.uri_params[0].type == "string"
    assert root.uri_params[0].min_length == 1
    assert root.uri_params[0].description is None
    assert root.uri_params[0].default is None
    assert root.uri_params[0].enum is None
    assert root.uri_params[0].example is None


def test_title(root):
    exp_name = "Spotify Web API Demo"
    assert exp_name == root.title


def test_version(root):
    exp_version = "v1"
    assert exp_version == root.version


def test_schemas(root):
    exp_schema = {'Playlist': {'name': 'New Playlist', 'public': False}}
    assert exp_schema == root.schemas[0]


def test_media_type(root):
    exp_media_type = "application/json"
    assert exp_media_type == root.media_type


@pytest.fixture
def api():
    raml_file = os.path.join(EXAMPLES + "complete-valid-example.raml")
    loaded_raml_file = loader.RAMLLoader().load(raml_file)
    return pw.parse_raml(loaded_raml_file)


#####
# Test Traits
#####
@pytest.fixture
def traits():
    raml_file = os.path.join(EXAMPLES + "complete-valid-example.raml")
    loaded_raml_file = loader.RAMLLoader().load(raml_file)
    api = pw.parse_raml(loaded_raml_file)
    return api.traits


def test_create_traits(api):
    for trait in api.traits:
        assert isinstance(trait, TraitNode)


def test_trait_query_params(traits):
    trait = traits[0]
    assert trait.name == "filterable"
    assert trait.usage == "Some description about using filterable"
    assert trait.query_params[0].name == "fields"
    assert trait.query_params[0].type == "string"
    assert trait.query_params[0].display_name == "Fields"

    example = "tracks.items(added_by.id,track(name,href,album(name,href)))"
    assert trait.query_params[0].example == example


def test_trait_headers(traits):
    trait = traits[0]
    assert trait.headers[0].name == "X-example-header"
    assert trait.headers[0].description == "An example of a trait header"


def test_trait_body(traits):
    trait = traits[0]
    assert trait.body[0].mime_type == "application/json"
    assert trait.body[0].schema == {"name": "string"}
    assert trait.body[0].example == {"name": "example body for trait"}


def test_trait_uri_params(traits):
    trait = traits[1]
    assert trait.uri_params[0].name == "limit"
    assert trait.uri_params[0].type == "integer"
    assert trait.uri_params[0].example == 10
    assert trait.uri_params[0].minimum == 0
    assert trait.uri_params[0].maximum == 50
    assert trait.uri_params[0].default == 20

    desc = "The maximum number of track objects to return"
    assert trait.uri_params[0].description == desc


def test_trait_form_params(traits):
    trait = traits[2]
    assert trait.form_params[0].name == "foo"
    assert trait.form_params[0].display_name == "Foo"
    assert trait.form_params[0].type == "string"
    assert trait.form_params[0].default == "bar"
    assert trait.form_params[0].min_length == 5
    assert trait.form_params[0].max_length == 50
    assert trait.form_params[0].description == "The Foo Form Field"

    trait_desc = "A description of a trait with form parameters"
    assert trait.description == trait_desc

    media_type = "application/x-www-form-urlencoded"
    assert trait.media_type == media_type


def test_trait_base_uri_params(traits):
    trait = traits[3]
    assert trait.base_uri_params[0].name == "communityPath"
    assert trait.base_uri_params[0].display_name == "Community Path trait"
    assert trait.base_uri_params[0].type == "string"
    assert trait.base_uri_params[0].example == "baz-community"

    param_desc = "The community path base URI trait"
    assert trait.base_uri_params[0].description == param_desc

    trait_desc = "A description of a trait with base URI parameters"
    assert trait.description == trait_desc


#####
# Test Resource Types
#####
@pytest.fixture
def resource_types():
    raml_file = os.path.join(EXAMPLES + "complete-valid-example.raml")
    loaded_raml_file = loader.RAMLLoader().load(raml_file)
    api = pw.parse_raml(loaded_raml_file)
    return api.resource_types


def test_create_resource_types(api):
    for res_type in api.resource_types:
        assert isinstance(res_type, ResourceTypeNode)


def test_resource_type(resource_types):
    resource_type = resource_types[0]
    assert resource_type.name == "base"
    assert resource_type.method == "get"
    assert resource_type.optional
    assert resource_type.is_ is None
    assert resource_type.traits is None

    header = resource_type.headers[0]
    assert header.name == "Accept"
    assert header.method == "get"
    assert header.type == "string"
    assert header.description == "Is used to set specified media type."
    assert header.example is None
    assert header.default is None
    assert header.required is False

    body = resource_type.body[0]
    assert body.mime_type == "application/json"
    assert body.schema == {"name": "string"}
    assert body.example == {"name": "Foo Bar"}
    assert body.form_params is None

    response = resource_type.responses[0]
    assert response.code == 403

    desc = ("API rate limit exceeded. See http://developer.spotify.com/"
            "web-api/#rate-limiting for details.\n")
    assert response.description == desc
    assert response.method == "get"

    resp_header = response.headers[0]
    assert resp_header.name == "X-waiting-period"

    resp_desc = ("The number of seconds to wait before you can attempt to "
                 "make a request again.\n")
    assert resp_header.description == resp_desc
    assert resp_header.type == "integer"
    assert resp_header.required

    # TODO: add types to Header object
    assert resp_header.minimum == 1
    assert resp_header.maximum == 3600
    assert resp_header.example == 34

    resp_body = response.body[0]
    assert resp_body.mime_type == "application/json"
    assert resp_body.schema == {"name": "string"}
    assert resp_body.example == {"name": "Foo Bar"}
    assert resp_body.form_params is None


def test_resource_type_method_protocol(resource_types):
    resource = resource_types[3]
    assert resource.name == "item"
    assert resource.protocols == ["HTTP"]


def test_resource_type_uri_params(resource_types):
    uri_param = resource_types[0].uri_params[0]
    assert uri_param.name == "mediaTypeExtension"

    desc = "Use .json to specify application/json media type."
    assert uri_param.description == desc
    assert uri_param.enum == [".json"]
    assert uri_param.min_length is None
    assert uri_param.param_type == "string"
    assert uri_param.required
    assert uri_param.default is None


def test_resource_type_query_params(resource_types):
    query_param = resource_types[4].query_params[0]
    assert query_param.name == "ids"
    assert query_param.description == "A comma-separated list of IDs"
    assert query_param.display_name == "Some sort of IDs"
    assert query_param.type == "string"
    assert query_param.required


def test_resource_type_form_params(resource_types):
    form_param = resource_types[5].form_params[0]
    assert form_param.name == "aFormParam"
    assert form_param.description == "An uncreative form parameter"
    assert form_param.display_name == "Some sort of Form Parameter"
    assert form_param.type == "string"
    assert form_param.required


def test_resource_type_base_uri_params(resource_types):
    base_uri_params = resource_types[6].base_uri_params[0]
    assert base_uri_params.name == "subdomain"

    desc = "subdomain for the baseUriType resource type"
    assert base_uri_params.description == desc

    assert base_uri_params.default == "fooBar"


def test_resource_type_properties(resource_types):
    another_example = resource_types[7]
    assert another_example.name == "anotherExample"

    desc = "Another Resource Type example"
    assert another_example.description == desc

    usage = "Some sort of usage description"
    assert another_example.usage == usage

    assert another_example.optional is False
    assert another_example.media_type == "text/xml"


def test_resource_type_inherited(resource_types):
    inherited = resource_types[8]
    assert inherited.type == "base"
    assert inherited.usage == "Some sort of usage text"
    assert inherited.display_name == "inherited example"

    inherited_response = inherited.responses[0]
    assert inherited_response.code == 403

    new_response = inherited.responses[1]
    assert new_response.code == 500


def test_resource_type_with_trait(resource_types):
    another_example = resource_types[7]
    assert another_example.is_ == ["filterable"]

    trait = another_example.traits[0]
    assert trait.name == "filterable"

    query_param = trait.query_params[0]
    assert query_param.name == "fields"
    assert query_param.display_name == "Fields"
    assert query_param.type == "string"

    desc = "A comma-separated list of fields to filter query"
    assert query_param.description == desc

    example = "tracks.items(added_by.id,track(name,href,album(name,href)))"
    assert query_param.example == example


def test_resource_type_secured_by(resource_types):
    another_example = resource_types[7]
    assert another_example.secured_by == ["oauth_2_0"]

    scheme = another_example.security_schemes[0]
    assert scheme.name == "oauth_2_0"
    assert scheme.type == "OAuth 2.0"

    desc = "Spotify supports OAuth 2.0 for authenticating all API requests.\n"
    assert scheme.description == desc

    desc_by = {
        "headers": {
            "Authorization": {
                "description": "Used to send a valid OAuth 2 access token.\n",
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
    assert scheme.described_by == desc_by

    settings = {
        "authorizationUri": "https://accounts.spotify.com/authorize",
        "accessTokenUri": "https://accounts.spotify.com/api/token",
        "authorizationGrants": ["code", "token"],
        "scopes": [
            "playlist-read-private",
            "playlist-modify-public",
            "playlist-modify-private",
            "user-library-read",
            "user-library-modify",
            "user-read-private",
            "user-read-email"
        ]
    }
    assert scheme.settings == settings


#####
# Test Resources
#####
@pytest.fixture
def resources():
    raml_file = os.path.join(EXAMPLES + "complete-valid-example.raml")
    loaded_raml_file = loader.RAMLLoader().load(raml_file)
    api = pw.parse_raml(loaded_raml_file)
    return api.resources


def test_resource_properties(resources):
    assert resources[0].name == "/albums"
    assert resources[0].display_name == "several-albums"
    assert resources[0].method == "get"
    assert resources[0].protocols == ["HTTPS"]

    assert resources[1].parent.name == "/albums"
    assert resources[1].path == "/albums/{id}"

    abs_uri = "https://{subdomain}.spotify.com/v1/{communityPath}/albums/{id}"
    assert resources[1].absolute_uri == abs_uri

    assert resources[2].is_ == ["paged"]
    assert resources[12].type == "collection"


def test_resource_no_method_properties(resources):
    assert resources[-2].method is None
    assert resources[-2].name == "/no_method_properties"

    assert resources[-1].parent.name == resources[-2].name
    assert resources[-1].method == "get"


def test_resource_headers(resources):
    assert resources[0].headers[0].name == "X-bogus-header"
    desc = "just an extra header for funsies"
    assert resources[0].headers[0].description == desc


def test_resource_inherited_properties(resources):
    res = resources[9]
    assert res.base_uri_params[0] == res.resource_type.base_uri_params[0]

    res = resources[-7]
    assert res.form_params[0] == res.resource_type.form_params[0]

    res = resources[11]
    assert res.is_ == ["protocolTrait"]
    assert res.traits[0].description == "A trait to assign a protocol"
    assert res.traits[0].protocols == ["HTTP"]


def test_resource_assigned_type(resources):
    res = resources[19]

    assert res.display_name == "playlist"
    assert res.method == "get"
    assert res.type == "item"

    assert res.uri_params[0] == res.resource_type.uri_params[0]
    assert res.headers[0] == res.resource_type.headers[0]
    assert res.body[0] == res.resource_type.body[0]
    assert res.responses[0] == res.resource_type.responses[0]
    assert len(res.headers) == 2
    assert res.headers[0].name == "Accept"
    assert res.headers[1].name == "X-example-header"

    res = resources[18]
    assert res.type == "collection"
    assert res.method == "post"
    assert res.form_params[0] == res.resource_type.form_params[0]

    res = resources[11]
    assert res.type == "queryParamType"
    assert res.method == "get"
    assert res.resource_type.query_params[0] == res.query_params[0]

    res = resources[9]
    assert res.type == "baseUriType"
    assert res.method == "get"
    assert res.base_uri_params[0] == res.resource_type.base_uri_params[0]

    res = resources[1]
    assert res.type == "protocolExampleType"
    assert res.resource_type.name == "protocolExampleType"
    assert res.protocols == res.resource_type.protocols


def test_resource_assigned_trait(resources):
    res = resources[10]

    assert res.name == "/search"
    assert res.is_ == ["paged"]
    assert res.traits[0].description == "A description of the paged trait"
    assert res.traits[0].media_type == "application/xml"
    assert res.uri_params == res.traits[0].uri_params


def test_resource_protocols(resources):
    res = resources[13]

    assert res.method == "put"
    assert res.name == "/tracks"

    assert res.protocols == ["HTTP"]

    res = resources[16]

    assert res.method == "get"
    assert res.name == "/users/{user_id}"
    assert res.protocols == ["HTTP"]


def test_resource_responses(resources):
    res = resources[17]

    assert res.responses[0].code == 200
    assert res.responses[0].body[0].mime_type == "application/json"

    schema = {
        "$schema": "http://json-schema.org/draft-03/schema",
        "type": "array",
        "items": {
            "$ref": "schemas/playlist.json"
        }
    }
    assert json.loads(res.responses[0].body[0].schema) == schema

    res = resources[-9]

    assert res.path == "/users/{user_id}/playlists/{playlist_id}"
    assert res.type == "item"
    assert res.responses[0] == res.resource_type.responses[0]
    assert len(res.responses[0].headers) == 1
    assert res.responses[0].headers[0].name == "X-waiting-period"
    assert res.responses[0].headers[0].type == "integer"
    assert res.responses[0].headers[0].minimum == 1
    assert res.responses[0].headers[0].maximum == 3600
    assert res.responses[0].headers[0].example == 34

    desc = ("The number of seconds to wait before you can attempt to make "
            "a request again.\n")
    assert res.responses[0].headers[0].description == desc

    res_response = res.responses[0].headers[0]
    res_type_resp = res.resource_type.responses[0].headers[0]
    assert res_response == res_type_resp

    res = resources[-11]

    assert res.display_name == "playlists"
    assert res.responses[0].code == 201
    assert res.responses[0].headers[0].name == "X-another-bogus-header"
    assert res.responses[0].headers[0].description == "A bogus header"
    assert res.responses[0].body[0].mime_type == "application/json"
    assert res.responses[0].body[0].schema == "Playlist"


def test_resource_base_uri_params(resources):
    res = resources[2]

    assert res.display_name == "album-tracks"
    assert res.base_uri_params[0].name == "subdomain"

    desc = "subdomain for the baseUriType resource type"
    assert res.base_uri_params[0].description == desc
    assert res.base_uri_params[0].default == "fooBar"

    res = resources[-13]

    assert res.display_name == "users-profile"
    assert res.base_uri_params[0].name == "subdomain"
    assert res.base_uri_params[0].default == "barFoo"

    desc = "a test base URI parameter for resource-level"
    assert res.base_uri_params[0].description == desc


def test_resource_form_params(resources):
    res = resources[-3]

    assert res.display_name == "formParamResource"
    assert res.description == "A example resource with form parameters"
    assert res.form_params[0].name == "foo"
    assert res.form_params[0].description == "Post some foo"
    assert res.form_params[0].type == "string"
    assert res.form_params[0].required
    assert res.form_params[0].min_length == 10
    assert res.form_params[0].max_length == 100

    assert res.form_params[1].name == "bar"
    assert res.form_params[1].description == "Post some bar"
    assert res.form_params[1].type == "string"
    assert res.form_params[1].required is False
    assert res.form_params[1].min_length == 15
    assert res.form_params[1].max_length == 150
    assert res.form_params[1].default == "aPostedBarExample"


def test_resource_security_scheme(resources):
    res = resources[17]
    assert res.method == "get"
    assert res.name == "/users/{user_id}/playlists"
    assert res.secured_by == [
        {"oauth_2_0": {"scopes": ["playlist-read-private"]}}
    ]
    assert res.security_schemes[0].name == "oauth_2_0"


def test_fill_params_resource_type(resources):
    res = resources[-4]
    assert res.name == "/fill_param_example"
    assert res.type == "parameterType"
    assert res.query_params[0].name == "foo"

    desc = ("Return /fill_param_example that have their foo "
            "matching the given value")
    assert res.query_params[0].description == desc

    assert res.query_params[1].name == "bar"

    desc = ("If no values match the value given for foo, "
            "use bar instead")
    assert res.query_params[1].name == desc
