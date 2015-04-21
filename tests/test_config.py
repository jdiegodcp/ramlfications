# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB
from __future__ import absolute_import, division, print_function

import os

import pytest

from six import iteritems

from ramlfications.config import setup_config
from ramlfications.config import (
    AUTH_SCHEMES, HTTP_RESP_CODES, MEDIA_TYPES, PROTOCOLS, HTTP_METHODS,
    RAML_VERSIONS, PRIM_TYPES
)

from .base import EXAMPLES


@pytest.fixture
def config():
    return os.path.join(EXAMPLES + "test-config.ini")


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
    }
    optional = [m + "?" for m in basic_conf["http_methods"]]
    basic_conf["http_optional"] = optional + basic_conf["http_methods"]
    return basic_conf


def _clean(a_list):
    return sorted(list(set(a_list)))


def _dict_equal(dict1, dict2):
    for k, v1 in list(iteritems(dict1)):
        assert k in dict2
        v2 = dict2[k]
        assert v1, v2
    return True


def test_no_config_file_given(basic_config):
    parsed_config = setup_config(config_file=None)
    assert parsed_config == basic_config


def test_config_file(config, basic_config):
    bc = basic_config  # lazy
    bc["resp_codes"] = _clean(bc["resp_codes"] + [420, 421, 422])
    bc["auth_schemes"] = _clean(
        bc["auth_schemes"] + ["oauth_3_0", "oauth_4_0"]
    )
    bc["media_types"] = _clean(
        bc["media_types"] + ["application/vnd.github.v3", "foo/bar"]
    )
    bc["protocols"] = _clean(bc["protocols"] + ["FTP"])
    bc["raml_versions"] = _clean(bc["raml_versions"] + ["0.8"])
    bc["production"] = 'True'
    bc["validate"] = 'True'

    parsed_config = setup_config(config)

    assert _dict_equal(bc, parsed_config)


def test_no_config_file_found():
    config_file = "/tmp/a-nonexistent-RAML-config-file.ini"
    with pytest.raises(IOError) as e:
        setup_config(config_file)

    msg = ("No such file or directory: '{0}'".format(config_file),)
    assert e.value.args == msg
