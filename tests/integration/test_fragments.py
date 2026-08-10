# -*- coding: utf-8 -*-
"""
Tests for RAML 1.0 typed fragments, parsed both standalone and when
included from an API document.
"""

import os

import pytest

from ramlfications import parse
from ramlfications.models import ResourceTypeNode, TraitNode
from ramlfications.models import SecuritySchemeNode
from ramlfications.models.libraries import Library
from ramlfications.models.root import Documentation

from tests.base import RAML_10

FRAGMENTS = os.path.join(RAML_10, "fragments")


# <--[ standalone parsing ]-->
def test_parse_standalone_trait():
    trait = parse(os.path.join(FRAGMENTS, "paged_trait.raml"))
    assert isinstance(trait, TraitNode)
    assert trait.name == "paged"
    assert trait.usage == "Apply to paginated collection methods"
    param_names = [q.name for q in trait.query_params]
    assert param_names == ["page", "perPage"]


def test_parse_standalone_resource_type():
    nodes = parse(
        os.path.join(FRAGMENTS, "collection_resource_type.raml"))
    # one node per declared method
    assert len(nodes) == 2
    assert all(isinstance(n, ResourceTypeNode) for n in nodes)
    assert [n.method for n in nodes] == ["get", "post"]
    assert all(n.name == "collection" for n in nodes)


def test_parse_standalone_security_scheme():
    scheme = parse(os.path.join(FRAGMENTS, "oauth2_scheme.raml"))
    assert isinstance(scheme, SecuritySchemeNode)
    assert scheme.name == "oauth_2_0"
    assert scheme.type == "OAuth 2.0"
    grants = scheme.settings.get("authorizationGrants")
    assert grants == ["authorization_code", "client_credentials"]


def test_parse_standalone_documentation_item():
    doc = parse(os.path.join(FRAGMENTS, "getting_started.raml"))
    assert isinstance(doc, Documentation)
    assert doc.title.raw == "Getting Started"
    assert "Welcome to the Example API" in doc.content.raw


def test_parse_standalone_library():
    library = parse(os.path.join(RAML_10, "libs", "common.raml"))
    assert isinstance(library, Library)
    assert library.usage == "Common definitions"
    type_names = [t.name for t in library.types]
    assert type_names == ["BaseError", "Error", "Envelope"]
    assert [t.name for t in library.traits] == ["paged"]
    assert [a.name for a in library.annotation_types] == ["deprecated"]
    # the nested `uses` library keeps its own namespace
    assert library.uses[0].name == "base"
    assert [t.name for t in library.uses[0].types] == ["base.Payload"]


# <--[ fragments included from an API document ]-->
@pytest.fixture(scope="session")
def api():
    ramlfile = os.path.join(FRAGMENTS, "fragments_api.raml")
    return parse(ramlfile)


def test_included_trait_fragment(api):
    trait = api.traits.filter_by(name="paged").one()
    param_names = [q.name for q in trait.query_params]
    assert param_names == ["page", "perPage"]


def test_included_resource_type_fragment(api):
    nodes = api.resource_types.filter_by(name="collection")
    assert [n.method for n in nodes] == ["get", "post"]


def test_included_security_scheme_fragment(api):
    scheme = api.security_schemes.filter_by(name="oauth_2_0").one()
    assert scheme.type == "OAuth 2.0"
    grants = scheme.settings.get("authorizationGrants")
    assert grants == ["authorization_code", "client_credentials"]


def test_included_documentation_item_fragment(api):
    doc = api.documentation[0]
    assert doc.title.raw == "Getting Started"


def test_trait_from_fragment_applied(api):
    res = api.resources[0]
    assert res.is_ == ["paged"]
