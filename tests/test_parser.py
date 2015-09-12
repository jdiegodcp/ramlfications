# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB
from __future__ import absolute_import, division, print_function

import os

import pytest
import xmltodict

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
    assert root.uri_params[0].description is None
    assert not hasattr(root.uri_params[0].description, "raw")
    assert not hasattr(root.uri_params[0].description, "html")
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
    thingy_json_schema = {'Thingy': {'name': 'New Thingy', 'public': False}}
    assert thingy_json_schema == root.schemas[0]

    thingy_xsd_schema = {
        'ThingyXsd': {
            'xs:schema': {
                '@attributeFormDefault': 'unqualified',
                '@elementFormDefault': 'qualified',
                '@xmlns:xs': 'http://www.w3.org/2001/XMLSchema',
                'xs:element': {
                    '@name': 'thingy',
                    '@type': 'thingyType'
                },
                'xs:complexType': {
                    '@name': 'thingyType',
                    'xs:sequence': {
                        'xs:element': {
                            '@type': 'xs:string',
                            '@name': 'name',
                            '@minOccurs': '1',
                            '@maxOccurs': '1'
                        }
                    }
                }
            }
        }
    }
    assert thingy_xsd_schema == root.schemas[1]

    thingy_xsd_list_schema = {
        'ThingyListXsd': {
            'xs:schema': {
                '@attributeFormDefault': 'unqualified',
                '@elementFormDefault': 'qualified',
                '@xmlns:xs': 'http://www.w3.org/2001/XMLSchema',
                'xs:include': {
                    '@schemaLocation': './thingy.xsd'
                },
                'xs:element': {
                    '@name': 'thingies',
                    'xs:complexType': {
                        'xs:sequence': {
                            '@minOccurs': '0',
                            '@maxOccurs': 'unbounded',
                            'xs:element': {
                                '@type': 'thingyType',
                                '@name': 'thingy'
                            }
                        }
                    }
                }
            }
        }
    }
    assert thingy_xsd_list_schema == root.schemas[2]


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
    assert len(sec_schemes) == 3
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


def test_security_scheme_no_desc(sec_schemes):
    no_desc = sec_schemes[2]

    assert no_desc.name == "no_desc"
    assert no_desc.description is None


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


def test_resource_type_empty_mapping():
    raml_file = os.path.join(EXAMPLES + "empty-mapping-resource-type.raml")
    loaded_raml_file = load_file(raml_file)
    config = setup_config(EXAMPLES + "test-config.ini")
    config['validate'] = False
    api = pw.parse_raml(loaded_raml_file, config)

    assert len(api.resource_types) == 1

    res = api.resource_types[0]

    assert res.name == "emptyType"
    assert res.raw == {}


def test_resource_type_empty_mapping_headers():
    raml_file = os.path.join(EXAMPLES + "empty-mapping.raml")
    loaded_raml_file = load_file(raml_file)
    config = setup_config(EXAMPLES + "test-config.ini")
    config['validate'] = False
    api = pw.parse_raml(loaded_raml_file, config)

    base_res_type = api.resource_types[0]

    assert len(base_res_type.headers) == 3
    assert base_res_type.headers[-1].description is None


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

    abs_uri = "http://{subdomain}.example.com/v1/{communityPath}/widgets/{id}"
    assert resources[1].absolute_uri == abs_uri
    assert resources[1].media_type == "application/xml"
    assert resources[1].protocols == ["HTTP"]

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

    res = resources[-6]
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
    assert res.responses[0].body[1].mime_type == "text/xml"
    assert len(res.responses[0].body) == 2

    json_schema = {
        "$schema": "http://json-schema.org/draft-03/schema",
        "type": "array",
        "items": {
            "$ref": "schemas/thingy.json"
        }
    }
    assert res.responses[0].body[0].schema == json_schema
    assert res.responses[0].body[1].schema == 'ThingyListXsd'

    res = resources[10]
    headers = [h.name for h in res.responses[0].headers]
    assert sorted(["X-search-header", "X-another-header"]) == sorted(headers)

    schema = res.responses[0].body[0].schema
    assert schema == {"name": "the search body"}

    schema = res.responses[0].body[1].schema
    assert schema == {}
    example = res.responses[0].body[1].example
    assert example == {}

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


