# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB
from __future__ import absolute_import, division, print_function

import os

import pytest

from ramlfications.parser import parse_raml
from ramlfications.config import setup_config
from ramlfications.utils import load_file


from tests.base import V020EXAMPLES, assert_not_set

#####
# TODO: add tests re: assigning resource types to resources
# once that functionality is added to parser.py
#####


@pytest.fixture(scope="session")
def api():
    ramlfile = os.path.join(V020EXAMPLES, "resource_types.raml")
    loaded_raml = load_file(ramlfile)
    conffile = os.path.join(V020EXAMPLES, "test_config.ini")
    config = setup_config(conffile)
    return parse_raml(loaded_raml, config)


def test_create_resource_types(api):
    types = api.resource_types
    assert len(types) == 13

    exp = [
        "base", "base", "inheritBase", "queryParamType", "formParamType",
        "typeWithTrait", "protocolsType", "securedByType", "parameterType",
        "inheritParameterTypeResourceAssigned",
        "inheritParameterTypeMethodAssigned", "typeWithParameterTrait",
        "noMethodType"
    ]
    assert exp == [t.name for t in types]


def test_root_resource_types_base_get(api):
    base_get = api.resource_types[0]
    assert base_get.name == "base"
    assert base_get.method == "get"
    assert base_get.optional
    desc = "This is the base type description"
    assert base_get.description.raw == desc
    assert len(base_get.headers) == 1
    assert len(base_get.body) == 1
    assert len(base_get.responses) == 1
    assert len(base_get.uri_params) == 1
    assert not base_get.query_params
    assert not base_get.form_params

    header = base_get.headers[0]
    assert header.name == "Accept"
    assert header.display_name == "Accept"
    assert header.description.raw == "An Acceptable header"
    assert header.type == "string"
    assert header.method == "get"
    not_set = [
        "default", "enum", "example", "max_length", "maximum",
        "min_length", "minimum", "pattern", "repeat", "required"
    ]
    assert_not_set(header, not_set)

    body = base_get.body[0]
    assert body.mime_type == "application/json"
    assert body.schema == {"name": "string"}
    assert body.example == {"name": "Foo Bar"}
    assert not body.form_params

    resp = base_get.responses[0]
    assert resp.code == 403
    assert resp.description.raw == "API rate limit exceeded.\n"
    assert resp.method == "get"
    assert len(resp.headers) == 1
    assert len(resp.body) == 1

    resp_header = resp.headers[0]
    assert resp_header.name == "X-waiting-period"
    desc = ("The number of seconds to wait before you can attempt to "
            "make a request again.\n")
    assert resp_header.description.raw == desc
    assert resp_header.type == "integer"
    assert resp_header.required
    assert resp_header.minimum == 1
    assert resp_header.maximum == 3600
    assert resp_header.example == 34
    not_set = [
        "default", "enum", "max_length", "min_length", "pattern", "repeat"
    ]
    assert_not_set(resp_header, not_set)

    resp_body = resp.body[0]
    assert resp_body.mime_type == "application/json"
    assert resp_body.schema == {"name": "string"}
    assert resp_body.example == {"name": "Foo Bar"}
    assert not resp_body.form_params


