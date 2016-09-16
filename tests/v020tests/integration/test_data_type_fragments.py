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
def api():
    ramlfile = os.path.join(V020EXAMPLES, "uses_data_fragment.raml")
    loaded_raml = load_file(ramlfile)
    configfile = os.path.join(RAMLEXAMPLES, "simple_config.ini")
    config = setup_config(configfile)
    return parse_raml(loaded_raml, config)


def test_includes_fragment(api):
    assert len(api.types) == 2


def test_person_data_type(api):
    person = api.types[0]

    assert person.type == 'object'
    assert person.name == 'Person'
    assert len(person.properties) == 1

    name = person.properties.get('name')
    assert name.required
    assert name.type == 'string'


def test_employee_data_type(api):
    employee = api.types[1]

    assert employee.type == 'Person'
    assert employee.name == 'Employee'
    assert len(employee.properties) == 2

    name = employee.properties.get('name')
    assert name.required
    assert name.type == 'string'

    id_ = employee.properties.get('id')
    assert id_.required
    assert id_.type == 'string'
