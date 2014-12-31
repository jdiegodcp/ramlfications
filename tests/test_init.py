#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

import os

from ramlfications import parse, load, validate
from ramlfications.raml import RAMLRoot
from ramlfications.loader import LoadRamlFileError, RAMLDict
from ramlfications.validate import InvalidRamlFileError

from .base import BaseTestCase, EXAMPLES


class TestParse(BaseTestCase):
    def setUp(self):
        self.raml_file = os.path.join(EXAMPLES + "spotify-web-api.raml")

    def test_parse(self):
        result = parse(self.raml_file)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, RAMLRoot)

    def test_parse_nonexistant_file(self):
        raml_file = "/tmp/non-existant-raml-file.raml"
        e = self.assert_raises(LoadRamlFileError, parse, raml_file=raml_file)
        msg = "[Errno 2] No such file or directory: '{0}'".format(raml_file)
        self.assertEqual(msg, str(e))

    def test_load(self):
        result = load(self.raml_file)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, RAMLDict)

    def test_load_nonexistant_file(self):
        raml_file = "/tmp/non-existant-raml-file.raml"
        e = self.assert_raises(LoadRamlFileError, load, raml_file=raml_file)
        msg = "[Errno 2] No such file or directory: '{0}'".format(raml_file)
        self.assertEqual(msg, str(e))

    def test_validate(self):
        result = validate(self.raml_file)
        self.assertIsNone(result)

    def test_validate_nonexistant_file(self):
        raml_file = "/tmp/non-existant-raml-file.raml"
        e = self.assert_raises(InvalidRamlFileError,
                               validate, raml_file=raml_file)
        msg = "[Errno 2] No such file or directory: '{0}'".format(raml_file)
        self.assertEqual(msg, str(e))
