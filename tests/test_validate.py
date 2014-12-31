#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

import os

from ramlfications.validate import InvalidRamlFileError, validate_raml

from .base import BaseTestCase, EXAMPLES, VALIDATE


class TestValidateRAML(BaseTestCase):
    def setUp(self):
        self.here = os.path.abspath(os.path.dirname(__file__))

    def fail_validate(self, error_class, raml_file, expected_msg):
        self.raml_file = raml_file
        e = self.assert_raises(error_class, validate_raml,
                               raml_file=self.raml_file, prod=True)

        self.assertEqual(expected_msg, str(e))

    def test_nonexistant_raml_file(self):
        raml_file = os.path.join(EXAMPLES, "this-file-doesnt-exist.raml")
        expected_msg = ("[Errno 2] No such file or directory: '" + EXAMPLES +
                        "this-file-doesnt-exist.raml'")
        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_validate_raml_header(self):
        raml_file = os.path.join(EXAMPLES, "incorrect-raml-header.raml")
        expected_msg = 'Not a valid RAML header: #%FOO.'

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_no_raml_header(self):
        raml_file = os.path.join(EXAMPLES, "no-raml-header.raml")
        expected_msg = ("RAML header empty. Please make sure the first line "
                        "of the file contains a valid RAML file definition.")

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_invalid_raml_header(self):
        raml_file = os.path.join(EXAMPLES, "invalid-raml-header.raml")
        expected_msg = ("Not a valid RAML header: #%RAML.")

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_validate_raml_version(self):
        raml_file = os.path.join(EXAMPLES, "invalid-version-raml-header.raml")
        expected_msg = 'Not a valid version of RAML: 0.9.'

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_validate_title(self):
        raml_file = os.path.join(VALIDATE, "no-title.raml")
        expected_msg = 'RAML File does not define an API title.'

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_validate_version(self):
        raml_file = os.path.join(VALIDATE, "no-version.raml")
        expected_msg = 'RAML File does not define an API version.'

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_validate_base_uri(self):
        raml_file = os.path.join(VALIDATE, "no-base-uri.raml")
        expected_msg = 'RAML File does not define the baseUri.'

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_validate_base_params(self):
        no_default_param = "no-default-base-uri-params.raml"
        raml_file = os.path.join(VALIDATE, no_default_param)
        expected_msg = "'domainName' needs a default parameter."

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_validate_resource_responses(self):
        raml_file = os.path.join(VALIDATE, "responses.raml")
        expected_msg = "'anInvalidKey' not a valid Response parameter."

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_has_resources(self):
        raml_file = os.path.join(VALIDATE, "no-resources.raml")
        expected_msg = "No resources are defined."
        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_validate_docs_title(self):
        raml_file = os.path.join(VALIDATE, "docs-no-title.raml")

        expected_msg = "API Documentation requires a title."

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_validate_docs_content(self):
        raml_file = os.path.join(VALIDATE, "docs-no-content.raml")
        expected_msg = "API Documentation requires content defined."

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_validate_security_scheme(self):
        invalid_sec_scheme = "invalid-security-scheme.raml"
        raml_file = os.path.join(VALIDATE, invalid_sec_scheme)
        expected_msg = "'Invalid Scheme' is not a valid Security Scheme."

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)
