#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

import os

from ramlfications import loader

from .base import BaseTestCase


class TestRAMLLoader(BaseTestCase):
    def setUp(self):
        self.here = os.path.abspath(os.path.dirname(__file__))

    def test_raml_file(self):
        raml_file = os.path.join(self.here, "examples/spotify-web-api.raml")
        raml = loader.RAMLLoader(raml_file).raml
        self.assertIsNotNone(raml)

    def test_no_raml_file(self):
        raml_file = '/foo/bar.raml'
        self.assertRaises(loader.RAMLLoaderError,
                          lambda: loader.RAMLLoader(raml_file).raml)

    def test_root_includes(self):
        raml_file = os.path.join(self.here, "examples/base-includes.raml")
        raml = loader.RAMLLoader(raml_file).raml

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
