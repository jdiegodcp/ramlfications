# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB
from __future__ import absolute_import, division, print_function

import os

import pytest
import xmltodict

from ramlfications import parser as pw
from ramlfications.config import setup_config
from ramlfications.raml import RootNode, ResourceTypeNode, TraitNode
from ramlfications.utils import load_file

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
    trait = traits[4]
    assert trait.uri_params[0].name == "communityPath"
    assert trait.uri_params[0].type == "string"
    assert trait.uri_params[0].example == 'baz-community'

    desc = "The community path URI params trait"
    assert trait.uri_params[0].description.raw == desc
    assert repr(trait.uri_params[0].description) == desc

    desc_html = "<p>The community path URI params trait</p>\n"
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


@pytest.fixture(scope="session")
def trait_parameters():
    raml_file = os.path.join(EXAMPLES + "resource-type-trait-parameters.raml")
    loaded_raml_file = load_file(raml_file)
    config = setup_config(EXAMPLES + "test-config.ini")
    api = pw.parse_raml(loaded_raml_file, config)
    return api


def test_inherited_assigned_trait_params_books(trait_parameters):
    res = trait_parameters.resources[0]

    assert res.name == "/books"
    assert res.method == "get"
    assert len(res.traits) == 2
    assert len(res.query_params) == 4
    assert len(res.headers) == 1
    assert len(res.body) == 1
    assert len(res.responses) == 1

    q_param = res.query_params[1]
    assert q_param.name == "access_token"
    assert q_param.description.raw == "A valid access_token is required"

    q_param = res.query_params[0]
    assert q_param.name == "numPages"
    desc = "The number of pages to return, not to exceed 10"
    assert q_param.description.raw == desc

    header = res.headers[0]
    assert header.name == "x-some-header"
    assert header.description.raw == "x-some-header is required here"

    body = res.body[0]
    assert body.mime_type == "application/json"
    assert body.schema == "foo-schema"

    resp = res.responses[0]
    assert resp.code == 200
    assert resp.method == 'get'
    assert resp.description.raw == "No more than 10 pages returned"
    assert len(resp.headers) == 1

    resp_headers = resp.headers[0]
    assert resp_headers.name == "x-another-header"
    desc = "some description for x-another-header"
    assert resp_headers.description.raw == desc


def test_inherited_assigned_trait_params_articles(trait_parameters):
    res = trait_parameters.resources[1]

    assert res.name == "/articles"
    assert res.method == "get"
    assert len(res.traits) == 2
    assert len(res.query_params) == 4
    assert len(res.headers) == 1
    assert len(res.body) == 1
    assert len(res.responses) == 1

    q_param = res.query_params[1]
    assert q_param.name == "foo_token"
    assert q_param.description.raw == "A valid foo_token is required"

    q_param = res.query_params[0]
    assert q_param.name == "numPages"
    desc = "The number of pages to return, not to exceed 20"
    assert q_param.description.raw == desc

    header = res.headers[0]
    assert header.name == "x-foo-header"
    assert header.description.raw == "x-foo-header is required here"

    body = res.body[0]
    assert body.mime_type == "application/json"
    assert body.schema == "bar-schema"

    resp = res.responses[0]
    assert resp.code == 200
    assert resp.description.raw == "No more than 20 pages returned"
    assert len(resp.headers) == 1

    resp_headers = resp.headers[0]
    assert resp_headers.name == "x-another-foo-header"
    desc = "some description for x-another-foo-header"
    assert resp_headers.description.raw == desc


