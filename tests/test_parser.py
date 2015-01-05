#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

import os
import unittest

from ramlfications import loader
from ramlfications import parse
from ramlfications.parser import RAMLParserError
from .base import BaseTestCase, EXAMPLES, VALIDATE


class TestAPIRoot(BaseTestCase):
    fixture = 'test_api_root.json'

    def setup_parsed_raml(self, ramlfile):
        return parse(ramlfile)

    def setUp(self):
        self.f = self.fixture_data.get(self.fixture).get  # fixtures setup
        raml_file = os.path.join(EXAMPLES + "spotify-web-api.raml")
        self.api = parse(raml_file)


class TestParser(BaseTestCase):
    def setup_parsed_raml(self, ramlfile):
        return parse(ramlfile)

    def setUp(self):
        raml_file = os.path.join(EXAMPLES + "spotify-web-api.raml")
        self.api = parse(raml_file)


class TestParserError(BaseTestCase):
    def setup_parsed_raml(self, ramlfile):
        return parse(ramlfile)

    def setUp(self):
        raml_file = os.path.join(EXAMPLES + "spotify-web-api.raml")
        self.api = parse(raml_file)

    def test_no_raml_file(self):
        raml_file = '/foo/bar.raml'
        self.assertRaises(loader.LoadRamlFileError,
                          lambda: self.setup_parsed_raml(raml_file))

    def test_set_traits_none_defined(self):
        raml_file = os.path.join(VALIDATE, "no-traits-defined.raml")

        self.assertRaises(RAMLParserError,
                          lambda: self.setup_parsed_raml(raml_file))

    def test_set_traits_undefined_str(self):
        raml_file = os.path.join(VALIDATE, "trait-undefined.raml")

        self.assertRaises(RAMLParserError,
                          lambda: self.setup_parsed_raml(raml_file))

    def test_set_traits_undefined_dict(self):
        raml_file = os.path.join(VALIDATE, "trait-undefined-dict.raml")

        self.assertRaises(RAMLParserError,
                          lambda: self.setup_parsed_raml(raml_file))

    @unittest.skip("FIX: see parser:__set_traits")
    def test_set_traits_unsupported_obj(self):
        raml_file = os.path.join(VALIDATE, "trait-unsupported-obj.raml")

        self.assertRaises(RAMLParserError,
                          lambda: self.setup_parsed_raml(raml_file))
