#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

import os

from ramlfications import loader

from .base import BaseTestCase, EXAMPLES


class TestRAMLLoader(BaseTestCase):
    def test_repr(self):
        raml_file = os.path.join(EXAMPLES + "spotify-web-api.raml")
        obj = loader.RAMLLoader(raml_file)

        self.assertEqual(repr(obj), '<RAMLLoader(raml_file="{0}")>'.format(
                         raml_file))

    def test_raml_file(self):
        # Everything this method does seems already be covered in test_repr
        # Can this method be deleted?
        raml_file = os.path.join(EXAMPLES + "spotify-web-api.raml")
        raml = loader.RAMLLoader(raml_file).load()
        self.assertIsNotNone(raml)

    def test_raml_fileobj(self):
        raml_file = os.path.join(EXAMPLES + "spotify-web-api.raml")
        with open(raml_file) as f:
            loader_obj = loader.RAMLLoader(f)
            raml = loader_obj.load()
            self.assertIsNotNone(raml)
            self.assertEqual(loader_obj.raml_file.closed, True)

    def test_no_raml_file(self):
        raml_file = os.path.join(EXAMPLES + "this-file-doesnt-exist.raml")
        self.assertRaises(loader.LoadRamlFileError,
                          lambda: loader.RAMLLoader(raml_file).load())

    def test_none_raml_file(self):
        raml_file = None
        self.assertRaises(loader.LoadRamlFileError,
                          lambda: loader.RAMLLoader(raml_file).load())

    def test_root_includes(self):
        raml_file = os.path.join(EXAMPLES + "base-includes.raml")
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
