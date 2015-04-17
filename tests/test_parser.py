# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

import os

import pytest

from ramlfications import parser as pw
from ramlfications.config import setup_config
from ramlfications.raml import RootNode, ResourceTypeNode, TraitNode
from ramlfications._helpers import load_file

from .base import EXAMPLES


@pytest.fixture(scope="session")
def loaded_raml():
    raml_file = os.path.join(EXAMPLES + "complete-valid-example.raml")
    return load_file(raml_file)


@pytest.fixture(scope="session")
def root():
    raml_file = os.path.join(EXAMPLES + "complete-valid-example.raml")
    loaded_raml_file = load_file(raml_file)
    config = setup_config(EXAMPLES + "test-config.ini")
    return pw.create_root(loaded_raml_file, config)


def test_parse_raml(loaded_raml):
    config = setup_config(EXAMPLES + "test-config.ini")
    root = pw.parse_raml(loaded_raml, config)
    assert isinstance(root, RootNode)


def test_create_root(root):
    assert isinstance(root, RootNode)


def test_base_uri(root):
    expected = "https://{subdomain}.example.com/v1/{communityPath}"
    assert expected == root.base_uri


def test_protocols(root):
    expected = ["HTTPS"]
    assert expected == root.protocols


def test_docs(root):
    exp_title = "Example Web API Docs"
    exp_content = ("Welcome to the _Example Web API_ demo specification. "
                   "This is *not* the complete API\nspecification, and is "
                   "meant for testing purposes within this RAML "
                   "specification.\n")

    assert exp_title == root.documentation[0].title.raw
    assert exp_title == repr(root.documentation[0].title)
    assert exp_content == root.documentation[0].content.raw
    assert exp_content == repr(root.documentation[0].content)

    title_html = "<p>Example Web API Docs</p>\n"
    content_html = ("<p>Welcome to the <em>Example Web API</em> demo "
                    "specification. This is <em>not</em> the complete API\n"
                    "specification, and is meant for testing purposes within "
                    "this RAML specification.</p>\n")
    assert title_html == root.documentation[0].title.html
    assert content_html == root.documentation[0].content.html


def test_base_uri_params(root):
    exp_name = "subdomain"
    exp_desc = "subdomain of API"
    exp_desc_html = "<p>subdomain of API</p>\n"
    exp_default = "api"

    assert exp_name == root.base_uri_params[0].name
    assert exp_desc == root.base_uri_params[0].description.raw
    assert exp_desc_html == root.base_uri_params[0].description.html
    assert exp_default == root.base_uri_params[0].default


def test_uri_params(root):
    assert root.uri_params[0].name == "communityPath"
    assert root.uri_params[0].display_name == "Community Path"
    assert root.uri_params[0].type == "string"
    assert root.uri_params[0].min_length == 1
    assert root.uri_params[0].description.raw is None
    assert root.uri_params[0].description.html is None
    assert root.uri_params[0].default is None
    assert root.uri_params[0].enum is None
    assert root.uri_params[0].example is None


def test_title(root):
    exp_name = "Example Web API"
    assert exp_name == root.title


def test_version(root):
    exp_version = "v1"
    assert exp_version == root.version


def test_schemas(root):
    exp_schema = {'Thingy': {'name': 'New Thingy', 'public': False}}
    assert exp_schema == root.schemas[0]


def test_media_type(root):
    exp_media_type = "application/json"
    assert exp_media_type == root.media_type


@pytest.fixture(scope="session")
def api():
    raml_file = os.path.join(EXAMPLES + "complete-valid-example.raml")
    loaded_raml_file = load_file(raml_file)
    config = setup_config(EXAMPLES + "test-config.ini")
    return pw.parse_raml(loaded_raml_file, config)


#####
# Test Security Schemes
#####
@pytest.fixture(scope="session")
def sec_schemes():
    raml_file = os.path.join(EXAMPLES + "complete-valid-example.raml")
    loaded_raml_file = load_file(raml_file)
    config = setup_config(EXAMPLES + "test-config.ini")
    api = pw.parse_raml(loaded_raml_file, config)
    return api.security_schemes