def test_root_resource_types_base_post(api):
    base_post = api.resource_types[1]

    assert base_post.name == "base"
    assert base_post.method == "post"
    assert base_post.optional
    assert len(base_post.headers) == 1
    assert len(base_post.body) == 1
    assert len(base_post.responses) == 1
    assert len(base_post.uri_params) == 1
    assert not base_post.query_params
    assert not base_post.form_params

    header = base_post.headers[0]
    assert header.name == "Accept"
    assert header.display_name == "Accept"
    assert header.description.raw == "An Acceptable header"
    assert header.type == "string"
    assert header.method == "post"
    not_set = [
        "default", "enum", "example", "max_length", "maximum",
        "min_length", "minimum", "pattern", "repeat", "required"
    ]
    assert_not_set(header, not_set)

    body = base_post.body[0]
    assert body.mime_type == "application/json"
    assert body.schema == {"name": "string"}
    assert body.example == {"name": "Foo Bar"}
    assert not body.form_params

    resp = base_post.responses[0]
    assert resp.code == 403
    assert resp.description.raw == "API rate limit exceeded.\n"
    assert resp.method == "post"
    assert len(resp.headers) == 1
    assert len(resp.body) == 1

    resp_header = resp.headers[0]
    assert resp_header.name == "X-waiting-period"
    desc = ("The number of seconds to wait before you can attempt to "
            "make a request again.\n")
    assert resp_header.description.raw == desc
    assert resp_header.type == "integer"
    assert resp_header.required
    assert resp_header.minimum == 1
    assert resp_header.maximum == 3600
    assert resp_header.example == 34
    not_set = [
        "default", "enum", "max_length", "min_length", "pattern", "repeat"
    ]
    assert_not_set(resp_header, not_set)

    resp_body = resp.body[0]
    assert resp_body.mime_type == "application/json"
    assert resp_body.schema == {"name": "string"}
    assert resp_body.example == {"name": "Foo Bar"}
    assert not resp_body.form_params


def test_root_resource_types_inherit_base(api):
    inherit_base = api.resource_types[2]

    assert inherit_base.name == "inheritBase"
    assert inherit_base.method == "get"
    assert inherit_base.optional
    assert inherit_base.display_name == "inherited example"
    desc = "This should overwrite the base type description"
    assert inherit_base.description.raw == desc
    assert len(inherit_base.headers) == 1
    assert len(inherit_base.body) == 2
    assert len(inherit_base.responses) == 3
    assert len(inherit_base.uri_params) == 1
    assert not inherit_base.query_params
    assert not inherit_base.form_params

    header = inherit_base.headers[0]
    assert header.name == "Accept"
    assert header.display_name == "Accept"
    assert header.description.raw == "An Acceptable header"
    assert header.type == "string"
    assert header.method == "get"
    not_set = [
        "default", "enum", "example", "max_length", "maximum",
        "min_length", "minimum", "pattern", "repeat", "required"
    ]
    assert_not_set(header, not_set)

    json_body = inherit_base.body[1]
    assert json_body.mime_type == "application/json"
    assert json_body.schema == {"name": "string"}
    assert json_body.example == {"name": "Foo Bar"}
    assert not json_body.form_params

    form_body = inherit_base.body[0]
    assert form_body.mime_type == "application/x-www-form-urlencoded"
    assert len(form_body.form_params) == 1
    assert not form_body.schema
    assert not form_body.example

    form_param = form_body.form_params[0]
    assert form_param.name == "foo"
    assert form_param.display_name == "Foo"
    assert form_param.description.raw == "some foo bar"
    assert form_param.type == "string"
    not_set = [
        "default", "enum", "example", "max_length", "maximum", "min_length",
        "minimum", "pattern", "repeat", "required"
    ]
    assert_not_set(form_param, not_set)

    resp200 = inherit_base.responses[0]
    assert resp200.code == 200
    assert resp200.description.raw == "A 200 response"
    assert resp200.method == "get"
    assert len(resp200.headers) == 1
    assert len(resp200.body) == 1

    resp200_header = resp200.headers[0]
    assert resp200_header.name == "X-InheritBase-Success-Response-Header"
    assert resp200_header.description.raw == "A 200 header"
    assert resp200_header.type == "string"
    assert resp200_header.required
    assert resp200_header.example == "f00bAr"
    not_set = [
        "default", "enum", "max_length", "maximum", "min_length", "minimum",
        "pattern", "repeat"
    ]
    assert_not_set(resp200_header, not_set)

    resp200_body = resp200.body[0]
    assert resp200_body.mime_type == "application/json"
    assert resp200_body.schema == {"name": "a schema body"}
    assert resp200_body.example == {"name": "an example body"}
    assert not resp200_body.form_params

    resp403 = inherit_base.responses[1]
    assert resp403.code == 403
    assert resp403.description.raw == "API rate limit exceeded.\n"
    assert resp403.method == "get"
    assert len(resp403.headers) == 1
    assert len(resp403.body) == 1

    resp403_header = resp403.headers[0]
    assert resp403_header.name == "X-waiting-period"
    desc = ("The number of seconds to wait before you can attempt to "
            "make a request again.\n")
    assert resp403_header.description.raw == desc
    assert resp403_header.type == "integer"
    assert resp403_header.required
    assert resp403_header.minimum == 1
    assert resp403_header.maximum == 3600
    assert resp403_header.example == 34
    not_set = [
        "default", "enum", "max_length", "min_length", "pattern", "repeat"
    ]
    assert_not_set(resp403_header, not_set)

    resp403_body = resp403.body[0]
    assert resp403_body.mime_type == "application/json"
    assert resp403_body.schema == {"name": "string"}
    assert resp403_body.example == {"name": "Foo Bar"}
    assert not resp403_body.form_params

    resp500 = inherit_base.responses[2]
    assert resp500.code == 500
    assert resp500.description.raw == "A 500 response"
    assert resp500.method == "get"
    assert len(resp500.headers) == 1
    assert not resp500.body

    resp500_header = resp500.headers[0]
    assert resp500_header.name == "X-InheritBase-ServerError-Response-Header"
    assert resp500_header.description.raw == "A 500 error"
    assert resp500_header.method == "get"
    assert resp500_header.type == "string"
    assert resp500_header.required
    assert resp500_header.example == "fuuuuuu"
    not_set = [
        "default", "enum", "maximum", "max_length", "minimum", "min_length",
        "pattern", "repeat"
    ]
    assert_not_set(resp500_header, not_set)