def test_inherited_assigned_trait_params_videos(trait_parameters):
    res = trait_parameters.resources[2]

    assert res.name == "/videos"
    assert res.method == "get"
    assert len(res.traits) == 2
    assert len(res.query_params) == 4
    assert len(res.headers) == 1
    assert len(res.body) == 1
    assert len(res.responses) == 1

    q_param = res.query_params[1]
    assert q_param.name == "bar_token"
    assert q_param.description.raw == "A valid bar_token is required"

    q_param = res.query_params[0]
    assert q_param.name == "numPages"
    desc = "The number of pages to return, not to exceed 30"
    assert q_param.description.raw == desc

    header = res.headers[0]
    assert header.name == "x-bar-header"
    assert header.description.raw == "x-bar-header is required here"

    body = res.body[0]
    assert body.mime_type == "application/json"
    assert body.schema == "baz-schema"

    resp = res.responses[0]
    assert resp.code == 200
    assert resp.description.raw == "No more than 30 pages returned"
    assert len(resp.headers) == 1

    resp_headers = resp.headers[0]
    assert resp_headers.name == "x-another-bar-header"
    desc = "some description for x-another-bar-header"
    assert resp_headers.description.raw == desc


def test_assigned_trait_params(trait_parameters):
    res = trait_parameters.resources[0]
    assert len(res.traits) == 2

    secured = res.traits[0]
    assert secured.name == "secured"
    assert len(secured.query_params) == 1
    assert len(secured.headers) == 1
    assert len(secured.body) == 1
    assert not secured.responses
    assert not secured.uri_params

    q_param = secured.query_params[0]
    assert q_param.name == "<<tokenName>>"
    assert q_param.description.raw == "A valid <<tokenName>> is required"

    header = secured.headers[0]
    assert header.name == "<<aHeaderName>>"
    assert header.description.raw == "<<aHeaderName>> is required here"

    body = secured.body[0]
    assert body.mime_type == "application/json"
    assert body.schema == "<<schemaName>>"

    paged = res.traits[1]
    assert paged.name == "paged"
    assert len(paged.query_params) == 1
    assert len(paged.responses) == 1
    assert not paged.headers
    assert not paged.uri_params

    q_param = paged.query_params[0]
    assert q_param.name == "numPages"
    desc = "The number of pages to return, not to exceed <<maxPages>>"
    assert q_param.description.raw == desc

    resp = paged.responses[0]
    assert resp.code == 200
    assert resp.description.raw == "No more than <<maxPages>> pages returned"
    assert len(resp.headers) == 1

    assert resp.headers[0].name == "<<anotherHeader>>"
    desc = "some description for <<anotherHeader>>"
    assert resp.headers[0].description.raw == desc


# make sure root trait params are not changed after processing
# all the `<< parameter >>` substitution
def test_root_trait_params(trait_parameters):
    traits = trait_parameters.traits
    assert len(traits) == 2

    secured = traits[0]
    assert secured.name == "secured"
    assert len(secured.query_params) == 1
    assert len(secured.headers) == 1
    assert len(secured.body) == 1
    assert not secured.responses
    assert not secured.uri_params

    q_param = secured.query_params[0]
    assert q_param.name == "<<tokenName>>"
    assert q_param.description.raw == "A valid <<tokenName>> is required"

    header = secured.headers[0]
    assert header.name == "<<aHeaderName>>"
    assert header.description.raw == "<<aHeaderName>> is required here"

    body = secured.body[0]
    assert body.mime_type == "application/json"
    assert body.schema == "<<schemaName>>"

    paged = traits[1]
    assert paged.name == "paged"
    assert len(paged.query_params) == 1
    assert len(paged.responses) == 1
    assert not paged.headers
    assert not paged.uri_params

    q_param = paged.query_params[0]
    assert q_param.name == "numPages"
    desc = "The number of pages to return, not to exceed <<maxPages>>"
    assert q_param.description.raw == desc

    resp = paged.responses[0]
    assert resp.code == 200
    # TODO: FIXME - should be none, but getting copied when assigned to
    #               resources
    # assert not resp.method
    assert resp.description.raw == "No more than <<maxPages>> pages returned"
    assert len(resp.headers) == 1

    assert resp.headers[0].name == "<<anotherHeader>>"
    desc = "some description for <<anotherHeader>>"
    assert resp.headers[0].description.raw == desc


