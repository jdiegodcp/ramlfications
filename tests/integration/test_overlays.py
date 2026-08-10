# -*- coding: utf-8 -*-
"""
Tests for RAML 1.0 Overlay and Extension documents: `extends`
resolution, merge semantics, and the rule that overlays cannot change
behavioral aspects of their target.
"""

import os

import pytest

from ramlfications import parse
from ramlfications.errors import InvalidOverlayError

from tests.base import RAML_10

OVERLAYS = os.path.join(RAML_10, "overlays")


@pytest.fixture(scope="session")
def overlaid():
    return parse(os.path.join(OVERLAYS, "overlay_descriptions.raml"))


@pytest.fixture(scope="session")
def extended():
    return parse(os.path.join(OVERLAYS, "extension_admin.raml"))


# <--[ overlay ]-->
def test_overlay_overrides_title(overlaid):
    assert overlaid.title == "Friendly Base API"


def test_overlay_adds_documentation(overlaid):
    doc = overlaid.documentation[0]
    assert doc.title.raw == "About"
    assert "added by the overlay" in doc.content.raw


def test_overlay_overrides_descriptions(overlaid):
    res = overlaid.resources.filter_by(path="/users").one()
    assert res.description.raw == "Overlaid users description"
    assert res.display_name == "All the users"


def test_overlay_adds_annotation(overlaid):
    res = overlaid.resources.filter_by(path="/users").one()
    annotations = {a.name: a for a in res.annotations}
    assert annotations["audience"].value == "external"


def test_overlay_keeps_behavior_unchanged(overlaid):
    # same resources and methods as the target, and the target's
    # behavioral details (query parameters) are untouched
    assert [r.path for r in overlaid.resources] == ["/users"]
    res = overlaid.resources.filter_by(path="/users").one()
    assert res.method == "get"
    assert [q.name for q in res.query_params] == ["city"]


def test_overlay_may_not_change_behavior():
    with pytest.raises(InvalidOverlayError) as e:
        parse(os.path.join(OVERLAYS, "overlay_illegal.raml"))
    assert "/admin" in str(e.value)


# <--[ extension ]-->
def test_extension_adds_resource(extended):
    paths = [(r.path, r.method) for r in extended.resources]
    assert ("/admin", "get") in paths
    admin = extended.resources.filter_by(path="/admin").one()
    assert admin.description.raw == "Admin endpoint added by the extension"


def test_extension_merges_method_details(extended):
    users = extended.resources.filter_by(path="/users").one()
    assert sorted(q.name for q in users.query_params) == \
        ["city", "country"]


def test_extension_keeps_target_metadata(extended):
    assert extended.title == "Base API"
    assert extended.base_uri == "http://example.com/api"
