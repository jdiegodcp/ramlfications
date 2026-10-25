# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

import os

import pytest

from ramlfications import parse, load, loads, validate
from ramlfications.models.raml import RAML08, RAML10
from ramlfications.errors import (
    InvalidRAMLError, InvalidVersionError, LoadRAMLError
)

from tests.base import RAML_08, RAML_10, VALIDATE_08


@pytest.fixture(scope="session")
def raml():
    return os.path.join(RAML_08, "complete-example.raml")


@pytest.fixture(scope="session")
def raml_string():
    return """#%RAML 0.8
---
title: GitHub API
version: v3
baseUri: https://api.github.com/
"""


def test_parse(raml):
    config = os.path.join(RAML_08, "test-config.ini")
    result = parse(raml, config)
    assert result
    assert isinstance(result, RAML08)


def test_parse_nonexistant_file():
    raml_file = "/tmp/non-existant-raml-file.raml"
    with pytest.raises(LoadRAMLError):
        parse(raml_file)


def test_parse_raml_string():
    # Issue #135: parse() should accept a string of RAML content,
    # not only a file path or file object.
    raml_string = """#%RAML 0.8
---
title: GitHub API
version: v3
baseUri: https://api.github.com/
/user:
  get:
    description: Get the authenticated user
"""
    result = parse(raml_string)
    assert result
    assert isinstance(result, RAML08)
    assert result.title == "GitHub API"
    assert result.resources[0].path == "/user"


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


def test_parse_dispatches_to_raml08(raml):
    result = parse(raml)
    assert isinstance(result, RAML08)
    assert result.raml_version == "0.8"


def test_parse_dispatches_to_raml10():
    # 1.0 documents parse through the default entry point, with no
    # custom config needed.
    raml_file = os.path.join(RAML_10, "examples.raml")
    result = parse(raml_file)
    assert isinstance(result, RAML10)
    assert result.raml_version == "1.0"


def test_parse_unsupported_version():
    raml_string = """#%RAML 2.0
title: From The Future
"""
    with pytest.raises(InvalidVersionError) as e:
        parse(raml_string)
    assert "2.0" in e.value.args[0]
    assert "0.8, 1.0" in e.value.args[0]


NO_TITLE = os.path.join(VALIDATE_08, "no-title.raml")


def test_parse_with_custom_only_config_validates():
    config = os.path.join(VALIDATE_08, "custom-only-config.ini")
    with pytest.raises(InvalidRAMLError) as e:
        parse(NO_TITLE, config)
    assert "does not define an API title" in str(e.value)


@pytest.mark.parametrize("text,raises", [
    (None, True),
    ("[custom]\nprotocols = FTP\n", True),
    ("[main]\nvalidate = False\n", False),
    ("[main]\nvalidate = false\n", False),
    ("[main]\nvalidation = False\n", False),
    ("[main]\nvalidate = True\nvalidation = False\n", True),
    ("[main]\nvalidate = False\nvalidation = True\n", False),
])
def test_parse_validation_by_config_contents(tmp_path, text, raises):
    config = None
    if text is not None:
        config_file = tmp_path / "config.ini"
        config_file.write_text(text)
        config = str(config_file)

    if raises:
        with pytest.raises(InvalidRAMLError,
                           match="does not define an API title"):
            parse(NO_TITLE, config)
    else:
        assert parse(NO_TITLE, config)
