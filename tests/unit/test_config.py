# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

import os

import pytest


from ramlfications.config import setup_config
from ramlfications.config import (
    AUTH_SCHEMES, HTTP_RESP_CODES, MEDIA_TYPES, PROTOCOLS, HTTP_METHODS,
    HTTP_OPTIONAL, RAML_VERSIONS, PRIM_TYPES
)

from tests.base import RAML_08, VALIDATE_08


@pytest.fixture
def config():
    return os.path.join(RAML_08, "test-config.ini")


def _validates(parsed_config):
    # consumers read the option as ``str(value).lower() == "true"``
    return str(parsed_config["validate"]).lower() == "true"


def _write_config(tmp_path, text):
    config_file = tmp_path / "config.ini"
    config_file.write_text(text)
    return str(config_file)


@pytest.fixture
def basic_config():
    basic_conf = {
        "auth_schemes": AUTH_SCHEMES,
        "resp_codes": HTTP_RESP_CODES,
        "media_types": MEDIA_TYPES,
        "protocols": PROTOCOLS,
        "http_methods": HTTP_METHODS,
        "raml_versions": RAML_VERSIONS,
        "prim_types": PRIM_TYPES,
        "validate": True,
    }
    optional = [m + "?" for m in basic_conf["http_methods"]]
    basic_conf["http_optional"] = optional + basic_conf["http_methods"]
    return basic_conf


def _clean(a_list):
    return sorted(list(set(a_list)))


def _dict_equal(dict1, dict2):
    for k, v1 in list(dict1.items()):
        assert k in dict2
        v2 = dict2[k]
        assert v1 == v2, k
    return True


def test_no_config_file_given(basic_config):
    parsed_config = setup_config(config_file=None)
    assert parsed_config == basic_config


def test_config_file(config, basic_config):
    bc = basic_config  # lazy
    # custom values are appended in file order; only resp_codes is
    # sorted and deduplicated
    bc["resp_codes"] = _clean(
        bc["resp_codes"] + [420, 421, 422, 429, 430]
    )
    bc["auth_schemes"] = bc["auth_schemes"] + ["oauth_3_0", "oauth_4_0"]
    bc["media_types"] = bc["media_types"] + [
        "application/vnd.github.v3", "foo/bar"
    ]
    bc["protocols"] = bc["protocols"] + ["FTP"]
    bc["raml_versions"] = bc["raml_versions"] + ["0.8"]
    bc["production"] = 'True'
    bc["validate"] = 'False'

    parsed_config = setup_config(config)

    assert _dict_equal(bc, parsed_config)


def test_config_without_validate_option_keeps_validation():
    config_file = os.path.join(VALIDATE_08, "custom-only-config.ini")
    parsed_config = setup_config(config_file)

    assert _validates(parsed_config)
    assert "FTP" in parsed_config["protocols"]


@pytest.mark.parametrize("text,validates", [
    ("[main]\nvalidation = False\n", False),
    ("[main]\nvalidation = false\n", False),
    ("[main]\nvalidation = True\n", True),
])
def test_config_legacy_validation_option(tmp_path, text, validates):
    parsed_config = setup_config(_write_config(tmp_path, text))
    assert _validates(parsed_config) is validates


@pytest.mark.parametrize("text,validates", [
    ("[main]\nvalidate = True\nvalidation = False\n", True),
    ("[main]\nvalidate = False\nvalidation = True\n", False),
    ("[main]\nvalidate = false\n", False),
])
def test_config_validate_option_wins_over_legacy(tmp_path, text, validates):
    parsed_config = setup_config(_write_config(tmp_path, text))
    assert _validates(parsed_config) is validates


def test_http_optional_constant():
    assert "get?" in HTTP_OPTIONAL
    assert "get" in HTTP_OPTIONAL
    assert HTTP_OPTIONAL == setup_config()["http_optional"]


def test_no_config_file_found():
    config_file = "/tmp/a-nonexistent-RAML-config-file.ini"
    with pytest.raises(IOError) as e:
        setup_config(config_file)

    msg = ("No such file or directory: '{0}'".format(config_file),)
    assert e.value.args == msg
