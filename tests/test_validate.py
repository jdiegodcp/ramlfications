#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

import os

from ramlfications.validate import RAMLValidationError, ValidateRAML

from .base import BaseTestCase


class TestValidateRAML(BaseTestCase):
    def setUp(self):
        self.here = os.path.abspath(os.path.dirname(__file__))

    def setup_raml(self, path):
        raml_file = os.path.join(self.here, path)
        return ValidateRAML(raml_file)

    def test_raml_header_invalid_version(self):
        raml = self.setup_raml("examples/invalid-version-raml-header.raml")

        self.assertRaises(RAMLValidationError, lambda: raml.raml_header())

    def test_raml_header_invalid_raml_def(self):
        raml = self.setup_raml("examples/incorrect-raml-header.raml")

        self.assertRaises(RAMLValidationError, lambda: raml.raml_header())

    def test_api_title(self):
        raml = self.setup_raml("examples/validate/no-title.raml")

        self.assertRaises(RAMLValidationError, lambda: raml.api_title())

    def test_base_uri(self):
        raml = self.setup_raml("examples/validate/no-base-uri.raml")

        self.assertRaises(RAMLValidationError, lambda: raml.base_uri())

    def test_base_uri_params(self):
        raml = self.setup_raml("examples/validate/base-uri-params.raml")

        self.assertRaises(RAMLValidationError, lambda: raml.base_uri_params())

    def test_responses_invalid_keys(self):
        raml = self.setup_raml("examples/validate/responses.raml")

        self.assertRaises(RAMLValidationError, lambda: raml.node_response())

    def test_doc_no_title(self):
        raml = self.setup_raml("examples/validate/docs-no-title.raml")

        self.assertRaises(RAMLValidationError,
                          lambda: raml.root_documentation())

    def test_doc_no_content(self):
        raml = self.setup_raml("examples/validate/docs-no-content.raml")

        self.assertRaises(RAMLValidationError,
                          lambda: raml.root_documentation())

    def test_invalid_security_scheme(self):
        raml_file = "examples/validate/invalid-security-scheme.raml"
        raml = self.setup_raml(raml_file)

        self.assertRaises(RAMLValidationError,
                          lambda: raml.security_schemes())