# Test `<< parameter | !function >>` handling
@pytest.fixture(scope="session")
def param_functions():
    raml_file = os.path.join(EXAMPLES, "parameter-tag-functions.raml")
    loaded_raml_file = load_file(raml_file)
    config = setup_config(EXAMPLES + "test-config.ini")
    api = pw.parse_raml(loaded_raml_file, config)
    return api


def test_trait_pluralize(param_functions):
    paged = param_functions.traits[0]
    assert paged.name == 'paged'
    assert len(paged.query_params) == 2

    assert paged.query_params[0].name == "<<item>>"
    desc = ("The number of <<item | !pluralize>> to return, not to "
            "exceed <<maxPages>>")
    assert paged.query_params[0].description.raw == desc

    assert paged.query_params[1].name == "<<spacedItem >>"
    desc = ("The number of << spacedItem | !pluralize >> to return, not "
            "to exceed << maxPages >>")
    assert paged.query_params[1].description.raw == desc

    assert len(param_functions.resources) == 5
    res = param_functions.resources[2]
    assert res.name == "/user"
    assert res.method == "get"
    assert len(res.traits) == 1
    # TODO: FIXME
    # assert len(res.query_params) == 2

    item = res.query_params[0]
    assert item.name == "user"
    desc = ("The number of users to return, not to exceed 10")
    assert item.description.raw == desc

    # TODO: FIXME
    # spaced_item = res.query_params[1]
    assert item.name == "user"
    assert item.description.raw == desc

    foo_trait = param_functions.traits[1]
    assert foo_trait.name == "fooTrait"
    assert len(foo_trait.headers) == 1
    assert len(foo_trait.body) == 1
    assert len(foo_trait.responses) == 1

    foo = param_functions.resources[4]
    assert len(foo.headers) == 1
    header = foo.headers[0]
    assert header.name == "aPluralHeader"
    desc = "This header should be pluralized- cats"
    assert header.description.raw == desc

    assert len(foo.body) == 1
    assert foo.body[0].mime_type == "application/json"
    assert foo.body[0].example == "foos"

    # TODO fixme: returns len 2
    # assert len(foo.responses) == 1
    assert foo.responses[0].code == 200
    desc = "A singular response - bar"
    # TODO: fixme
    # assert foo.responses[0].description.raw == desc


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
    resource = resource_types[-2]
    assert resource.name == "protocolExampleType"
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
    res = resource_types[4]
    assert res.name == "queryParamType"
    query_param = res.query_params[0]
    assert query_param.name == "ids"
    assert query_param.description.raw == "A comma-separated list of IDs"
    assert query_param.display_name == "Some sort of IDs"
    assert query_param.type == "string"
    assert query_param.required


def test_resource_type_form_params(resource_types):
    res = resource_types[5]
    assert res.name == "formParamType"
    form_param = res.form_params[0]
    assert form_param.name == "aFormParam"
    assert form_param.description.raw == "An uncreative form parameter"
    assert form_param.display_name == "Some sort of Form Parameter"
    assert form_param.type == "string"
    assert form_param.required


def test_resource_type_base_uri_params(resource_types):
    res = resource_types[6]
    assert res.name == "baseUriType"
    base_uri_params = res.base_uri_params[0]
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

    assert len(api.resource_types) == 3

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


def test_resource_type_no_method():
    raml_file = os.path.join(EXAMPLES + "resource_type_no_method.raml")
    loaded_raml_file = load_file(raml_file)
    config = setup_config(EXAMPLES + "test-config.ini")
    config['validate'] = False
    api = pw.parse_raml(loaded_raml_file, config)

    res_type = api.resource_types[0]
    assert not res_type.method
    assert res_type.description.raw == "this resource type has no method"


