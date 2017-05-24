# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
"""
Tests for handling of data type expressions in RAML 1.0.

"""

import os
import pytest

from ramlfications.parser import parse_raml
from ramlfications.config import setup_config
from ramlfications.utils import load_file

from tests.base import RAML_10


@pytest.fixture(scope="session")
def api():
    ramlfile = os.path.join(RAML_10, "data_types/data_type_expressions.raml")
    loaded_raml = load_file(ramlfile)
    conffile = os.path.join(RAML_10, "test-config.ini")
    config = setup_config(conffile)
    return parse_raml(loaded_raml, config)


def get_named_type(api, name):
    t, = api.types.filter_by(name=name)
    return t


def test_definition_by_expression(api):
    typeobj = get_named_type(api, "Organization")
    assert typeobj.example is None
    assert typeobj.examples is None
    assert typeobj.name == "Organization"
    assert typeobj.type == "Org"
    assert typeobj.description.raw == ""
    assert typeobj.display_name == "Organization"


@pytest.mark.skip(reason="Union types not yet implemented.")
def test_array_definition_by_expression(api):
    typeobj = get_named_type(api, "Organizations")
    assert typeobj.example is None
    assert typeobj.examples is None
    assert typeobj.name == "Organizations"
    assert typeobj.description.raw == ""
    assert typeobj.display_name == "Organizations"
    # TODO: Figure out what this should look like.
    # assert typeobj.type == "Organization[]"


@pytest.mark.skip(reason="Union types not yet implemented.")
def test_definition_by_union_expression(api):
    typeobj = get_named_type(api, "FunPet")
    assert typeobj.example is None
    assert typeobj.examples is None
    assert typeobj.name == "FunPet"
    assert typeobj.type == "Python | Boa"
    assert typeobj.description.raw == ""
    assert typeobj.display_name == "FunPet"