def test_resource_response_no_desc():
    raml_file = os.path.join(EXAMPLES + "empty-mapping.raml")
    loaded_raml_file = load_file(raml_file)
    config = setup_config(EXAMPLES + "test-config.ini")
    config['validate'] = False
    api = pw.parse_raml(loaded_raml_file, config)

    res = api.resources[-1]
    response = res.responses[-1]

    assert response.code == 204
    assert response.description is None


@pytest.fixture(scope="session")
def inherited_resources():
    raml_file = os.path.join(EXAMPLES, "resource-type-inherited.raml")
    loaded_raml = load_file(raml_file)
    config = setup_config(EXAMPLES + "test-config.ini")
    config['validate'] = False
    return pw.parse_raml(loaded_raml, config)


def test_resource_inherits_type(inherited_resources):
    assert len(inherited_resources.resources) == 6
    res = inherited_resources.resources[0]
    assert res.type == "inheritgetmethod"
    assert res.method == "get"
    assert len(res.headers) == 1
    assert len(res.body) == 1
    assert len(res.responses) == 2
    assert len(res.query_params) == 1

    exp_desc = ("This description should be inherited when applied to "
                "resources")
    assert res.description.raw == exp_desc

    h = res.headers[0]
    assert h.name == "X-Inherited-Header"
    assert h.description.raw == "This header should be inherited"

    b = res.body[0]
    assert b.mime_type == "application/json"
    # lazy checking
    assert b.schema is not None
    assert b.example is not None

    q = res.query_params[0]
    assert q.name == "inherited_param"
    assert q.display_name == "inherited query parameter for a get method"
    assert q.type == "string"
    assert q.description.raw == "description for inherited query param"
    assert q.example == "fooBar"
    assert q.min_length == 1
    assert q.max_length == 50
    assert q.required is True


def test_resource_inherits_type_optional_post(inherited_resources):
    assert len(inherited_resources.resources) == 6
    res = inherited_resources.resources[1]
    assert res.type == "inheritgetoptionalmethod"
    assert res.method == "post"
    assert res.headers is None
    assert res.query_params is None
    assert res.description.raw == "post some foobar"


def test_resource_inherits_type_optional_get(inherited_resources):
    # make sure that optional resource type methods are not inherited if not
    # explicitly included in resource (unless no methods defined)
    assert len(inherited_resources.resources) == 6
    res = inherited_resources.resources[2]
    assert res.type == "inheritgetoptionalmethod"
    assert res.method == "get"
    assert len(res.headers) == 2
    assert len(res.query_params) == 1

    desc = ("This description should be inherited when applied to resources "
            "with get methods")
    assert res.description.raw == desc


def test_resource_inherits_get(inherited_resources):
    assert len(inherited_resources.resources) == 6
    post_res = inherited_resources.resources[3]
    get_res = inherited_resources.resources[4]

    assert get_res.method == "get"
    assert len(get_res.headers) == 1
    assert len(get_res.body) == 1
    assert len(get_res.responses) == 2
    assert len(get_res.query_params) == 1

    h = get_res.headers[0]
    assert h.name == "X-Inherited-Header"
    assert h.description.raw == "This header should be inherited"

    b = get_res.body[0]
    assert b.mime_type == "application/json"
    # lazy checking
    assert b.schema is not None
    assert b.example is not None

    q = get_res.query_params[0]
    assert q.name == "inherited_param"
    assert q.display_name == "inherited query parameter for a get method"
    assert q.type == "string"
    assert q.description.raw == "description for inherited query param"
    assert q.example == "fooBar"
    assert q.min_length == 1
    assert q.max_length == 50
    assert q.required is True

    assert post_res.method == "post"
    assert post_res.description.raw == "post some more foobar"