def test_root_resource_types_query_param(api):
    query_param = api.resource_types[3]

    assert query_param.name == "queryParamType"
    assert query_param.method == "get"
    assert query_param.optional
    assert query_param.display_name == "query param type"
    desc = ("A resource type with query parameters")
    assert query_param.description.raw == desc
    not_set = ["headers", "body", "responses", "form_params", "uri_params"]
    assert_not_set(query_param, not_set)

    assert len(query_param.query_params) == 6

    string = query_param.query_params[0]
    assert string.name == "stringParam"
    assert string.display_name == "String Parameter"
    desc = "A description of the string query parameter"
    assert string.description.raw == desc
    assert string.type == "string"
    assert string.required
    assert string.max_length == 255
    assert string.min_length == 1
    assert string.default == "foobar"
    assert string.pattern == "^[a-zA-Z0-9][-a-zA-Z0-9]*$"
    assert string.repeat
    not_set = ["enum", "example"]
    assert_not_set(string, not_set)

    integer = query_param.query_params[1]
    assert integer.name == "intParam"
    assert integer.display_name == "Integer Parameter"
    desc = "A description of the integer query parameter"
    assert integer.description.raw == desc
    assert integer.type == "integer"
    assert integer.required is False
    assert integer.maximum == 1000
    assert integer.minimum == 0
    assert integer.example == 5
    assert integer.default == 10
    not_set = ["enum", "pattern", "repeat", "max_length", "min_length"]
    assert_not_set(integer, not_set)

    enum = query_param.query_params[2]
    assert enum.name == "enumParam"
    assert enum.display_name == "Enum Parameter"
    desc = "A description of the enum query parameter"
    assert enum.description.raw == desc
    assert enum.type == "string"
    assert enum.required
    assert enum.enum == ["foo", "bar", "baz"]
    assert enum.default == "foo"
    not_set = [
        "example", "pattern", "repeat", "max_length", "min_length",
        "minimum", "maximum"
    ]
    assert_not_set(enum, not_set)

    date = query_param.query_params[3]
    assert date.name == "dateParam"
    assert date.display_name == "Date Parameter"
    desc = "A description of the date query parameter"
    assert date.description.raw == desc
    assert date.type == "date"
    assert date.required is False
    assert date.repeat is False
    not_set = [
        "example", "pattern", "max_length", "maximum", "min_length",
        "minimum", "enum", "default"
    ]
    assert_not_set(date, not_set)

    boolean = query_param.query_params[4]
    assert boolean.name == "boolParam"
    assert boolean.display_name == "Boolean Parameter"
    desc = "A description of the bool query parameter"
    assert boolean.description.raw == desc
    assert boolean.type == "boolean"
    assert boolean.required
    assert boolean.repeat is False
    not_set = [
        "example", "pattern", "max_length", "maximum", "min_length",
        "minimum", "enum", "default"
    ]
    assert_not_set(boolean, not_set)

    filep = query_param.query_params[5]
    assert filep.name == "fileParam"
    assert filep.display_name == "File Parameter"
    desc = "A description of the file query parameter"
    assert filep.description.raw == desc
    assert filep.type == "file"
    assert filep.required is False
    assert filep.repeat
    not_set = [
        "example", "pattern", "max_length", "maximum", "min_length",
        "minimum", "enum", "default"
    ]
    assert_not_set(boolean, not_set)


