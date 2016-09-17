# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB
from __future__ import absolute_import, division, print_function

import os

import pytest

from ramlfications.config import setup_config
from ramlfications.models import data_types
from ramlfications.parser import parse_raml
from ramlfications.utils import load_file

from tests.base import RAML_ORG_EXAMPLES, RAML_10

DATA_TYPES = os.path.join(RAML_10, "data_types")


@pytest.fixture(scope="session")
def api():
    ramlfile = os.path.join(DATA_TYPES, "data_type_traits.raml")
    loaded_raml = load_file(ramlfile)
    configfile = os.path.join(RAML_ORG_EXAMPLES, "simple_config.ini")
    config = setup_config(configfile)
    return parse_raml(loaded_raml, config)


def test_api(api):
    assert len(api.types) == 1
    assert len(api.traits) == 1
    assert len(api.resources) == 1


def test_traits(api):
    paged = api.traits[0]

    assert len(paged.query_params) == 1
    q_param = paged.query_params[0]
    assert q_param.name == "id"
    assert q_param.type == "PageId"
    assert q_param.data_type.name == "PageId"
    assert q_param.data_type.type == "string"
    assert isinstance(q_param.data_type, data_types.StringDataType)


def test_resource(api):
    res = api.resources[0]

    assert res.name == "/employees"
    assert res.method == "get"
    assert res.is_ == ["paged"]
    assert len(res.traits) == 1
    assert len(res.query_params) == 1

    q_param = res.query_params[0]
    assert q_param.name == "id"
    assert q_param.type == "PageId"
    assert q_param.data_type.name == "PageId"
    assert q_param.data_type.type == "string"
    assert isinstance(q_param.data_type, data_types.StringDataType)
