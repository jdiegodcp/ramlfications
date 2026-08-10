# -*- coding: utf-8 -*-
"""
Tests for handling of data type expressions in RAML 1.0.

"""

import os
import pytest

from ramlfications.models import data_types
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


def test_array_definition_by_expression(api):
    typeobj = get_named_type(api, "Organizations")
    assert typeobj.example is None
    assert typeobj.examples is None
    assert typeobj.name == "Organizations"
    assert typeobj.display_name == "Organizations"
    assert isinstance(typeobj, data_types.ArrayDataType)
    assert typeobj.type == "array"
    assert isinstance(typeobj.items, data_types.ObjectDataType)
    assert typeobj.items.name == "Organization"
    assert "name" in typeobj.items.properties


def test_definition_by_union_expression(api):
    typeobj = get_named_type(api, "FunPet")
    assert typeobj.example is None
    assert typeobj.examples is None
    assert typeobj.name == "FunPet"
    assert typeobj.type == "Python | Boa"
    assert typeobj.display_name == "FunPet"
    assert isinstance(typeobj, data_types.UnionDataType)
    members = typeobj.of
    assert [m.name for m in members] == ["Python", "Boa"]
    assert all(isinstance(m, data_types.ObjectDataType) for m in members)


def test_array_of_union_expression(api):
    typeobj = get_named_type(api, "FunPets")
    assert typeobj.name == "FunPets"
    assert isinstance(typeobj, data_types.ArrayDataType)
    assert isinstance(typeobj.items, data_types.UnionDataType)
    assert [m.name for m in typeobj.items.of] == ["Python", "Boa"]


def test_forward_reference_resolves(api):
    # FutureOrgs is declared before FutureOrg in the document
    typeobj = get_named_type(api, "FutureOrgs")
    assert isinstance(typeobj, data_types.ArrayDataType)
    assert isinstance(typeobj.items, data_types.ObjectDataType)
    assert typeobj.items.name == "FutureOrg"