def test_root_resource_types_form_param(api):
    form_param = api.resource_types[4]

    assert form_param.name == "formParamType"
    assert form_param.method == "post"
    assert form_param.optional
    assert form_param.display_name == "form param type"
    desc = ("A resource type with form parameters")
    assert form_param.description.raw == desc
    not_set = ["headers", "body", "responses", "query_params", "uri_params"]
    assert_not_set(form_param, not_set)

    assert len(form_param.form_params) == 6

    string = form_param.form_params[0]
    assert string.name == "stringParam"
    assert string.display_name == "String Parameter"
    desc = "A description of the string form parameter"
    assert string.description.raw == desc
    assert string.type == "string"
    assert string.required
    assert string.max_length == 255
    assert string.min_length == 1
    assert string.default == "foobar"
    assert string.pattern == "^[a-zA-Z0-9][-a-zA-Z0-9]*$"
    assert string.repeat
    not_set = ["enum", "example"]
    assert_not_set(string, not_set)

    integer = form_param.form_params[1]
    assert integer.name == "intParam"
    assert integer.display_name == "Integer Parameter"
    desc = "A description of the integer form parameter"
    assert integer.description.raw == desc
    assert integer.type == "integer"
    assert integer.required is False
    assert integer.maximum == 1000
    assert integer.minimum == 0
    assert integer.example == 5
    assert integer.default == 10
    not_set = ["enum", "pattern", "repeat", "max_length", "min_length"]
    assert_not_set(integer, not_set)

    enum = form_param.form_params[2]
    assert enum.name == "enumParam"
    assert enum.display_name == "Enum Parameter"
    desc = "A description of the enum form parameter"
    assert enum.description.raw == desc
    assert enum.type == "string"
    assert enum.required
    assert enum.enum == ["foo", "bar", "baz"]
    assert enum.default == "foo"
    not_set = [
        "example", "pattern", "repeat", "max_length", "min_length",
        "minimum", "maximum"
    ]
    assert_not_set(enum, not_set)

    date = form_param.form_params[3]
    assert date.name == "dateParam"
    assert date.display_name == "Date Parameter"
    desc = "A description of the date form parameter"
    assert date.description.raw == desc
    assert date.type == "date"
    assert date.required is False
    assert date.repeat is False
    not_set = [
        "example", "pattern", "max_length", "maximum", "min_length",
        "minimum", "enum", "default"
    ]
    assert_not_set(date, not_set)

    boolean = form_param.form_params[4]
    assert boolean.name == "boolParam"
    assert boolean.display_name == "Boolean Parameter"
    desc = "A description of the bool form parameter"
    assert boolean.description.raw == desc
    assert boolean.type == "boolean"
    assert boolean.required
    assert boolean.repeat is False
    not_set = [
        "example", "pattern", "max_length", "maximum", "min_length",
        "minimum", "enum", "default"
    ]
    assert_not_set(boolean, not_set)

    filep = form_param.form_params[5]
    assert filep.name == "fileParam"
    assert filep.display_name == "File Parameter"
    desc = "A description of the file form parameter"
    assert filep.description.raw == desc
    assert filep.type == "file"
    assert filep.required is False
    assert filep.repeat
    not_set = [
        "example", "pattern", "max_length", "maximum", "min_length",
        "minimum", "enum", "default"
    ]
    assert_not_set(boolean, not_set)


