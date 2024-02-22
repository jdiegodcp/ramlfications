# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB
from __future__ import absolute_import, division, print_function

import os

import pytest

from ramlfications.config import setup_config
from ramlfications.models import data_types
from ramlfications.parser import parse_raml
from ramlfications.utils import load_file

from tests.base import RAML_ORG_EXAMPLES, RAML_10, assert_not_set

DATA_TYPES = os.path.join(RAML_10, "data_types")


@pytest.fixture(scope="session")
def api():
    ramlfile = os.path.join(DATA_TYPES, "data_type_resource_types.raml")
    loaded_raml = load_file(ramlfile)
    configfile = os.path.join(RAML_ORG_EXAMPLES, "simple_config.ini")
    config = setup_config(configfile)
    return parse_raml(loaded_raml, config)


def test_api(api):
    assert len(api.types) == 1
    assert len(api.resource_types) == 2
    assert len(api.resources) == 2


def test_resource_type(api):
    res_type = api.resource_types[0]
    assert res_type.name == "qParamCollection"
    assert res_type.method == "get"
    assert len(res_type.query_params) == 1

    q_param = res_type.query_params[0]
    assert q_param.name == 'id'
    assert q_param.type == 'EmployeeId'
    assert q_param.data_type.name == 'EmployeeId'
    assert q_param.data_type.type == 'string'
    assert isinstance(q_param.data_type, data_types.StringDataType)

    res_type = api.resource_types[1]
    assert res_type.name == "uParamCollection"
    assert res_type.method == "get"
    assert len(res_type.uri_params) == 1

    uri_param = res_type.uri_params[0]
    assert uri_param.name == 'id'
    assert uri_param.type == 'EmployeeId'
    assert uri_param.data_type.name == 'EmployeeId'
    assert uri_param.data_type.type == 'string'
    assert isinstance(uri_param.data_type, data_types.StringDataType)


def test_resource_query_params(api):
    res = api.resources[0]
    assert res.name == "/employees"
    assert res.display_name == "/employees"
    assert res.type == "qParamCollection"
    assert res.method == "get"
    assert len(res.query_params) == 1

    q_param = res.query_params[0]
    assert q_param.name == "id"
    assert q_param.type == "EmployeeId"
    assert q_param.data_type.name == "EmployeeId"
    assert isinstance(q_param.data_type, data_types.StringDataType)

    not_set = [
        'default', 'desc', 'description', 'enum', 'errors', 'example',
        'max_length', 'maximum', 'min_length', 'minimum', 'pattern',
        'required'
    ]
    if api.raml_version == "0.8":
        not_set.append("repeat")
    assert_not_set(q_param, not_set)

    not_set = [
        'annotation', 'default', 'enum', 'errors', 'example',
        'examples', 'facets', 'min_length', 'pattern', 'schema',
        'usage', 'xml'
    ]
    assert_not_set(q_param.data_type, not_set)


def test_resource_uri_params(api):
    res = api.resources[1]
    assert res.name == "/{id}"
    assert res.display_name == "/{id}"
    assert res.type == "uParamCollection"
    assert res.method == "get"
    assert len(res.uri_params) == 1

    uri_param = res.uri_params[0]
    assert uri_param.name == "id"
    assert uri_param.type == "EmployeeId"
    assert uri_param.data_type.name == "EmployeeId"
    assert isinstance(uri_param.data_type, data_types.StringDataType)

    not_set = [
        'default', 'desc', 'description', 'enum', 'errors', 'example',
        'max_length', 'maximum', 'min_length', 'minimum', 'pattern',
    ]
    if api.raml_version == "0.8":
        not_set.append("repeat")
    assert_not_set(uri_param, not_set)

    not_set = [
        'annotation', 'default', 'enum', 'errors', 'example',
        'examples', 'facets', 'min_length', 'pattern', 'schema',
        'usage', 'xml'
    ]
    assert_not_set(uri_param.data_type, not_set)
