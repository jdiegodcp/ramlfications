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
        obj = loader.RAMLLoader().load(raml_file)

        self.assertEqual(repr(obj), '<RAMLDict(name="{0}")>'.format(
                         raml_file))

    def test_raml_basestring(self):
        # Everything this method does seems already be covered in test_repr
        # Can this method be deleted?
        raml_file = os.path.join(str(EXAMPLES + "spotify-web-api.raml"))
        raml = loader.RAMLLoader().load(raml_file)
        self.assertIsNotNone(raml)

    def test_raml_fileobj(self):
        raml_file = os.path.join(EXAMPLES + "spotify-web-api.raml")
        with open(raml_file) as f:
            raml = loader.RAMLLoader().load(f)
            self.assertIsNotNone(raml)
            self.assertEqual(raml.raml_file.closed, True)

    def test_no_raml_file(self):
        raml_file = os.path.join(EXAMPLES + "this-file-doesnt-exist.raml")
        self.assertRaises(loader.LoadRamlFileError,
                          lambda: loader.RAMLLoader().load(raml_file))

    def test_none_raml_file(self):
        raml_file = None
        self.assertRaises(loader.LoadRamlFileError,
                          lambda: loader.RAMLLoader().load(raml_file))

    def test_root_includes(self):
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

        self.assertDictEqual(raml.data, expected_data)

    def test_incorrect_raml_obj(self):
        raml_file = dict(nota="raml_file")
        self.assertRaises(loader.LoadRamlFileError,
                          lambda: loader.RAMLLoader().load(raml_file))
