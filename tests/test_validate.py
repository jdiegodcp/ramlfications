#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

import os

from ramlfications import validate, parse
from ramlfications.validate import InvalidRamlFileError

from .base import BaseTestCase, EXAMPLES, VALIDATE


class TestValidateRAML(BaseTestCase):
    def setUp(self):
        self.here = os.path.abspath(os.path.dirname(__file__))

    # TODO: get rid of
    def setup_parsed_raml(self, raml_file):
        raml_file = os.path.join(raml_file[0], raml_file[1])
        return parse(raml_file)

    def fail_validate(self, error_class, raml_file, expected_msg, prod=True):
        raml_file = os.path.join(raml_file[0], raml_file[1])
        e = self.assert_raises(error_class, validate, raml_file=raml_file,
                               production=prod)

        self.assertEqual(expected_msg, str(e))

    #####
    # API Metadata Validation
    #####
    # __raml_header
    def test_validate_raml_header(self):
        raml_file = (EXAMPLES, "incorrect-raml-header.raml")
        expected_msg = 'Not a valid RAML header: #%FOO.'

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_no_raml_header(self):
        raml_file = (VALIDATE, "no-raml-header.raml")
        expected_msg = ("RAML header empty. Please make sure the first line "
                        "of the file contains a valid RAML file definition.")

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_invalid_raml_header(self):
        raml_file = (EXAMPLES, "invalid-raml-header.raml")
        expected_msg = ("Not a valid RAML header: #%RAML.")

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_validate_raml_version(self):
        raml_file = (EXAMPLES, "invalid-version-raml-header.raml")
        expected_msg = 'Not a valid version of RAML: 0.9.'

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    # __base_uri
    def test_validate_no_base_uri(self):
        raml_file = (VALIDATE, "no-base-uri.raml")
        expected_msg = 'RAML File does not define the baseUri.'

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    # __version
    def test_validate_version_base_uri(self):
        raml_file = (VALIDATE, "no-version.raml")
        expected_msg = 'RAML File does not define an API version.'

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_validate_no_version_base_uri(self):
        raml_file = (VALIDATE, "no-version-base-uri.raml")
        expected_msg = ("RAML File's baseUri includes {version} parameter but "
                        "no version is defined.")

        self.fail_validate(InvalidRamlFileError, raml_file,
                           expected_msg, prod=False)

    # __api_title
    def test_validate_title(self):
        raml_file = (VALIDATE, "no-title.raml")
        expected_msg = 'RAML File does not define an API title.'

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    # __documentation
    def test_documentation_no_title(self):
        raml_file = (EXAMPLES, "docs-no-title-parameter.raml")
        expected_msg = "API Documentation requires a title."

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_validate_docs_content(self):
        raml_file = (VALIDATE, "docs-no-content.raml")
        expected_msg = "API Documentation requires content defined."

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    # __base_uri_params
    def test_validate_no_default_base_param(self):
        no_default_param = "no-default-base-uri-params.raml"
        raml_file = (VALIDATE, no_default_param)
        expected_msg = ("The 'default' parameter is not set for base URI "
                        "parameter 'domainName'")

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    # __schemas
    def test_validate_schemas(self):
        pass

    # __protocols
    def test_validate_protocols(self):
        invalid_protocols = "invalid-protocols.raml"
        raml_file = (VALIDATE, invalid_protocols)
        expected_msg = "'FTP' not a valid protocol for a RAML-defined API."

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    # __mediatype
    def test_media_type(self):
        invalid_media_type = "invalid-media-type.raml"
        raml_file = (VALIDATE, invalid_media_type)
        expected_msg = "Unsupported MIME Media Type: 'awesome/sauce'."

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    # __security_schemes
    def test_validate_security_scheme(self):
        invalid_sec_scheme = "invalid-security-scheme.raml"
        raml_file = (VALIDATE, invalid_sec_scheme)
        expected_msg = "'invalid-scheme' is not a valid Security Scheme."

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    # __uri_params
    def test_validate_version_uri_params(self):
        raml_file = (VALIDATE, "version-in-uri-params.raml")
        expected_msg = "'version' can only be defined in baseUriParameters."

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    # __has_resources
    def test_has_resources(self):
        raml_file = (VALIDATE, "no-resources.raml")
        expected_msg = "No resources are defined."
        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    # Trait Validation

    # ResourceType Validation

    # Resource Validation

    # Parameter Validation

    def test_validate_resource_responses(self):
        raml_file = (VALIDATE, "invalid-response-body.raml")
        expected_msg = "Unsupported MIME Media Type: \'invalid/mediatype\'."

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_validate_trait_responses(self):
        raml_file = (VALIDATE, "invalid-trait-response.raml")
        expected_msg = "'678' not a valid response code."

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_validate_resource_type_responses(self):
        raml_file = (VALIDATE, "invalid-resource-type-response.raml")
        expected_msg = "'678' not a valid response code."

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_raises_incorrect_response_code(self):
        raml_file = (EXAMPLES, "invalid-resp-code.raml")
        expected_msg = "'299' not a valid response code."

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_resource_types_too_many(self):
        raml_file = (EXAMPLES, "mapped-types-too-many.raml")
        expected_msg = "Too many resource types applied to '/magazines'."

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_resource_types_invalid_mapped_type(self):
        raml_path = "mapped-types-incorrect-resource-type.raml"
        raml_file = (EXAMPLES, raml_path)

        expected_msg = "'invalidResourceType' is not defined in resourceTypes"

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_invalid_body_keys(self):
        invalid_body = "invalid-body.raml"
        raml_file = (VALIDATE, invalid_body)
        expected_msg = ("'schema' may not be specified when the body's media "
                        "type is application/x-www-form-urlencoded or "
                        "multipart/form-data.")

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_invalid_secured_by(self):
        invalid_secured_by = "invalid-secured-by.raml"
        raml_file = (VALIDATE, invalid_secured_by)
        expected_msg = ("'not_a_scheme' is applied to '/foo' but is not "
                        "defined in the securitySchemes")

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_no_security_schemes(self):
        no_security_scheme = "no-security-scheme.raml"
        raml_file = (VALIDATE, no_security_scheme)
        expected_msg = ("No Security Schemes are defined in RAML file but "
                        "['oauth_2_0'] scheme is assigned to '/foo'.")

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_validate_data_exists(self):
        only_raml_header = "only-raml-header.raml"
        raml_file = (VALIDATE, only_raml_header)
        expected_msg = "No RAML data to parse."

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_validate_empty_file(self):
        empty_file = "empty-file.raml"
        raml_file = (VALIDATE, empty_file)
        expected_msg = "RAML File is empty"

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_traits_invalid_type(self):
        raml_file = (EXAMPLES, "invalid-trait-obj.raml")
        expected_msg = ("'1' needs to be a string referring to a trait, or a "
                        "dictionary mapping parameter values to a trait")

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)

    def test_uri_parameters_throws_exception(self):
        raml_file = (EXAMPLES, "uri-parameters-error.raml")
        expected_msg = "'version' can only be defined in baseUriParameters."

        self.fail_validate(InvalidRamlFileError, raml_file, expected_msg)
