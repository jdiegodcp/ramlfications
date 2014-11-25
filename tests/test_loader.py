#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

import os

from ramlfications import loader

from .base import BaseTestCase


class TestRAMLLoader(BaseTestCase):
    def setUp(self):
        # Weird variable name. Please improve to something more meaningful.
        self.here = os.path.abspath(os.path.dirname(__file__))

    def test_repr(self):
        raml_file = os.path.join(self.here, "examples/spotify-web-api.raml")
        obj = loader.RAMLLoader(raml_file)

        self.assertEqual(repr(obj), '<RAMLLoader(raml_file="{0}")>'.format(
                         raml_file))

    def test_raml_file(self):
        # Everything this method does seems already be covered in test_repr
        # Can this method be deleted?
        raml_file = os.path.join(self.here, "examples/spotify-web-api.raml")
        raml = loader.RAMLLoader(raml_file).load()
        self.assertIsNotNone(raml)

    def test_no_raml_file(self):
        raml_file = "examples/this-file-doesnt-exist.raml"
        self.assertRaises(loader.LoadRamlFileError,
                          lambda: loader.RAMLLoader(raml_file).load())

    def test_none_raml_file(self):
        raml_file = None
        self.assertRaises(loader.LoadRamlFileError,
                          lambda: loader.RAMLLoader(raml_file).load())

    def test_root_includes(self):
        raml_file = os.path.join(self.here, "examples/base-includes.raml")
        raml = loader.RAMLLoader(raml_file).load()

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

        self.assertDictEqual(raml, expected_data)
