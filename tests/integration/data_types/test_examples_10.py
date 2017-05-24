# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
"""
Tests for handling of data type examples in RAML 0.8.

"""

import os
import pytest

from ramlfications import errors
from ramlfications.parser import parse_raml
from ramlfications.config import setup_config
from ramlfications.utils import load_file

from tests.base import RAML_10


@pytest.fixture(scope="session")
def api():
    ramlfile = os.path.join(RAML_10, "examples.raml")
    loaded_raml = load_file(ramlfile)
    conffile = os.path.join(RAML_10, "test-config.ini")
    config = setup_config(conffile)
    return parse_raml(loaded_raml, config)


def get_resource_body_type(api, resource):
    res, = api.resources.filter_by(name=resource)
    return res.body[0].type


def get_named_type(api, name):
    t, = api.types.filter_by(name=name)
    return t


def test_simple_example_structured(api):
    t = get_named_type(api, "with_example_structured")
    assert t.examples is None

    ex = t.example
    assert ex.description.raw == "This is a typical structure."
    assert ex.display_name == "Typical Example"
    assert ex.strict is True
    assert ex.value == {"key": "Yo."}


def test_simple_example_unstructured(api):
    t = get_named_type(api, "with_example_unstructured")
    assert t.examples is None

    ex = t.example
    assert ex.description is None
    assert ex.display_name is None
    assert ex.strict is True
    assert ex.value == {"key": "Example value."}


def test_multiple_examples(api):
    t = get_named_type(api, "with_multiple_examples")
    assert t.example is None
    assert len(t.examples) == 3

    ex, = t.examples.filter_by(name="simple")
    assert ex.description is None
    assert ex.display_name == "simple"
    assert ex.strict is True
    assert ex.value == "abc"

    ex, = t.examples.filter_by(name="fancy")
    assert ex.description is None
    assert ex.display_name == "fancy"
    assert ex.strict is True
    assert ex.value == "two words"

    ex, = t.examples.filter_by(name="excessive")
    assert ex.description.raw == "There's way too much text here.\n"
    assert ex.display_name == "Serious Overkill"
    assert ex.strict is False
    assert ex.value == {
        "error": ("This type is defined to be a string,"
                  " so this should not be a map.\n"),
    }


def test_header_with_example(api):
    h = api.resources.filter_by(name="/with_header")[0].headers[0]
    assert h.name == "x-extra-fluff"
    assert h.example.value is True
    assert h.example.description is None
    assert h.example.display_name is None
    assert h.example.strict is True


def test_header_with_mutiple_examples(api):
    headers = api.resources.filter_by(name="/with_header")[0].headers
    h = headers.filter_by(name="x-multiple")[0]
    assert h.name == "x-multiple"
    assert h.example is None
    assert len(h.examples) == 4

    ex, = h.examples.filter_by(name="simple")
    assert ex.description is None
    assert ex.display_name == "simple"
    assert ex.strict is True
    assert ex.value == "42"

    ex, = h.examples.filter_by(name="typical")
    assert ex.description.raw == "This is what we expect."
    assert ex.display_name == "Typical Value"
    assert ex.strict is True
    assert ex.value == "typical"

    ex, = h.examples.filter_by(name="special")
    assert ex.description.raw == "No one expects the ..."
    assert ex.display_name == "Surprise Visit"
    assert ex.strict is True
    assert ex.value == "Spanish Inqusition!"

    ex, = h.examples.filter_by(name="broken")
    assert ex.description.raw == "Send this for a 500"
    assert ex.display_name == "DON'T DO THIS"
    assert ex.strict is False
    assert ex.value == "breakfast"


def test_disallows_example_with_examples():
    ramlfile = os.path.join(RAML_10, "broken-example-with-examples.raml")
    loaded_raml = load_file(ramlfile)
    conffile = os.path.join(RAML_10, "test-config.ini")
    config = setup_config(conffile)
    with pytest.raises(errors.InvalidRAMLStructureError) as e:
        parse_raml(loaded_raml, config)
    assert str(e.value) == "example and examples cannot co-exist"


def test_disallows_non_map_examples():
    ramlfile = os.path.join(RAML_10, "broken-non-map-examples.raml")
    loaded_raml = load_file(ramlfile)
    conffile = os.path.join(RAML_10, "test-config.ini")
    config = setup_config(conffile)
    with pytest.raises(errors.InvalidRAMLStructureError) as e:
        parse_raml(loaded_raml, config)
    assert str(e.value) == "examples must be a map node"
