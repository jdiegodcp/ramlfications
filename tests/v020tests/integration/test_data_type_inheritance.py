# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB
from __future__ import absolute_import, division, print_function

import os

import pytest

from ramlfications.config import setup_config
from ramlfications.parser import parse_raml
from ramlfications.utils import load_file

from tests.base import RAMLEXAMPLES, V020EXAMPLES


@pytest.fixture(scope="session")
def fragment_api():
    ramlfile = os.path.join(V020EXAMPLES, "uses_data_fragment.raml")
    loaded_raml = load_file(ramlfile)
    configfile = os.path.join(RAMLEXAMPLES, "simple_config.ini")
    config = setup_config(configfile)
    return parse_raml(loaded_raml, config)


def test_includes_fragment(fragment_api):
    assert len(fragment_api.types) == 2


def test_person_data_type(fragment_api):
    person = fragment_api.types[0]

    assert person.type == 'object'
    assert person.name == 'Person'
    assert len(person.properties) == 1

    name = person.properties.get('name')
    assert name.required
    assert name.type == 'string'


def test_employee_data_type(fragment_api):
    employee = fragment_api.types[1]

    assert employee.type == 'Person'
    assert employee.name == 'Employee'
    assert len(employee.properties) == 2

    name = employee.properties.get('name')
    assert name.required
    assert name.type == 'string'

    id_ = employee.properties.get('id')
    assert id_.required
    assert id_.type == 'string'


@pytest.fixture(scope="session")
def api():
    ramlfile = os.path.join(V020EXAMPLES, "data_type_inheritance.raml")
    loaded_raml = load_file(ramlfile)
    configfile = os.path.join(RAMLEXAMPLES, "simple_config.ini")
    config = setup_config(configfile)
    return parse_raml(loaded_raml, config)


def test_inherit_name(api):
    person = api.types[0]
    props = person.properties
    first_name = props.get('firstName')
    assert first_name.required
    assert first_name.type == 'string'

    last_name = props.get('lastName')
    assert last_name.required
    assert last_name.type == 'string'

    middle_name = props.get('middleName')
    assert not middle_name.required
    assert middle_name.type == 'string'