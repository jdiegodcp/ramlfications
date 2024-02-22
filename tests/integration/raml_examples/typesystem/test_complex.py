# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB
from __future__ import absolute_import, division, print_function

import os

import pytest

from ramlfications.config import setup_config
from ramlfications.models import data_types
from ramlfications.parser import parse_raml
from ramlfications.utils import load_file

from tests.base import (
    DATA_TYPE_OBJECT_ATTRS, RAML_ORG_EXAMPLES, assert_not_set
)


def _test_attrs_set(item, attrs_to_exp):
    for attrib, exp in attrs_to_exp:
        assert getattr(item, attrib) == exp


@pytest.fixture(scope="session")
def api():
    typesystem = os.path.join(RAML_ORG_EXAMPLES, "typesystem")
    ramlfile = os.path.join(typesystem, "complex.raml")
    loaded_raml = load_file(ramlfile)
    configfile = os.path.join(RAML_ORG_EXAMPLES, "simple_config.ini")
    config = setup_config(configfile)
    return parse_raml(loaded_raml, config)


def test_root(api):
    assert api.title == "My API with Types"
    assert api.media_type == "application/json"
    assert len(api.types) == 7
    assert len(api.resources) == 1
    assert not api.resource_types
    assert not api.traits
    assert not api.security_schemes


def test_org_type(api):
    org = api.types[0]
    attrs_to_exp = [
        ("name", "Org"),
        ("type", "object"),
        ("display_name", "Org"),
        ("raml_version", "1.0")
    ]
    _test_attrs_set(org, attrs_to_exp)
    assert len(org.properties) == 2
    assert sorted(org.properties.keys()) == sorted(["onCall", "Head"])
    assert isinstance(org, data_types.ObjectDataType)

    on_call = org.properties.get("onCall")
    assert on_call.type == "Alertable"
    assert not on_call.required
    assert not on_call.default
    # TODO: add support
    # assert on_call.data_type.name == "Alertable"

    not_set = [
        'additional_properties', 'annotation', 'default', 'discriminator',
        'discriminator_value', 'errors', 'example', 'examples', 'facets',
        'max_properties', 'min_properties', 'schema', 'usage', 'xml'
    ]
    assert_not_set(org, not_set)
    assert not org.description.html
    assert not org.description.raw


def test_person_type(api):
    person = api.types[1]

    attrs_to_exp = [
        ("name", "Person"),
        ("display_name", "Person"),
        ("type", "object"),
        ("discriminator", "kind"),
        ("raml_version", "1.0")
    ]
    _test_attrs_set(person, attrs_to_exp)
    assert isinstance(person, data_types.ObjectDataType)

    not_set = [
        'additional_properties', 'annotation', 'default',
        'discriminator_value', 'errors', 'example', 'examples', 'facets',
        'max_properties', 'min_properties', 'schema', 'usage', 'xml'
    ]
    assert_not_set(person, not_set)

    assert len(person.properties) == 4
    not_set = ["default", "required"]
    for v in person.properties.values():
        assert_not_set(v, not_set)
        _test_attrs_set(v, [("type", "string")])


def test_phone_type(api):
    phone = api.types[2]
    attrs_to_exp = [
        ("name", "Phone"),
        ("display_name", "Phone"),
        ("type", "string"),
        ("max_length", 2147483647),
        ("raml_version", "1.0")
    ]
    _test_attrs_set(phone, attrs_to_exp)
    assert not phone.description.raw
    assert not phone.description.html
    assert phone.pattern.pattern == "^[0-9|-]+$"
    assert isinstance(phone, data_types.StringDataType)

    not_set = [
        'annotation', 'default', 'enum', 'errors', 'example',
        'examples', 'facets', 'min_length', 'schema', 'usage', 'xml'
    ]
    assert_not_set(phone, not_set)