def test_resource_type_protocols_method():
    raml_file = os.path.join(EXAMPLES + "resource-type-method-protocols.raml")
    loaded_raml_file = load_file(raml_file)
    config = setup_config(EXAMPLES + "test-config.ini")
    config['validate'] = False
    api = pw.parse_raml(loaded_raml_file, config)

    res_type = api.resource_types[0]
    assert res_type.protocols == ["HTTP"]
    desc = "this resource type defines a protocol at the method level"
    assert res_type.description.raw == desc


def test_resource_type_protocols_resource():
    _name = "resource-type-resource-protocols.raml"
    raml_file = os.path.join(EXAMPLES + _name)
    loaded_raml_file = load_file(raml_file)
    config = setup_config(EXAMPLES + "test-config.ini")
    config['validate'] = False
    api = pw.parse_raml(loaded_raml_file, config)

    res_type = api.resource_types[0]
    assert res_type.protocols == ["HTTP"]
    desc = "this resource type defines a protocol in the resource level"
    assert res_type.description.raw == desc


@pytest.fixture(scope="session")
def resource_type_parameters():
    raml_file = os.path.join(EXAMPLES + "resource-type-trait-parameters.raml")
    loaded_raml_file = load_file(raml_file)
    config = setup_config(EXAMPLES + "test-config.ini")
    api = pw.parse_raml(loaded_raml_file, config)
    return api


def test_inherit_resource_type_params(resource_type_parameters):
    res = resource_type_parameters.resources[0]

    assert res.name == "/books"
    assert res.method == "get"
    assert len(res.query_params) == 4

    q_param = res.query_params[2]
    assert q_param.name == "title"
    desc = ("Return books that have their title matching "
            "the given value")
    assert q_param.description.raw == desc

    q_param = res.query_params[3]
    assert q_param.name == "digest_all_fields"
    desc = ("If no values match the value given for title, use "
            "digest_all_fields instead")
    assert q_param.description.raw == desc


def test_assigned_resource_type_params(resource_type_parameters):
    res = resource_type_parameters.resources[0]

    assert res.resource_type.name == "searchableCollection"
    assert res.resource_type.method == "get"

    q_params = res.resource_type.query_params
    assert len(q_params) == 2

    assert q_params[0].name == "<<queryParamName>>"
    desc = ("Return <<resourcePathName>> that have their <<queryParamName>> "
            "matching the given value")
    assert q_params[0].description.raw == desc

    assert q_params[1].name == "<<fallbackParamName>>"
    desc = ("If no values match the value given for <<queryParamName>>, "
            "use <<fallbackParamName>> instead")
    assert q_params[1].description.raw == desc


def test_root_resource_type_params(resource_type_parameters):
    res_types = resource_type_parameters.resource_types
    assert len(res_types) == 1
    res = res_types[0]

    assert res.name == "searchableCollection"
    assert res.method == "get"

    q_params = res.query_params
    assert len(q_params) == 2

    assert q_params[0].name == "<<queryParamName>>"
    desc = ("Return <<resourcePathName>> that have their <<queryParamName>> "
            "matching the given value")
    assert q_params[0].description.raw == desc

    assert q_params[1].name == "<<fallbackParamName>>"
    desc = ("If no values match the value given for <<queryParamName>>, use "
            "<<fallbackParamName>> instead")
    assert q_params[1].description.raw == desc


