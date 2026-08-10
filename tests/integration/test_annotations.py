# -*- coding: utf-8 -*-
"""
Tests for RAML 1.0 annotationTypes declarations and applied annotations.
"""

import os

import pytest

from ramlfications import parse
from ramlfications.models import data_types

from tests.base import RAML_10


@pytest.fixture(scope="session")
def api():
    ramlfile = os.path.join(RAML_10, "annotations.raml")
    return parse(ramlfile)


def test_annotation_types_declared(api):
    names = [a.name for a in api.annotation_types]
    assert names == ["monitoring", "clearanceLevel", "deprecated"]


def test_annotation_type_shorthand(api):
    monitoring = api.annotation_types.filter_by(name="monitoring")[0]
    assert monitoring.type == "boolean"
    assert isinstance(monitoring.data_type, data_types.BooleanDataType)


def test_annotation_type_full_declaration(api):
    clearance = api.annotation_types.filter_by(name="clearanceLevel")[0]
    assert clearance.type == "string"
    assert clearance.allowed_targets == ["Method"]
    assert clearance.description.raw == "The clearance level required"
    assert isinstance(clearance.data_type, data_types.StringDataType)


def test_method_annotation_applied(api):
    res = api.resources[0]
    annotations = {a.name: a for a in res.annotations}
    assert annotations["monitoring"].value is True
    assert annotations["monitoring"].annotation_type.type == "boolean"


def test_resource_annotation_applied(api):
    res = api.resources[0]
    annotations = {a.name: a for a in res.annotations}
    assert annotations["clearanceLevel"].value == "high"


def test_undeclared_annotation_has_no_type(api):
    res = api.resources[0]
    annotations = {a.name: a for a in res.annotations}
    assert annotations["undeclared"].annotation_type is None