def test_manager_type(api):
    manager = api.types[3]
    attrs_to_exp = [
        ("name", "Manager"),
        ("display_name", "Manager"),
        ("type", "Person"),
        ("raml_version", "1.0"),
        ("discriminator", "kind")
    ]
    _test_attrs_set(manager, attrs_to_exp)
    assert isinstance(manager, data_types.ObjectDataType)

    not_set = [
        'additional_properties', 'annotation', 'default',
        'discriminator_value', 'errors', 'example', 'examples', 'facets',
        'max_properties', 'min_properties', 'schema', 'usage', 'xml'
    ]
    assert_not_set(manager, not_set)
    _set = ["config", "raw", "root"]
    for s in _set:
        assert getattr(manager, s)

    props = manager.properties
    assert len(props) == 6
    first = props.get("firstname")
    last = props.get("lastname")
    title = props.get("title?")
    kind = props.get("kind")
    reports = props.get("reports")
    phone = props.get("phone")

    not_set = ["required", "default"]
    for v in props.values():
        assert_not_set(v, not_set)

    assert first.type == "string"
    assert last.type == "string"
    assert title.type == "string"
    assert kind.type == "string"
    assert reports.type == "Person[]"
    assert phone.type == "Phone"


def test_admin_type(api):
    admin = api.types[4]
    attrs_to_exp = [
        ("name", "Admin"),
        ("display_name", "Admin"),
        ("type", "Person"),
        ("discriminator", "kind"),
        ("raml_version", "1.0")
    ]
    _test_attrs_set(admin, attrs_to_exp)

    assert isinstance(admin, data_types.ObjectDataType)

    not_set = [
        'additional_properties', 'annotation', 'default',
        'discriminator_value', 'errors', 'example', 'examples', 'facets',
        'max_properties', 'min_properties', 'schema', 'usage', 'xml'
    ]
    assert_not_set(admin, not_set)
    _set = ["config", "raw", "root"]
    for s in _set:
        assert getattr(admin, s)

    assert len(admin.properties) == 5
    not_set = ["required", "default"]
    for v in admin.properties.values():
        assert_not_set(v, not_set)

    first = admin.properties.get("firstname")
    last = admin.properties.get("lastname")
    title = admin.properties.get("title?")
    kind = admin.properties.get("kind")
    clearance = admin.properties.get("clearanceLevel")
    assert first.type == "string"
    assert last.type == "string"
    assert title.type == "string"
    assert kind.type == "string"
    # TODO: fixme - this should be an enum type
    assert clearance.type == "string"


def test_alertable_admin_type(api):
    alert_admin = api.types[5]
    attrs_to_exp = [
        ("name", "AlertableAdmin"),
        ("display_name", "AlertableAdmin"),
        ("type", "Admin"),
        ("discriminator", "kind"),
        ("raml_version", "1.0")
    ]
    _test_attrs_set(alert_admin, attrs_to_exp)

    assert isinstance(alert_admin, data_types.ObjectDataType)

    not_set = [
        'additional_properties', 'annotation', 'default',
        'discriminator_value', 'errors', 'example', 'examples', 'facets',
        'max_properties', 'min_properties', 'schema', 'usage', 'xml'
    ]
    assert_not_set(alert_admin, not_set)
    _set = ["config", "raw", "root"]
    for s in _set:
        assert getattr(alert_admin, s)

    assert len(alert_admin.properties) == 6
    not_set = ["required", "default"]
    for v in alert_admin.properties.values():
        assert_not_set(v, not_set)

    first = alert_admin.properties.get("firstname")
    last = alert_admin.properties.get("lastname")
    title = alert_admin.properties.get("title?")
    kind = alert_admin.properties.get("kind")
    clearance = alert_admin.properties.get("clearanceLevel")
    phone = alert_admin.properties.get("phone")

    assert first.type == "string"
    assert last.type == "string"
    assert title.type == "string"
    assert kind.type == "string"
    # TODO: fixme - this should be an enum type
    assert clearance.type == "string"
    assert phone.type == "Phone"