def test_create_security_schemes(sec_schemes):
    assert len(sec_schemes) == 2
    assert sec_schemes[0].name == "oauth_2_0"
    assert sec_schemes[0].type == "OAuth 2.0"

    desc = ("Example API supports OAuth 2.0 for authenticating all API "
            "requests.\n")
    assert sec_schemes[0].description.raw == desc

    assert len(sec_schemes[0].headers) == 2
    assert sec_schemes[0].headers[0].name == "Authorization"
    assert sec_schemes[0].headers[1].name == "X-Foo-Header"

    assert len(sec_schemes[0].responses) == 2
    assert sec_schemes[0].responses[0].code == 401

    desc = ("Bad or expired token. This can happen if the user revoked a "
            "token or\nthe access token has expired. You should "
            "re-authenticate the user.\n")
    assert sec_schemes[0].responses[0].description.raw == desc

    assert sec_schemes[0].responses[1].code == 403

    desc = ("Bad OAuth request (wrong consumer key, bad nonce, expired\n"
            "timestamp...). Unfortunately, re-authenticating the user won't "
            "help here.\n")
    assert sec_schemes[0].responses[1].description.raw == desc

    settings = {
        "authorizationUri": "https://accounts.example.com/authorize",
        "accessTokenUri": "https://accounts.example.com/api/token",
        "authorizationGrants": ["code", "token"],
        "scopes": [
            "user-public-profile",
            "user-email",
            "user-activity",
            "nsa-level-privacy"
        ]
    }
    assert sec_schemes[0].settings == settings


def test_create_security_schemes_custom(sec_schemes):
    custom = sec_schemes[1]

    assert custom.name == "custom_auth"
    assert custom.type == "Custom Auth"
    assert len(custom.uri_params) == 1
    assert len(custom.form_params) == 1
    assert len(custom.query_params) == 1
    assert len(custom.body) == 1

    assert custom.uri_params[0].name == "subDomain"
    assert custom.query_params[0].name == "fooQParam"
    assert custom.form_params[0].name == "fooFormParam"
    assert custom.body[0].mime_type == "application/x-www-form-urlencoded"

    assert custom.documentation[0].title.raw == "foo docs"
    assert custom.documentation[0].content.raw == "foo content"


#####
# Test Traits
#####
@pytest.fixture(scope="session")
def traits():
    raml_file = os.path.join(EXAMPLES + "complete-valid-example.raml")
    loaded_raml_file = load_file(raml_file)
    config = setup_config(EXAMPLES + "test-config.ini")
    api = pw.parse_raml(loaded_raml_file, config)
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

    example = "gizmos.items(added_by.id,gizmo(name,href,widget(name,href)))"
    assert trait.query_params[0].example == example


def test_trait_headers(traits):
    trait = traits[0]
    assert trait.headers[0].name == "X-example-header"
    assert trait.headers[0].description.raw == "An example of a trait header"
    html_desc = "<p>An example of a trait header</p>\n"
    assert trait.headers[0].description.html == html_desc


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

    desc = "The maximum number of gizmo objects to return"
    assert trait.uri_params[0].description.raw == desc
    assert repr(trait.uri_params[0].description) == desc

    desc_html = "<p>The maximum number of gizmo objects to return</p>\n"
    assert trait.uri_params[0].description.html == desc_html


def test_trait_form_params(traits):
    trait = traits[2]
    assert trait.form_params[0].name == "foo"
    assert trait.form_params[0].display_name == "Foo"
    assert trait.form_params[0].type == "string"
    assert trait.form_params[0].default == "bar"
    assert trait.form_params[0].min_length == 5
    assert trait.form_params[0].max_length == 50
    assert trait.form_params[0].description.raw == "The Foo Form Field"

    trait_desc = "A description of a trait with form parameters"
    assert trait.description.raw == trait_desc
    media_type = "application/x-www-form-urlencoded"
    assert trait.media_type == media_type


def test_trait_base_uri_params(traits):
    trait = traits[3]
    assert trait.base_uri_params[0].name == "communityPath"
    assert trait.base_uri_params[0].display_name == "Community Path trait"
    assert trait.base_uri_params[0].type == "string"
    assert trait.base_uri_params[0].example == "baz-community"

    param_desc = "The community path base URI trait"
    assert trait.base_uri_params[0].description.raw == param_desc

    trait_desc = "A description of a trait with base URI parameters"
    assert trait.description.raw == trait_desc