def test_root_resource_types_assigned_trait(api):
    trait_type = api.resource_types[5]

    assert trait_type.name == "typeWithTrait"
    assert trait_type.method == "get"
    assert not trait_type.optional
    assert trait_type.display_name == "Resource Type with Trait"
    assert trait_type.is_ == ["aResourceTypeTrait"]
    assert len(trait_type.traits) == 1

    trait = trait_type.traits[0]
    assert trait.name == "aResourceTypeTrait"
    desc = "A trait to be assigned to a Resource Type"
    assert trait.description.raw == desc
    assert len(trait.query_params) == 1
    assert not trait.form_params
    assert not trait.uri_params
    assert not trait.headers
    assert not trait.body
    assert not trait.responses

    q_param = trait_type.query_params[0]
    assert q_param.name == "stringParam"
    assert q_param.display_name == "String Parameter"
    desc = "A description of the string query parameter"
    assert q_param.description.raw == desc
    assert q_param.type == "string"
    assert q_param.required
    assert q_param.max_length == 255
    assert q_param.min_length == 1
    assert q_param.default == "foobar"
    assert q_param.pattern == "^[a-zA-Z0-9][-a-zA-Z0-9]*$"
    assert q_param.repeat


def test_root_resource_types_protocols(api):
    protos = api.resource_types[6]

    assert protos.name == "protocolsType"
    assert protos.method == "put"
    assert not protos.optional
    assert protos.display_name == "Protocols Type"
    desc = "Resource Type with different protocols than root"
    assert protos.description.raw == desc
    assert protos.protocols == ["HTTP"]


def test_root_resource_types_secured_by(api):
    secured = api.resource_types[7]

    assert secured.name == "securedByType"
    assert secured.display_name == "Secured Type"
    assert secured.method == "post"
    assert not secured.optional
    assert secured.description.raw == "Resource Type is secured"
    assert secured.secured_by == ["oauth_2_0"]


def test_root_resource_types_parameter(api):
    res = api.resource_types[8]

    assert res.name == "parameterType"
    assert res.display_name == "parameterType"
    assert res.method == "get"
    assert not res.optional
    assert res.protocols == ["HTTPS"]
    desc = "A resource type with substitutable parameters"
    assert res.description.raw == desc
    assert len(res.query_params) == 2

    not_set = [
        "form_params", "headers", "is_", "media_type", "responses",
        "secured_by", "security_schemes", "traits", "type", "uri_params",
        "usage"
    ]
    assert_not_set(res, not_set)

    q_param = res.query_params[0]
    assert q_param.name == "<<queryParamName>>"
    desc = ("Return <<resourcePathName>> that have their <<queryParamName>> "
            "matching the given value")
    assert q_param.description.raw == desc

    fallback = res.query_params[1]
    assert fallback.name == "<<fallbackParamName>>"
    desc = ("If no values match the value given for <<queryParamName>>, use "
            "<<fallbackParamName>> instead")
    assert fallback.description.raw == desc

    not_set = [
        "default", "enum", "example", "max_length", "maximum",
        "min_length", "minimum", "pattern", "repeat", "required"
    ]
    assert_not_set(q_param, not_set)
    assert_not_set(fallback, not_set)


def test_root_resource_types_inherit_parameter_resource(api):
    res = api.resource_types[9]

    assert res.name == "inheritParameterTypeResourceAssigned"
    assert res.display_name == "inheritParameterTypeResourceAssigned"
    assert res.method == "get"
    assert not res.optional
    desc = "Inherits parameterType resource type"
    assert res.description.raw == desc
    assert len(res.query_params) == 2

    not_set = [
        "form_params", "headers", "is_", "media_type", "responses",
        "secured_by", "security_schemes", "traits", "uri_params", "usage"
    ]
    assert_not_set(res, not_set)

    q_param = res.query_params[0]
    assert q_param.name == "foo"
    desc = ("Return <<resourcePathName>> that have their foo "
            "matching the given value")
    assert q_param.description.raw == desc

    fallback = res.query_params[1]
    assert fallback.name == "bar"
    desc = ("If no values match the value given for foo, use "
            "bar instead")
    assert fallback.description.raw == desc

    not_set = [
        "default", "enum", "example", "max_length", "maximum",
        "min_length", "minimum", "pattern", "repeat", "required"
    ]
    assert_not_set(q_param, not_set)
    assert_not_set(fallback, not_set)


