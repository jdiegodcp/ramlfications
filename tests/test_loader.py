# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

import os

import pytest
from six import iteritems

from ramlfications import loader
from ramlfications.errors import LoadRAMLError

from .base import EXAMPLES


def dict_equal(dict1, dict2):
    for k, v1 in list(iteritems(dict1)):
        assert k in dict2
        v2 = dict2[k]
        assert v1, v2
    return True


def test_load_file():
    raml_file = os.path.join(EXAMPLES + "base-includes.raml")
    with open(raml_file) as f:
        raml = loader.RAMLLoader().load(f)

        expected_data = {
            'external': {
                'propertyA': 'valueA',
                'propertyB': 'valueB'
            },
            'foo': {
                'foo': 'FooBar',
                'bar': 'BarBaz'
            },
            'title': 'GitHub API Demo - Includes',
            'version': 'v3'
        }

        assert dict_equal(raml, expected_data)


def test_load_string():
    raml_str = ("""
                - foo
                - bar
                - baz
                """)
    raml = loader.RAMLLoader().load(raml_str)

    expected_data = ["foo", "bar", "baz"]
    assert raml.sort() == expected_data.sort()


def test_yaml_parser_error():
    raml_obj = os.path.join(EXAMPLES, "invalid_yaml.yaml")
    with pytest.raises(LoadRAMLError) as e:
        loader.RAMLLoader().load(open(raml_obj))
    msg = "Error parsing RAML:"
    assert msg in e.value.args[0]
