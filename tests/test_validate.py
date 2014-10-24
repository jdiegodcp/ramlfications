#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

import os

from ramlfications.validate import RAMLValidationError, validate

from .base import BaseTestCase


class TestValidateRAML(BaseTestCase):
    def setUp(self):
        self.here = os.path.abspath(os.path.dirname(__file__))

    def test_validate_header(self):
        invalid_header = "examples/invalid-version-raml-header.raml"
        raml_file = os.path.join(self.here, invalid_header)

        self.assertRaises(RAMLValidationError, lambda: validate(raml_file))

    def test_validate_title(self):
        no_title = "examples/validate/no-title.raml"
        raml_file = os.path.join(self.here, no_title)

        self.assertRaises(RAMLValidationError, lambda: validate(raml_file))

    def test_validate_base_uri(self):
        no_base_uri = "examples/validate/no-base-uri.raml"
        raml_file = os.path.join(self.here, no_base_uri)

        self.assertRaises(RAMLValidationError, lambda: validate(raml_file))

    def test_validate_base_params(self):
        no_base_uri_params = "examples/validate/no-base-uri-params.raml"
        raml_file = os.path.join(self.here, no_base_uri_params)

        self.assertRaises(RAMLValidationError, lambda: validate(raml_file))

    def test_validate_node_responses(self):
        invalid_responses = "examples/validate/responses.raml"
        raml_file = os.path.join(self.here, invalid_responses)

        self.assertRaises(RAMLValidationError, lambda: validate(raml_file))

    def test_validate_docs_title(self):
        no_title = "examples/validate/docs-no-title.raml"
        raml_file = os.path.join(self.here, no_title)

        self.assertRaises(RAMLValidationError, lambda: validate(raml_file))

    def test_validate_docs_content(self):
        no_content = "examples/validate/docs-no-content.raml"
        raml_file = os.path.join(self.here, no_content)

        self.assertRaises(RAMLValidationError, lambda: validate(raml_file))

    def test_validate_security_scheme(self):
        invalid_sec_scheme = "examples/validate/invalid-security-scheme.raml"
        raml_file = os.path.join(self.here, invalid_sec_scheme)

        self.assertRaises(RAMLValidationError, lambda: validate(raml_file))