def test_root_resource_types_inherit_parameter_method(api):
    res = api.resource_types[10]

    assert res.name == "inheritParameterTypeMethodAssigned"
    assert res.display_name == "inheritParameterTypeMethodAssigned"
    assert res.method == "get"
    assert not res.optional
    desc = "Inherits parameterType resource type"
    assert res.description.raw == desc
    assert len(res.query_params) == 2

    not_set = [
        "form_params", "headers", "is_", "media_type", "responses",
        "secured_by", "security_schemes", "traits", "uri_params", "usage"
    ]
    assert_not_set(res, not_set)

    q_param = res.query_params[0]
    assert q_param.name == "foo"
    desc = ("Return <<resourcePathName>> that have their foo "
            "matching the given value")
    assert q_param.description.raw == desc

    fallback = res.query_params[1]
    assert fallback.name == "bar"
    desc = ("If no values match the value given for foo, use "
            "bar instead")
    assert fallback.description.raw == desc

    not_set = [
        "default", "enum", "example", "max_length", "maximum",
        "min_length", "minimum", "pattern", "repeat", "required"
    ]
    assert_not_set(q_param, not_set)
    assert_not_set(fallback, not_set)


def test_root_resource_types_inherit_parameter_trait(api):
    res = api.resource_types[11]

    assert res.name == "typeWithParameterTrait"
    assert res.display_name == "Resource Type with Parameter Trait"
    assert res.method == "get"
    assert res.protocols == ["HTTPS"]
    assert len(res.is_) == 1
    assert len(res.traits) == 1
    assert len(res.query_params) == 1
    assert len(res.responses) == 1
    assert len(res.responses[0].headers) == 1

    not_set = [
        "form_params", "headers", "type", "media_type", "secured_by",
        "security_schemes", "uri_params", "usage", "body"
    ]
    assert_not_set(res, not_set)

    q_param = res.query_params[0]
    assert q_param.name == "numPages"
    desc = ("The number of pages to return, not to exceed 10")
    assert q_param.description.raw == desc

    not_set = [
        "default", "enum", "example", "max_length", "maximum",
        "min_length", "minimum", "pattern", "repeat", "required"
    ]
    assert_not_set(q_param, not_set)

    resp = res.responses[0]
    assert resp.code == 200
    assert resp.method == "get"
    desc = ("No more than 10 pages returned")
    assert resp.description.raw == desc

    resp_header = resp.headers[0]
    assert resp_header.name == "X-foo-header"
    assert resp_header.method == "get"
    assert resp_header.description.raw == "some description for X-foo-header"
    assert not res.responses[0].body


def test_resource_type_no_method(api):
    res = api.resource_types[12]

    assert res.name == "noMethodType"
    assert res.display_name == "noMethodType"
    assert res.protocols == ["HTTPS"]
    assert res.description.raw == "This type has no methods defined"
    assert len(res.uri_params) == 1

    not_set = [
        "form_params", "headers", "type", "media_type", "secured_by",
        "security_schemes", "usage", "body", "method", "is_", "type"
    ]
    assert_not_set(res, not_set)

    uri = res.uri_params[0]
    assert uri.name == "id"
    assert uri.display_name == "id"
    assert uri.description.raw == "some random ID"
    assert uri.type == "string"
    assert uri.required

    not_set = [
        "default", "enum", "example", "max_length", "maximum",
        "min_length", "minimum", "pattern", "repeat"
    ]
    assert_not_set(uri, not_set)