def test_resource_inherited_no_overwrite(inherited_resources):
    # make sure that if resource inherits a resource type, and explicitly
    # defines properties that are defined in the resource type, the
    # properties in the resource take preference
    assert len(inherited_resources.resources) == 6
    res = inherited_resources.resources[5]

    assert res.method == "get"
    assert len(res.query_params) == 2

    desc = "This method-level description should be used"
    assert res.description.raw == desc

    # test query params
    first_param = res.query_params[0]
    second_param = res.query_params[1]

    assert first_param.name == "inherited"
    assert first_param.description.raw == "An inherited parameter"

    assert second_param.name == "overwritten"
    desc = "This query param description should be used"
    assert second_param.description.raw == desc

    # test form params
    first_param = res.form_params[0]

    desc = "This description should be inherited"
    assert first_param.description.raw == desc

    example = "This example for the overwritten form param should be used"
    assert first_param.example == example

    assert first_param.type == "string"
    assert first_param.min_length == 1
    assert first_param.max_length == 5

    # test headers
    first_header = res.headers[0]
    second_header = res.headers[1]

    assert first_header.name == "X-Inherited-Header"
    assert first_header.description.raw == "this header is inherited"

    assert second_header.name == "X-Overwritten-Header"
    desc = "This header description should be used"
    assert second_header.description.raw == desc
    assert second_header.required

    # test body
    first_body = res.body[0]
    second_body = res.body[1]

    assert first_body.mime_type == "application/json"

    schema = {
        "$schema": "http://json-schema.org/draft-03/schema",
        "type": "object",
        "properties": {
            "inherited": {
                "description": "this schema should be inherited"
            }
        }
    }
    example = {"inherited": "yes please!"}
    assert first_body.schema == schema
    assert first_body.example == example

    assert second_body.mime_type == "text/xml"

    schema = ("<xs:schema attributeFormDefault='unqualified' "
              "elementFormDefault='qualified' "
              "xmlns:xs='http://www.w3.org/2001/XMLSchema'>"
              "<xs:include schemaLocation='./thingy.xsd'/>"
              "<xs:element name='thingies'><xs:complexType>"
              "<xs:sequence minOccurs='0' maxOccurs='unbounded'>"
              "<xs:element type='thingyType' name='thingy'/>"
              "</xs:sequence></xs:complexType></xs:element></xs:schema>")
    schema = xmltodict.parse(schema)

    example = ("<thingies><thingy><name>Successfully overwrote body XML "
               "example</name></thingy></thingies>")
    example = xmltodict.parse(example)
    assert second_body.schema == schema
    assert second_body.example == example

    # test responses
    first_resp = res.responses[0]
    second_resp = res.responses[1]

    assert first_resp.code == 200

    desc = "overwriting the 200 response description"
    assert first_resp.description.raw == desc
    assert len(first_resp.headers) == 2

    first_header = first_resp.headers[0]
    second_header = first_resp.headers[1]

    assert first_header.name == "X-Inherited-Success"
    desc = "inherited success response header"
    assert first_header.description.raw == desc

    assert second_header.name == "X-Overwritten-Success"
    desc = "overwritten success response header"
    assert second_header.description.raw == desc

    assert second_resp.code == 201
    assert second_resp.body[0].mime_type == "application/json"
    example = {"description": "overwritten description of 201 body example"}
    assert second_resp.body[0].example == example


@pytest.fixture(scope="session")
def resource_protocol():
    raml_file = os.path.join(EXAMPLES, "protocols.raml")
    loaded_raml = load_file(raml_file)
    config = setup_config(EXAMPLES + "test-config.ini")
    config['validate'] = False
    return pw.parse_raml(loaded_raml, config)