# Test `<< parameter | !function >>` handling
def test_resource_type_pluralize(param_functions):
    assert len(param_functions.resource_types) == 4

    coll = param_functions.resource_types[0]
    assert coll.name == 'collection_single'
    assert coll.method == "get"
    assert coll.description.raw == "Get <<resourcePathName>>"

    res = param_functions.resources[1]
    assert res.name == "/users"
    assert res.method == "post"
    assert res.type == "collection_single"
    assert res.description.raw == "Post user"

    res = param_functions.resources[0]
    assert res.name == "/users"
    assert res.method == "get"
    assert res.type == "collection_single"
    assert res.description.raw == "Get users"

    res = param_functions.resources[3]
    assert res.name == "/user"
    assert res.method == "post"
    assert res.type == "collection_plural"
    assert res.description.raw == "Post user"

    res = param_functions.resources[2]
    assert res.name == "/user"
    assert res.method == "get"
    assert res.type == "collection_plural"
    assert res.description.raw == "Get users"


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

    # abs_uri = "http://{subdomain}.example.com/v1/{communityPath}/widgets/{id}"
    # TODO: FIXME
    # assert resources[1].absolute_uri == abs_uri
    # assert resources[1].media_type == "application/xml"
    # assert resources[1].protocols == ["HTTP"]

    assert resources[2].is_ == ["paged"]
    # assert resources[2].media_type == "application/xml"
    assert resources[12].type == "collection"

    # TODO: FIXME
    # assert resources[3].media_type == "text/xml"


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
    # actual object data will not match, just names
    res_uri = res.base_uri_params[0].name
    restype_uri = res.resource_type.base_uri_params[0].name
    assert res_uri  == restype_uri

    res = resources[-6]
    f1 = res.form_params[0]
    f2 = res.resource_type.form_params[0]
    assert f1.name == f2.name
    assert f1.display_name == f2.display_name
    assert f1.desc == f2.desc
    assert f1.type == f2.type
    assert f1.raw == f2.raw
    # TODO: Add assert_not_set here
    # not_set = [
    #     "example", "default", "min_length", "max_length", "minimum",
    #     "maximum", "eunum", "repeat", "pattern", "required"
    # ]

    res = resources[11]
    assert res.is_ == ["protocolTrait"]
    assert res.traits[0].description.raw == "A trait to assign a protocol"
    assert res.traits[0].protocols == ["HTTP"]


def test_resource_assigned_type(resources):
    res = resources[19]

    assert res.display_name == "thingy"
    assert res.method == "get"
    assert res.type == "item"

    res_type_uri = [r.name for r in res.resource_type.uri_params]
    res_uri = [r.name for r in res.uri_params]

    exp_res_type_uri = ["mediaTypeExtension", "communityPath"]
    exp_res_uri = [
        "mediaTypeExtension", "communityPath", "user_id", "thingy_id"
    ]
    # TODO: uri parameter order isn't preserved...I don't think...
    assert res_type_uri == exp_res_type_uri
    assert sorted(res_uri) == sorted(exp_res_uri)

    # TODO: add more attributes to test with parameter objects
    # e.g. h1.desc
    h1 = res.headers[0]
    h2 = res.resource_type.headers[0]
    assert h1.name == h2.name

    b1 = res.body[0]
    b2 = res.resource_type.body[0]
    assert b1.mime_type == b2.mime_type

    r1 = res.responses[1]
    r2 = res.resource_type.responses[0]
    assert r1.code == r2.code
    assert len(res.headers) == 3
    assert res.headers[0].name == "X-another-header"
    assert res.headers[2].name == "Accept"
    assert res.headers[1].name == "X-example-header"

    res = resources[18]
    assert res.type == "collection"
    assert res.method == "post"
    assert res.form_params[0].name == res.resource_type.form_params[0].name

    res = resources[11]
    assert res.type == "queryParamType"
    assert res.method == "get"
    assert res.resource_type.query_params[0].name == res.query_params[0].name

    res = resources[9]
    assert res.type == "baseUriType"
    assert res.method == "get"
    # actual object data will not match, just name
    res_uri = res.base_uri_params[0].name
    restype_uri = res.resource_type.base_uri_params[0].name
    assert res_uri == restype_uri

    res = resources[1]
    assert res.type == "protocolExampleType"
    assert res.resource_type.name == "protocolExampleType"
    # TODO: FIXME
    # assert res.protocols == res.resource_type.protocols


