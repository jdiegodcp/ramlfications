# -*- coding: utf-8 -*-
"""
Tests for RAML 1.0 ``uses`` library resolution and the dotted
``LibName.member`` notation, including libraries used by libraries.
"""

import os

import pytest

from ramlfications import parse
from ramlfications.models import data_types

from tests.base import RAML_10


@pytest.fixture(scope="session")
def api():
    ramlfile = os.path.join(RAML_10, "libraries.raml")
    return parse(ramlfile)


def test_uses_returns_library_objects(api):
    assert len(api.uses) == 1
    lib = api.uses[0]
    assert lib.name == "common"
    assert lib.usage == "Common definitions"


def test_library_types_addressable_dotted(api):
    names = [t.name for t in api.types]
    assert "common.BaseError" in names
    assert "common.Error" in names


def test_library_type_applied_to_body(api):
    res = api.resources[0]
    body = res.responses[0].body[0]
    assert body.type == "common.Error"
    assert body.data_type.name == "common.Error"
    assert isinstance(body.data_type, data_types.ObjectDataType)


def test_inheritance_within_library(api):
    error = api.types.filter_by(name="common.Error").one()
    assert error.type == "common.BaseError"
    # own property plus the property inherited from BaseError
    assert "code" in error.properties
    assert "message" in error.properties


def test_nested_library_objects(api):
    lib = api.uses[0]
    assert len(lib.uses) == 1
    nested = lib.uses[0]
    assert nested.name == "base"
    assert nested.usage == "Base definitions"


def test_nested_library_types_addressable(api):
    names = [t.name for t in api.types]
    assert "common.base.Payload" in names


def test_nested_library_reference_rewritten(api):
    envelope = api.types.filter_by(name="common.Envelope").one()
    assert envelope.properties["payload"].type == "common.base.Payload"


def test_library_trait_addressable(api):
    trait = api.traits.filter_by(name="common.paged").one()
    assert trait.query_params[0].name == "page"


def test_library_annotation_type_addressable(api):
    names = [a.name for a in api.annotation_types]
    assert "common.deprecated" in names


def test_library_members_attached(api):
    lib = api.uses[0]
    type_names = [t.name for t in lib.types]
    assert type_names == [
        "common.BaseError", "common.Error", "common.Envelope"
    ]
    # nested library members belong to the nested Library object
    assert lib.uses[0].types[0].name == "common.base.Payload"
