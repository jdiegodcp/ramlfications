# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB
from __future__ import absolute_import, division, print_function

import os

import pytest

from ramlfications.config import setup_config
from ramlfications.models import data_types
from ramlfications.parser import parse_raml
from ramlfications.utils import load_file

from tests.base import RAMLEXAMPLES, V020EXAMPLES, assert_not_set

DATA_TYPES = os.path.join(V020EXAMPLES, "data_types")


@pytest.fixture(scope="session")
def api():
    ramlfile = os.path.join(DATA_TYPES, "data_type_parameters.raml")
    loaded_raml = load_file(ramlfile)
    configfile = os.path.join(RAMLEXAMPLES, "simple_config.ini")
    config = setup_config(configfile)
    return parse_raml(loaded_raml, config)


def test_api_query_params(api):
    res = api.resources[0]
    assert len(res.query_params) == 1

    id_ = res.query_params[0]
    assert id_.type == 'EmployeeId'
    assert id_.required
    assert id_.name == 'id'

    not_set = [
        'default', 'desc', 'description', 'enum', 'errors', 'example',
        'max_length', 'maximum', 'min_length', 'minimum', 'pattern',
        'repeat'
    ]
    assert_not_set(id_, not_set)
    assert id_.data_type.name == 'EmployeeId'
    assert id_.data_type.type == 'string'
    assert isinstance(id_.data_type, data_types.StringDataType)


def test_api_uri_params(api):
    res = api.resources[1]
    assert len(res.uri_params) == 1

    id_ = res.uri_params[0]
    assert id_.type == 'EmployeeId'
    assert id_.required
    assert id_.name == 'id'

    not_set = [
        'default', 'desc', 'description', 'enum', 'errors', 'example',
        'max_length', 'maximum', 'min_length', 'minimum', 'pattern',
        'repeat'
    ]
    assert_not_set(id_, not_set)
    assert id_.data_type.name == 'EmployeeId'
    assert id_.data_type.type == 'string'
    assert isinstance(id_.data_type, data_types.StringDataType)


def test_api_response_headers(api):
    res = api.resources[2]

    assert len(res.headers) == 1

    id_ = res.headers[0]
    assert id_.type == 'EmployeeId'
    assert id_.required
    assert id_.name == 'X-Employee'

    not_set = [
        'default', 'desc', 'description', 'enum', 'errors', 'example',
        'max_length', 'maximum', 'min_length', 'minimum', 'pattern',
        'repeat'
    ]
    assert_not_set(id_, not_set)
    assert id_.data_type.name == 'EmployeeId'
    assert id_.data_type.type == 'string'
    assert isinstance(id_.data_type, data_types.StringDataType)


def test_api_response_body(api):
    res = api.resources[2]
    assert len(res.responses) == 1

    resp = res.responses[0]
    assert len(resp.body) == 1
    body = resp.body[0]
    assert body.type == 'EmployeeId'
    assert body.data_type.name == 'EmployeeId'
    assert body.data_type.type == 'string'
    assert isinstance(body.data_type, data_types.StringDataType)
