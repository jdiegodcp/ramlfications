# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB
from __future__ import absolute_import, division, print_function

import os

import pytest

from ramlfications.parser import parse_raml
from ramlfications.config import setup_config
from ramlfications.utils import load_file


from tests.base import V020EXAMPLES, assert_not_set


# Root node properties:
# version, base_uri, base_uri_params, uri_params, protocols, title,
# documentation, schemas, media_tpe, secured_by, resource_types, traits
# resources, raml_obj, config, errors


@pytest.fixture(scope="session")
def api():
    ramlfile = os.path.join(V020EXAMPLES, "root_node.raml")
    loaded_raml = load_file(ramlfile)
    conffile = os.path.join(V020EXAMPLES, "test_config.ini")
    config = setup_config(conffile)
    return parse_raml(loaded_raml, config)


def test_root_node(api):
    assert api.title == "Example Web API"
    assert api.version == "v1"
    assert api.protocols == ["HTTPS"]
    uri = "https://{subDomain}.example.com/v1/{external_party}"
    assert api.base_uri == uri
    assert api.media_type == "application/json"
    assert api.secured_by == [{"oauth_2_0": {"scopes": ["user-email"]}}]
    assert len(api.base_uri_params) == 1
    assert len(api.uri_params) == 1
    assert len(api.documentation) == 1
    assert len(api.security_schemes) == 1
    assert len(api.schemas) == 1

    b = api.base_uri_params[0]
    assert b.name == "subDomain"
    assert b.display_name == "subDomain"
    assert b.description.raw == "subdomain of API server"
    assert b.type == "string"
    assert b.example == "sjc"
    assert b.required
    not_set = [
        "default", "enum", "max_length", "maximum", "min_length",
        "minimum", "pattern", "repeat"
    ]
    assert_not_set(b, not_set)

    u = api.uri_params[0]
    assert u.name == "external_party"
    assert u.display_name == "external_party"
    assert u.description.raw == "code of third-party partner"
    assert u.example == "gizmo_co"
    assert u.type == "string"
    assert u.required
    not_set = [
        "default", "enum", "max_length", "maximum", "min_length",
        "minimum", "pattern", "repeat"
    ]
    assert_not_set(b, not_set)

    d = api.documentation[0]
    assert d.title.raw == "Example Web API Docs"
    cont = ("Welcome to the _Example Web API_ demo specification. This is "
            "*not* the complete API\nspecification, and is meant for testing "
            "purposes within this RAML specification.\n")
    assert d.content.raw == cont

    s = api.security_schemes[0]
    assert s.name == "oauth_2_0"
