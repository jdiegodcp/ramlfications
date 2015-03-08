#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

import os

import pytest

from ramlfications import parse, load, validate
from ramlfications.raml import RootNode
from ramlfications.loader import RAMLDict
from ramlfications.errors import LoadRAMLFileError

from .base import EXAMPLES


@pytest.fixture
def raml():
    return os.path.join(EXAMPLES + "complete-valid-example.raml")


def test_parse(raml):
    config = os.path.join(EXAMPLES + "test-config.ini")
    result = parse(raml, config)
    assert result
    assert isinstance(result, RootNode)


def test_parse_nonexistant_file():
    raml_file = "/tmp/non-existant-raml-file.raml"
    with pytest.raises(LoadRAMLFileError):
        parse(raml_file)


def test_load(raml):
    result = load(raml)
    assert result
    assert isinstance(result, RAMLDict)


def test_load_nonexistant_file():
    raml_file = "/tmp/non-existant-raml-file.raml"
    with pytest.raises(LoadRAMLFileError):
        parse(raml_file)


def test_validate(raml):
    result = validate(raml)
    assert result is None


def test_validate_nonexistant_file():
    raml_file = "/tmp/non-existant-raml-file.raml"
    with pytest.raises(LoadRAMLFileError):
        validate(raml_file)