def test_resource_assigned_trait(resources):
    res = resources[10]

    assert res.name == "/search"
    assert res.is_ == ["paged"]
    assert res.traits[0].description.raw == "A description of the paged trait"
    assert res.traits[0].media_type == "application/xml"

    params = [p.name for p in res.query_params]
    t_params = [p.name for p in res.traits[0].query_params]

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
    assert not schema
    example = res.responses[0].body[1].example
    assert not example

    res = resources[19]
    # TODO: FIXME - inheritance isn't working, probably for optional
    # methods, maybe multiple inherited resource types
    # headers = [h.name for h in res.responses[0].headers]
    # assert "X-waiting-period" in headers
    # body = res.responses[0].body[0].schema
    # TODO: FIXME - assigned JSON schemas are not working
    # assert body == {"name": "string"}
    codes = [r.code for r in res.responses]
    assert [200, 403] == sorted(codes)

    res = resources[-9]

    assert res.path == "/users/{user_id}/thingys/{thingy_id}"
    assert res.type == "item"
    assert res.responses[1].code == res.resource_type.responses[0].code
    assert len(res.responses[1].headers) == 1
    assert res.responses[1].headers[0].name == "X-waiting-period"
    assert res.responses[1].headers[0].type == "integer"
    assert res.responses[1].headers[0].minimum == 1
    assert res.responses[1].headers[0].maximum == 3600
    assert res.responses[1].headers[0].example == 34

    desc = ("The number of seconds to wait before you can attempt to make "
            "a request again.\n")
    assert res.responses[1].headers[0].description.raw == desc

    res_response = res.responses[1].headers[0]
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

    # TODO: figure out what this issue is
    # desc = "subdomain for the baseUriType resource type"
    # assert res.base_uri_params[0].description.raw == desc
    # assert res.base_uri_params[0].default == "fooBar"

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
    assert len(res.uri_params) == 2


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
    config["validate"] = False
    return pw.parse_raml(loaded_raml, config)


def test_resource_inherits_type(inherited_resources):
    # TODO: returns 6 instead of 7
    # assert len(inherited_resources.resources) == 7
    res = inherited_resources.resources[0]
    assert res.type == "inheritgetmethod"
    # TODO: FIXME - something's wrong here...
    # assert res.method == "get"
    # assert len(res.headers) == 1
    # assert len(res.body) == 1
    # assert len(res.responses) == 2
    # assert len(res.query_params) == 1

    # exp_desc = ("This description should be inherited when applied to "
    #             "resources")
    # assert res.description.raw == exp_desc

    # h = res.headers[0]
    # assert h.name == "X-Inherited-Header"
    # assert h.description.raw == "This header should be inherited"

    # b = res.body[0]
    # assert b.mime_type == "application/json"
    # # lazy checking
    # assert b.schema is not None
    # assert b.example is not None

    # q = res.query_params[0]
    # assert q.name == "inherited_param"
    # assert q.display_name == "inherited query parameter for a get method"
    # assert q.type == "string"
    # assert q.description.raw == "description for inherited query param"
    # assert q.example == "fooBar"
    # assert q.min_length == 1
    # assert q.max_length == 50
    # assert q.required is True


def test_res_type_inheritance(inherited_resources):
    res = inherited_resources.resource_types[0]
    assert res.name == "basetype"
    # assert len(res.query_params) == 1
    # assert len(res.form_params) == 1
    # assert len(res.uri_params) == 1
    # assert len(res.base_uri_params) == 1

    res = inherited_resources.resource_types[2]
    assert res.name == "inheritbase"
    assert len(res.query_params) == 2
    assert len(res.form_params) == 2
    assert len(res.uri_params) == 2
    assert len(res.base_uri_params) == 2


def test_resource_inherits_type_optional_post(inherited_resources):
    # TODO: FIXME - reutrns 6 instead of 7
    # assert len(inherited_resources.resources) == 7
    res = inherited_resources.resources[1]
    assert res.type == "inheritgetoptionalmethod"
    assert res.method == "post"
    assert res.headers is None
    assert res.query_params is None
    assert res.description.raw == "post some foobar"