def test_overwrite_protocol(resource_protocol):
    # if a resource explicitly defines a protocol, *that*
    # should be reflected in the absolute URI
    api = resource_protocol
    assert api.protocols == ["HTTPS"]
    assert api.base_uri == "https://api.spotify.com/v1"

    res = api.resources
    assert len(res) == 2

    first = res[0]
    second = res[1]

    assert first.display_name == "several-tracks"
    assert first.protocols == ["HTTP"]
    assert second.display_name == "track"
    assert second.protocols == ["HTTP"]


#####
# Test Includes parsing
#####
@pytest.fixture(scope="session")
def xml_includes():
    raml_file = os.path.join(EXAMPLES + "xsd_includes.raml")
    loaded_raml_file = load_file(raml_file)
    config = setup_config(EXAMPLES + "test-config.ini")
    return pw.parse_raml(loaded_raml_file, config)


def test_includes_xml(xml_includes):
    api = xml_includes
    assert api.title == "Sample API Demo - XSD Includes"
    assert api.version == "v1"
    assert api.schemas == [{
        "xml": {
            "root": {
                "false": "true",
                "name": "foo",
            }
        },
    }]


@pytest.fixture(scope="session")
def json_includes():
    raml_file = os.path.join(EXAMPLES + "json_includes.raml")
    loaded_raml_file = load_file(raml_file)
    config = setup_config(EXAMPLES + "test-config.ini")
    return pw.parse_raml(loaded_raml_file, config)


def test_includes_json(json_includes):
    api = json_includes
    assert api.title == "Sample API Demo - JSON Includes"
    assert api.version == "v1"
    assert api.schemas == [{
        "json": {
            "false": True,
            "name": "foo",
        },
    }]


@pytest.fixture(scope="session")
def md_includes():
    raml_file = os.path.join(EXAMPLES + "md_includes.raml")
    loaded_raml_file = load_file(raml_file)
    config = setup_config(EXAMPLES + "test-config.ini")
    return pw.parse_raml(loaded_raml_file, config)


def test_includes_md(md_includes):
    api = md_includes
    assert api.title == "Sample API Demo - Markdown Includes"
    assert api.version == "v1"
    markdown_raw = """## Foo

*Bacon ipsum dolor* amet pork belly _doner_ rump brisket. [Cupim jerky \
shoulder][0] ball tip, jowl bacon meatloaf shank kielbasa turducken corned \
beef beef turkey porchetta.

### Doner meatball pork belly andouille drumstick sirloin

Porchetta picanha tail sirloin kielbasa, pig meatball short ribs drumstick \
jowl. Brisket swine spare ribs picanha t-bone. Ball tip beef tenderloin jowl \
doner andouille cupim meatball. Porchetta hamburger filet mignon jerky flank, \
meatball salami beef cow venison tail ball tip pork belly.

[0]: https://baconipsum.com/?paras=1&type=all-meat&start-with-lorem=1
"""
    assert api.documentation[0].content.raw == markdown_raw

    markdown_html = """<h2>Foo</h2>

<p><em>Bacon ipsum dolor</em> amet pork belly <em>doner</em> rump brisket. \
<a href="https://baconipsum.com/?paras=1&amp;type=all-meat&amp;start-with-\
lorem=1">Cupim jerky shoulder</a> ball tip, jowl bacon meatloaf shank \
kielbasa turducken corned beef beef turkey porchetta.</p>

<h3>Doner meatball pork belly andouille drumstick sirloin</h3>

<p>Porchetta picanha tail sirloin kielbasa, pig meatball short ribs drumstick \
jowl. Brisket swine spare ribs picanha t-bone. Ball tip beef tenderloin jowl \
doner andouille cupim meatball. Porchetta hamburger filet mignon jerky flank, \
meatball salami beef cow venison tail ball tip pork belly.</p>
"""
    assert api.documentation[0].content.html == markdown_html