#####
# Test Resource Types
#####
@pytest.fixture(scope="session")
def resource_types():
    raml_file = os.path.join(EXAMPLES + "complete-valid-example.raml")
    loaded_raml_file = load_file(raml_file)
    config = setup_config(EXAMPLES + "test-config.ini")
    api = pw.parse_raml(loaded_raml_file, config)
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
    assert header.description.raw == "Is used to set specified media type."
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

    desc = ("API rate limit exceeded.\n")
    assert response.description.raw == desc
    assert response.method == "get"

    resp_header = response.headers[0]
    assert resp_header.name == "X-waiting-period"

    resp_desc = ("The number of seconds to wait before you can attempt to "
                 "make a request again.\n")
    assert resp_header.description.raw == resp_desc
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
    assert uri_param.description.raw == desc
    assert uri_param.enum == [".json"]
    assert uri_param.min_length is None
    assert uri_param.type == "string"
    assert uri_param.required
    assert uri_param.default is None


def test_resource_type_query_params(resource_types):
    query_param = resource_types[4].query_params[0]
    assert query_param.name == "ids"
    assert query_param.description.raw == "A comma-separated list of IDs"
    assert query_param.display_name == "Some sort of IDs"
    assert query_param.type == "string"
    assert query_param.required


def test_resource_type_form_params(resource_types):
    form_param = resource_types[5].form_params[0]
    assert form_param.name == "aFormParam"
    assert form_param.description.raw == "An uncreative form parameter"
    assert form_param.display_name == "Some sort of Form Parameter"
    assert form_param.type == "string"
    assert form_param.required


def test_resource_type_base_uri_params(resource_types):
    base_uri_params = resource_types[6].base_uri_params[0]
    assert base_uri_params.name == "subdomain"

    desc = "subdomain for the baseUriType resource type"
    assert base_uri_params.description.raw == desc

    assert base_uri_params.default == "fooBar"


def test_resource_type_properties(resource_types):
    another_example = resource_types[7]
    assert another_example.name == "anotherExample"

    desc = "Another Resource Type example"
    assert another_example.description.raw == desc

    usage = "Some sort of usage description"
    assert another_example.usage == usage

    assert another_example.optional is False
    assert another_example.media_type == "text/xml"


def test_resource_type_inherited(resource_types):
    inherited = resource_types[8]
    assert inherited.type == "base"
    assert inherited.usage == "Some sort of usage text"
    assert inherited.display_name == "inherited example"

    inherited_response = inherited.responses[1]
    assert inherited_response.code == 403

    new_response = inherited.responses[2]
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
    assert query_param.description.raw == desc

    example = "gizmos.items(added_by.id,gizmo(name,href,widget(name,href)))"
    assert query_param.example == example