def test_resource_inherits_type_optional_get(inherited_resources):
    # make sure that optional resource type methods are not inherited if not
    # explicitly included in resource (unless no methods defined)
    # FIXME: returns 6 instead of 7
    # assert len(inherited_resources.resources) == 7
    res = inherited_resources.resources[2]
    assert res.type == "inheritgetoptionalmethod"
    assert res.method == "get"
    assert len(res.headers) == 2
    assert len(res.query_params) == 1

    # TODO - this took the resource's description, not resource type's
    # method description; which is preferred?
    # desc = ("This description should be inherited when applied to resources "
    #         "with get methods")
    # assert res.description.raw == desc


def test_resource_inherits_get(inherited_resources):
    # FIXME: returns 6 instead of 7
    # assert len(inherited_resources.resources) == 7
    post_res = inherited_resources.resources[3]
    get_res = inherited_resources.resources[4]

    assert get_res.method == "get"
    assert len(get_res.headers) == 2
    assert len(get_res.body) == 2
    assert len(get_res.responses) == 2
    assert len(get_res.query_params) == 2

    h = get_res.headers[0]
    assert h.name == "X-Overwritten-Header"
    assert h.required
    assert h.description.raw == "This header description should be used"

    h = get_res.headers[1]
    assert h.name == "X-Inherited-Header"
    assert h.description.raw == "this header is inherited"

    b = get_res.body[0]
    assert b.mime_type == "text/xml"
    # lazy
    assert b.schema is not None
    assert b.example is not None

    b = get_res.body[1]
    assert b.mime_type == "application/json"
    # lazy checking
    assert b.schema is not None
    assert b.example is not None

    q = get_res.query_params[0]
    assert q.name == "overwritten"
    assert q.description.raw == "This query param description should be used"
    assert q.example == "This example should be inherited"
    assert q.type == "string"

    q = get_res.query_params[1]
    assert q.name == "inherited"
    assert q.display_name == "inherited"
    assert q.type == "string"
    assert q.description.raw == "An inherited parameter"
    # add assert_not_set

    assert post_res.method == "post"
    assert post_res.description.raw == "post some more foobar"


