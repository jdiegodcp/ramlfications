#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

import os

from ramlfications import validate

from .base import BaseTestCase


class TestValidateRAML(BaseTestCase):
    def setUp(self):
        self.here = os.path.abspath(os.path.dirname(__file__))

    def test_validate_raml_header(self):
        raml_file = os.path.join(self.here, "examples/spotify-web-api.raml")
        raml = validate.ValidateRAML(raml_file)

        expected_header = "#%RAML 0.8"

        raml_def, version = raml.validate_raml_header()
        self.assertEqual(raml_def, expected_header.split()[0])
        self.assertEqual(version, expected_header.split()[1])

    def test_validate_raml_header_invalid_version(self):
        r = "examples/invalid-version-raml-header.raml"
        raml_file = os.path.join(self.here, r)
        raml = validate.ValidateRAML(raml_file)

        self.assertRaises(validate.ValidateRAMLError,
                          lambda: raml.validate_raml_header())

    def test_validate_raml_header_invalid_raml_def(self):
        r = "examples/incorrect-raml-header.raml"
        raml_file = os.path.join(self.here, r)
        raml = validate.ValidateRAML(raml_file)

        self.assertRaises(validate.ValidateRAMLError,
                          lambda: raml.validate_raml_header())