def test_resource_type_secured_by(resource_types):
    another_example = resource_types[7]
    assert another_example.secured_by == ["oauth_2_0"]

    scheme = another_example.security_schemes[0]
    assert scheme.name == "oauth_2_0"
    assert scheme.type == "OAuth 2.0"

    desc = ("Example API supports OAuth 2.0 for authenticating all API "
            "requests.\n")
    assert scheme.description.raw == desc

    desc_by = {
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
    assert scheme.described_by == desc_by

    settings = {
        "authorizationUri": "https://accounts.example.com/authorize",
        "accessTokenUri": "https://accounts.example.com/api/token",
        "authorizationGrants": ["code", "token"],
        "scopes": [
            "user-public-profile",
            "user-email",
            "user-activity",
            "nsa-level-privacy"
        ]
    }
    assert scheme.settings == settings


#####
# Test Resources
#####
@pytest.fixture(scope="session")
def resources():
    raml_file = os.path.join(EXAMPLES + "complete-valid-example.raml")
    loaded_raml_file = load_file(raml_file)
    config = setup_config(EXAMPLES + "test-config.ini")
    api = pw.parse_raml(loaded_raml_file, config)
    return api.resources


def test_resource_properties(resources):
    assert resources[0].name == "/widgets"
    assert resources[0].display_name == "several-widgets"
    assert resources[0].method == "get"
    assert resources[0].protocols == ["HTTPS"]
    assert resources[0].media_type == "application/xml"

    assert resources[1].parent.name == "/widgets"
    assert resources[1].path == "/widgets/{id}"

    abs_uri = "https://{subdomain}.example.com/v1/{communityPath}/widgets/{id}"
    assert resources[1].absolute_uri == abs_uri
    assert resources[1].media_type == "application/xml"

    assert resources[2].is_ == ["paged"]
    assert resources[2].media_type == "application/xml"
    assert resources[12].type == "collection"

    assert resources[3].media_type == "text/xml"


def test_resource_no_method_properties(resources):
    assert resources[-2].method is None
    assert resources[-2].name == "/no_method_properties"

    assert resources[-1].parent.name == resources[-2].name
    assert resources[-1].method == "get"


def test_resource_headers(resources):
    assert resources[0].headers[0].name == "X-bogus-header"
    desc = "just an extra header for funsies"
    assert resources[0].headers[0].description.raw == desc


def test_resource_inherited_properties(resources):
    res = resources[9]
    assert res.base_uri_params[0] == res.resource_type.base_uri_params[0]

    res = resources[-7]
    assert res.form_params[0] == res.resource_type.form_params[0]

    res = resources[11]
    assert res.is_ == ["protocolTrait"]
    assert res.traits[0].description.raw == "A trait to assign a protocol"
    assert res.traits[0].protocols == ["HTTP"]


def test_resource_assigned_type(resources):
    res = resources[19]

    assert res.display_name == "thingy"
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
    assert res.traits[0].description.raw == "A description of the paged trait"
    assert res.traits[0].media_type == "application/xml"

    params = [p.name for p in res.uri_params]
    t_params = [p.name for p in res.traits[0].uri_params]

    for t in t_params:
        assert t in params


def test_resource_protocols(resources):
    res = resources[13]

    assert res.method == "put"
    assert res.name == "/widgets"

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
            "$ref": "schemas/thingy.json"
        }
    }
    assert res.responses[0].body[0].schema == schema

    res = resources[10]
    headers = [h.name for h in res.responses[0].headers]
    assert ["X-search-header", "X-another-header"] == headers
    body = res.responses[0].body[0].schema
    assert body == {"name": "the search body"}
    body = res.responses[0].body[1].schema
    assert body == {"name": "an schema body"}

    res = resources[19]
    headers = [h.name for h in res.responses[0].headers]
    assert "X-waiting-period" in headers
    body = res.responses[0].body[0].schema
    assert body == {"name": "string"}
    codes = [r.code for r in res.responses]
    assert [200, 403] == sorted(codes)

    res = resources[-9]

    assert res.path == "/users/{user_id}/thingys/{thingy_id}"
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
    assert res.responses[0].headers[0].description.raw == desc

    res_response = res.responses[0].headers[0]
    res_type_resp = res.resource_type.responses[0].headers[0]
    assert res_response == res_type_resp

    res = resources[-10]

    assert res.display_name == "thingys"
    assert res.responses[0].code == 201
    assert res.responses[0].headers[0].name == "X-another-bogus-header"
    assert res.responses[0].headers[0].description.raw == "A bogus header"
    assert res.responses[0].body[0].mime_type == "application/json"
    assert res.responses[0].body[0].schema == "Thingy"


def test_resource_base_uri_params(resources):
    res = resources[2]

    assert res.display_name == "widget-gizmos"
    assert res.base_uri_params[0].name == "subdomain"

    desc = "subdomain for the baseUriType resource type"
    assert res.base_uri_params[0].description.raw == desc
    assert res.base_uri_params[0].default == "fooBar"

    res = resources[-12]
    assert len(res.base_uri_params) == 1
    assert res.display_name == "users-profile"
    assert res.base_uri_params[0].name == "subdomain"
    assert res.base_uri_params[0].default == "barFoo"

    desc = "a test base URI parameter for resource-level"
    assert res.base_uri_params[0].description.raw == desc


def test_resource_form_params(resources):
    res = resources[-3]

    assert res.display_name == "formParamResource"
    assert res.description.raw == "A example resource with form parameters"
    assert res.form_params[0].name == "foo"
    assert res.form_params[0].description.raw == "Post some foo"
    assert res.form_params[0].type == "string"
    assert res.form_params[0].required
    assert res.form_params[0].min_length == 10
    assert res.form_params[0].max_length == 100

    assert res.form_params[1].name == "bar"
    assert res.form_params[1].description.raw == "Post some bar"
    assert res.form_params[1].type == "string"
    assert res.form_params[1].required is False
    assert res.form_params[1].min_length == 15
    assert res.form_params[1].max_length == 150
    assert res.form_params[1].default == "aPostedBarExample"


def test_resource_security_scheme(resources):
    res = resources[17]
    assert res.method == "get"
    assert res.name == "/users/{user_id}/thingys"
    assert res.secured_by == [
        {"oauth_2_0": {"scopes": ["thingy-read-private"]}}
    ]
    assert res.security_schemes[0].name == "oauth_2_0"


def test_resource_inherit_parent(resources):
    res = resources[2]
    assert len(res.uri_params) == 4