def test_resource_inherited_no_overwrite(inherited_resources):
    # make sure that if resource inherits a resource type, and explicitly
    # defines properties that are defined in the resource type, the
    # properties in the resource take preference
    # FIXME: returns 6 instead of 7
    # assert len(inherited_resources.resources) == 7
    # res = inherited_resources.resources[5]

    # TODO: FIXME - optional methods are not being assigned to resource methods
    # assert res.method == "get"
    # assert len(res.query_params) == 2

    # desc = "This method-level description should be used"
    # assert res.description.raw == desc

    # test query params
    # first_param = res.query_params[0]
    # second_param = res.query_params[1]

    # assert first_param.name == "inherited"
    # assert first_param.description.raw == "An inherited parameter"

    # assert second_param.name == "overwritten"
    # desc = "This query param description should be used"
    # assert second_param.description.raw == desc

    # # test form params
    # second_param = res.form_params[0]

    # desc = "This description should be inherited"
    # assert second_param.description.raw == desc

    # example = "This example for the overwritten form param should be used"
    # assert second_param.example == example

    # assert second_param.type == "string"
    # assert second_param.min_length == 1
    # assert second_param.max_length == 5

    # test headers
    # first_header = res.headers[0]
    # second_header = res.headers[1]

    # assert first_header.name == "X-Inherited-Header"
    # assert first_header.description.raw == "this header is inherited"

    # assert second_header.name == "X-Overwritten-Header"
    # desc = "This header description should be used"
    # assert second_header.description.raw == desc
    # assert second_header.required

    # # test body
    # first_body = res.body[0]
    # second_body = res.body[1]

    # assert first_body.mime_type == "application/json"

    # schema = {
    #     "$schema": "http://json-schema.org/draft-03/schema",
    #     "type": "object",
    #     "properties": {
    #         "inherited": {
    #             "description": "this schema should be inherited"
    #         }
    #     }
    # }
    # example = {"inherited": "yes please!"}
    # assert first_body.schema == schema
    # assert first_body.example == example

    # assert second_body.mime_type == "text/xml"

    # schema = ("<xs:schema attributeFormDefault='unqualified' "
    #           "elementFormDefault='qualified' "
    #           "xmlns:xs='http://www.w3.org/2001/XMLSchema'>"
    #           "<xs:include schemaLocation='./thingy.xsd'/>"
    #           "<xs:element name='thingies'><xs:complexType>"
    #           "<xs:sequence minOccurs='0' maxOccurs='unbounded'>"
    #           "<xs:element type='thingyType' name='thingy'/>"
    #           "</xs:sequence></xs:complexType></xs:element></xs:schema>")
    # schema = xmltodict.parse(schema)

    # example = ("<thingies><thingy><name>Successfully overwrote body XML "
    #            "example</name></thingy></thingies>")
    # example = xmltodict.parse(example)
    # assert second_body.schema == schema
    # assert second_body.example == example

    # # test responses
    # first_resp = res.responses[0]
    # second_resp = res.responses[1]

    # assert first_resp.code == 200

    # desc = "overwriting the 200 response description"
    # assert first_resp.description.raw == desc
    # assert len(first_resp.headers) == 2

    # first_header = first_resp.headers[0]
    # second_header = first_resp.headers[1]

    # assert first_header.name == "X-Inherited-Success"
    # desc = "inherited success response header"
    # assert first_header.description.raw == desc

    # assert second_header.name == "X-Overwritten-Success"
    # desc = "overwritten success response header"
    # assert second_header.description.raw == desc

    # assert second_resp.code == 201
    # assert second_resp.body[0].mime_type == "application/json"
    # example = {"description": "overwritten description of 201 body example"}
    # assert second_resp.body[0].example == example
    pass


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
    # TODO: FIXME - protocols aren't being inherited, maybe?
    # assert second.protocols == ["HTTP"]


@pytest.fixture(scope="session")
def uri_param_resources():
    raml_file = os.path.join(EXAMPLES, "preserve-uri-order.raml")
    loaded_raml = load_file(raml_file)
    config = setup_config(EXAMPLES + "test-config.ini")
    config['validate'] = False
    return pw.parse_raml(loaded_raml, config)


def test_uri_params_order(uri_param_resources):
    # res = uri_param_resources.resources[1]
    # expected_uri = ["lang", "user_id", "playlist_id"]
    # expected_base = ["subHostName", "bucketName"]

    # uri = [u.name for u in res.uri_params]
    # base = [b.name for b in res.base_uri_params]

    # TODO: implement/fix uri param order
    # assert uri == expected_uri
    # assert base == expected_base
    pass


@pytest.fixture(scope="session")
def undef_uri_params_resources():
    raml_file = os.path.join(EXAMPLES, "undefined-uri-params.raml")
    loaded_raml = load_file(raml_file)
    config = setup_config(EXAMPLES + "test-config.ini")
    config['validate'] = False
    return pw.parse_raml(loaded_raml, config)


def test_undefined_uri_params(undef_uri_params_resources):
    # res = undef_uri_params_resources.resources[1]

    # TODO: Fix undeclared uri params
    # assert len(res.uri_params) == 1
    # assert res.uri_params[0].name == "id"
    pass


@pytest.fixture(scope="session")
def root_secured_by():
    raml_file = os.path.join(EXAMPLES, "root-api-secured-by.raml")
    loaded_raml = load_file(raml_file)
    config = setup_config(EXAMPLES + "test-config.ini")
    config['validate'] = False
    return pw.parse_raml(loaded_raml, config)


def test_root_level_secured_by(root_secured_by):
    assert len(root_secured_by.resources) == 5

    exp = ['oauth_2_0']

    for res in root_secured_by.resources:
        assert res.secured_by == exp


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
