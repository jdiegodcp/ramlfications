# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

import os

import pytest

from ramlfications import parse, load, loads, validate
from ramlfications.raml import RootNode
from ramlfications.errors import LoadRAMLError

from .base import EXAMPLES


@pytest.fixture(scope="session")
def raml():
    return os.path.join(EXAMPLES + "complete-valid-example.raml")


@pytest.fixture(scope="session")
def raml_string():
    return """#%RAML 0.8
---
title: GitHub API
version: v3
baseUri: https://api.github.com/
"""


def test_parse(raml):
    config = os.path.join(EXAMPLES + "test-config.ini")
    result = parse(raml, config)
    assert result
    assert isinstance(result, RootNode)


def test_parse_nonexistant_file():
    raml_file = "/tmp/non-existant-raml-file.raml"
    with pytest.raises(LoadRAMLError):
        parse(raml_file)


def test_load(raml):
    result = load(raml)
    assert result
    assert isinstance(result, dict)


def test_load_nonexistant_file():
    raml_file = "/tmp/non-existant-raml-file.raml"
    with pytest.raises(LoadRAMLError):
        parse(raml_file)


def test_loads(raml_string):
    result = loads(raml_string)
    assert result
    assert isinstance(result, dict)


def test_validate(raml):
    result = validate(raml)
    assert result is None


def test_validate_nonexistant_file():
    raml_file = "/tmp/non-existant-raml-file.raml"
    with pytest.raises(LoadRAMLError):
        validate(raml_file)