# TODO: fixme when support for union types is added
def test_alertable_type(api):
    alertable = api.types[6]
    attrs_to_exp = [
        ("name", "Alertable"),
        ("display_name", "Alertable"),
        ("type", "Manager"),
        ("discriminator", "kind"),
        ("raml_version", "1.0")
    ]
    _test_attrs_set(alertable, attrs_to_exp)

    assert isinstance(alertable, data_types.ObjectDataType)

    not_set = [
        'additional_properties', 'annotation', 'default',
        'discriminator_value', 'errors', 'example', 'examples', 'facets',
        'max_properties', 'min_properties', 'schema', 'usage', 'xml'
    ]
    assert_not_set(alertable, not_set)
    _set = ["config", "raw", "root"]
    for s in _set:
        assert getattr(alertable, s)

    assert len(alertable.properties) == 6
    not_set = ["required", "default"]
    for v in alertable.properties.values():
        assert_not_set(v, not_set)

    first = alertable.properties.get("firstname")
    last = alertable.properties.get("lastname")
    title = alertable.properties.get("title?")
    kind = alertable.properties.get("kind")
    reports = alertable.properties.get("reports")
    phone = alertable.properties.get("phone")
    assert first.type == "string"
    assert last.type == "string"
    assert title.type == "string"
    assert kind.type == "string"
    # TODO: fixme - this should be an enum type
    assert reports.type == "Person[]"
    assert phone.type == "Phone"


def test_resource(api):
    res = api.resources[0]
    attrs_to_exp = [
        ("name", "/orgs/{orgId}"),
        ("display_name", "/orgs/{orgId}"),
        ("method", "get"),
        # why is this a list?!
        ("absolute_uri", ["/orgs/{orgId}"]),
        ("media_type", "application/json"),
        ("path", "/orgs/{orgId}"),
        # TODO: fixme - this should just be none or something
        ("protocols", [""])
    ]
    _test_attrs_set(res, attrs_to_exp)

    not_set = [
        'base_uri_params', 'body', 'desc', 'errors', 'form_params',
        'headers', 'is_', 'parent', 'query_params', 'resource_type',
        'secured_by', 'security_schemes', 'traits', 'type'
    ]
    assert_not_set(res, not_set)

    _set = ["raw", "root", "description"]
    for s in _set:
        assert getattr(res, s)

    assert len(res.uri_params) == 1
    u_param = res.uri_params[0]

    attrs_to_exp = [
        ("name", "orgId"),
        ("display_name", "orgId"),
        ("type", "string"),
        ("required", True)
    ]
    _test_attrs_set(u_param, attrs_to_exp)

    not_set = [
        'data_type', 'default', 'desc', 'description',
        'enum', 'errors', 'example', 'max_length',
        'maximum', 'min_length', 'minimum', 'pattern',
    ]
    if api.raml_version == "0.8":
        not_set.append("repeat")
    assert_not_set(u_param, not_set)
    _set = ["config", "raw"]
    for s in _set:
        assert getattr(u_param, s)

    assert len(res.responses) == 1
    resp = res.responses[0]

    attrs_to_exp = [
        ("code", 200),
        ("method", "get")
    ]
    _test_attrs_set(resp, attrs_to_exp)

    not_set = [
        'errors', 'headers'
    ]
    assert_not_set(resp, not_set)
    _set = ["config", "raw"]
    for s in _set:
        assert getattr(resp, s)

    assert len(resp.body) == 1
    body = resp.body[0]

    attrs_to_exp = [
        ("mime_type", "application/json"),
        ("type", "Org"),
    ]
    _test_attrs_set(body, attrs_to_exp)

    not_set = [
        'errors', 'form_params', 'schema'
    ]
    assert_not_set(body, not_set)
    _set = ["config", "raw"]
    for s in _set:
        assert getattr(body, s)

    _set = [
        "config", "raw", "description", "root", "properties",
        "name", "display_name", "type", "raml_version"
    ]
    for s in _set:
        assert getattr(body.data_type, s)

    attrs_to_exp = [
        ("name", "Org"),
        ("display_name", "Org"),
        ("type", "object"),
        ("raml_version", "1.0")
    ]
    _test_attrs_set(body.data_type, attrs_to_exp)
    not_set = set(DATA_TYPE_OBJECT_ATTRS) - set(_set)
    assert_not_set(body.data_type, not_set)

    # TODO: once example object implementation is done, update this test
    expected_example = {
        'onCall': {
            'firstname': 'nico',
            'lastname': 'ark',
            'kind': 'admin',
            'clearanceLevel': 'low',
            'phone': '12321'
        },
        'Head': {
            'firstname': 'nico',
            'lastname': 'ark',
            'kind': 'manager',
            'reports': [{
                'firstname': 'nico',
                'lastname': 'ark',
                'kind': 'admin'}],
            'phone': '123-23'
        }
    }
    assert body.example == expected_example
