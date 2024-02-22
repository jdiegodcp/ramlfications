# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB
from __future__ import absolute_import, division, print_function

import os

import pytest

from ramlfications.config import setup_config
from ramlfications.parser import parse_raml
from ramlfications.utils import load_file

from tests.base import RAML_ORG_EXAMPLES


@pytest.fixture(scope="session")
def api():
    typesystem = os.path.join(RAML_ORG_EXAMPLES, "typesystem")
    ramlfile = os.path.join(typesystem, "simple.raml")
    loaded_raml = load_file(ramlfile)
    configfile = os.path.join(RAML_ORG_EXAMPLES, "simple_config.ini")
    config = setup_config(configfile)
    return parse_raml(loaded_raml, config)


def test_create_root(api):
    assert api.title == "API with Types"
    assert api.raml_version == "1.0"


def test_types(api):
    assert len(api.types) == 1

    user = api.types[0]
    assert user.name == 'User'
    assert user.type == 'object'
    assert len(user.properties) == 3

    first = user.properties.get('firstName')
    last = user.properties.get('lastName')
    age = user.properties.get('age')

    assert first.default is None
    assert last.default is None
    assert age.default is None

    assert first.required is False
    assert last.required is False
    assert age.required is False

    assert first.type == 'string'
    assert last.type == 'string'
    assert age.type == 'number'


def test_assigned_user_type(api):
    res = api.resources[0]

    assigned_type = res.responses[0].body[0].data_type
    assert assigned_type.name == 'User'
