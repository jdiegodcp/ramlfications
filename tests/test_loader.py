#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

import os

import pytest
from six import iteritems

from ramlfications import loader
from ramlfications.errors import LoadRAMLFileError

from .base import EXAMPLES


def dict_equal(dict1, dict2):
    for k, v1 in list(iteritems(dict1)):
        assert k in dict2
        v2 = dict2[k]
        assert v1, v2
    return True


def test_raml_basestring():
    raml_file = os.path.join(str(EXAMPLES + "complete-valid-example.raml"))
    raml = loader.RAMLLoader().load(raml_file)
    assert raml is not None


def test_raml_fileobj():
    raml_file = os.path.join(EXAMPLES + "complete-valid-example.raml")
    with open(raml_file) as f:
        raml = loader.RAMLLoader().load(f)
        assert raml is not None
        assert raml.raml_file.closed


def test_no_raml_file():
    raml_file = os.path.join(EXAMPLES + "this-file-doesnt-exist.raml")
    with pytest.raises(LoadRAMLFileError):
        loader.RAMLLoader().load(raml_file)


def test_none_raml_file():
    raml_file = None
    with pytest.raises(LoadRAMLFileError):
        loader.RAMLLoader().load(raml_file)


def test_root_includes():
    raml_file = os.path.join(EXAMPLES + "base-includes.raml")
    raml = loader.RAMLLoader().load(raml_file)

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

    assert dict_equal(raml.data, expected_data)


def test_incorrect_raml_obj():
    raml_file = dict(nota="raml_file")
    with pytest.raises(LoadRAMLFileError):
        loader.RAMLLoader().load(raml_file)
