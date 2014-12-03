#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

import os

from ramlfications.loader import RAMLLoader, LoadRamlFileError
from ramlfications.validate import InvalidRamlFileError, validate

from .base import BaseTestCase


class TestValidateRAML(BaseTestCase):
    def setUp(self):
        self.here = os.path.abspath(os.path.dirname(__file__))

    def fail_validate(self, error_class, raml_file, expected_msg):
        self.load_object = RAMLLoader(raml_file)
        e = self.assert_raises(error_class, validate,
                               load_object=self.load_object)
        self.raml_file = raml_file
        e = self.assert_raises(error_class, validate_raml,
                               raml_file=self.raml_file, prod=True)

        self.assertEqual(expected_msg, str(e))

    def test_nonexistant_raml_file(self):
        nonexistant_file = "examples/this-file-doesnt-exist.raml"
        raml_file = os.path.join(self.here, nonexistant_file)
        expected_msg = ("[Errno 2] No such file or directory: '/Users/lynn/Dev"
                        "/spotify/ramlfications/tests/examples/this-file-"
                        "doesnt-exist.raml'")
        self.fail_validate(LoadRamlFileError, raml_file, expected_msg)

    def test_validate_raml_header(self):
        invalid_header = "examples/incorrect-raml-header.raml"
        raml_file = os.path.join(self.here, invalid_header)
        expected_msg = 'Not a valid RAML header: #%FOO.'

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_validate_raml_version(self):
        invalid_header = "examples/invalid-version-raml-header.raml"
        raml_file = os.path.join(self.here, invalid_header)
        expected_msg = 'Not a valid version of RAML: 0.9.'

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_validate_title(self):
        no_title = "examples/validate/no-title.raml"
        raml_file = os.path.join(self.here, no_title)
        expected_msg = 'RAML File does not define an API title.'

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_validate_version(self):
        no_version = "examples/validate/no-version.raml"
        raml_file = os.path.join(self.here, no_version)
        expected_msg = 'RAML File does not define an API version.'

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_validate_base_uri(self):
        no_base_uri = "examples/validate/no-base-uri.raml"
        raml_file = os.path.join(self.here, no_base_uri)
        expected_msg = 'RAML File does not define the baseUri.'

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_validate_base_params(self):
        no_default_param = "examples/validate/no-default-base-uri-params.raml"
        raml_file = os.path.join(self.here, no_default_param)
        expected_msg = "'domainName' needs a default parameter."

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_validate_resource_responses(self):
        invalid_responses = "examples/validate/responses.raml"
        raml_file = os.path.join(self.here, invalid_responses)

        expected_msg = "'anInvalidKey' not a valid Response parameter."

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_validate_docs_title(self):
        docs_no_title = "examples/validate/docs-no-title.raml"
        raml_file = os.path.join(self.here, docs_no_title)

        expected_msg = "API Documentation requires a title."

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_validate_docs_content(self):
        no_content = "examples/validate/docs-no-content.raml"
        raml_file = os.path.join(self.here, no_content)
        expected_msg = "API Documentation requires content defined."

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_validate_security_scheme(self):
        invalid_sec_scheme = "examples/validate/invalid-security-scheme.raml"
        raml_file = os.path.join(self.here, invalid_sec_scheme)
        expected_msg = "'Invalid Scheme' is not a valid Security Scheme."

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)
