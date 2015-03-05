#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

import os

import pytest

from ramlfications import loader
from ramlfications.parser import parse_raml as parse
from ramlfications import errors
from .base import VALIDATE


raises = pytest.raises(errors.InvalidRootNodeError)


def load_raml(filename):
    raml_file = os.path.join(VALIDATE + filename)
    return loader.RAMLLoader().load(raml_file)


def test_invalid_root_protocols():
    raml = load_raml("invalid-protocols.raml")
    with raises as e:
        parse(raml)
    msg = ("'FTP' not a valid protocol for a RAML-defined API.",)
    assert e.value.args == msg


def test_invalid_version_not_defined():
    raml = load_raml("no-version.raml")
    with raises as e:
        parse(raml)
    msg = ('RAML File does not define an API version.',)
    assert e.value.args == msg


def test_invalid_version_base_uri():
    raml = load_raml("no-version-base-uri.raml")
    with raises as e:
        parse(raml)
    msg = ("RAML File's baseUri includes {version} parameter but no "
           "version is defined.",)
    assert e.value.args == msg


def test_invalid_base_uri_not_defined():
    raml = load_raml("no-base-uri.raml")
    with raises as e:
        parse(raml)
    msg = ("RAML File does not define the baseUri.",)
    assert e.value.args == msg


def test_invalid_base_uri_default_not_defined():
    raml = load_raml("no-default-base-uri-params.raml")
    with raises as e:
        parse(raml)
    msg = ("The 'default' parameter is not set for base URI "
           "parameter 'domainName'",)
    assert e.value.args == msg


def test_invalid_uri_params_version():
    raml = load_raml("version-in-uri-params.raml")
    with raises as e:
        parse(raml)
    msg = ("'version' can only be defined in baseUriParameters.",)
    assert e.value.args == msg


def test_invalid_no_title():
    raml = load_raml("no-title.raml")
    with raises as e:
        parse(raml)
    assert ('RAML File does not define an API title.',) == e.value.args


def test_invalid_docs_not_list():
    raml = load_raml("docs-not-list.raml")
    with pytest.raises(AssertionError) as e:
        parse(raml)
    assert ("Error parsing documentation",) == e.value.args


def test_invalid_docs_no_title():
    raml = load_raml("docs-no-title.raml")
    with raises as e:
        parse(raml)
    assert ("API Documentation requires a title.",) == e.value.args


def test_invalid_docs_no_content():
    raml = load_raml("docs-no-content.raml")
    with raises as e:
        parse(raml)
    assert ("API Documentation requires content defined.",) == e.value.args


def test_assigned_undefined_resource_type():
    raml = load_raml("undefined-resource-type-str.raml")
    with pytest.raises(errors.InvalidResourceNodeError) as e:
        parse(raml)
    msg = ("Resource Type 'undefined' is assigned to '/foo' but is not "
           "defined in the root of the API.",)
    assert msg == e.value.args


def test_no_resources_defined():
    raml = load_raml("no-resources.raml")
    with pytest.raises(errors.InvalidRootNodeError) as e:
        parse(raml)
    assert ("API does not define any resources.",) == e.value.args


def test_invalid_media_type():
    raml = load_raml("invalid-media-type.raml")
    with pytest.raises(errors.InvalidRootNodeError) as e:
        parse(raml)
    assert ("Unsupported MIME Media Type: 'awesome/sauce'.",) == e.value.args


# TODO: move assert from parser to validate
def test_invalid_trait_obj():
    raml = load_raml("trait-unsupported-obj.raml")
    with pytest.raises(AssertionError) as e:
        parse(raml)
    msg = ("Error parsing trait",)
    assert msg == e.value.args


def test_traits_undefined():
    raml = load_raml("trait-undefined.raml")
    with pytest.raises(errors.InvalidResourceNodeError) as e:
        parse(raml)
    msg = ("Trait 'undefined' is assigned to '/users/{user_id}/playlists' "
           "but is not defined in the root of the API.",)
    assert msg == e.value.args


def test_no_traits_defined():
    raml = load_raml("no-traits-defined.raml")
    with pytest.raises(errors.InvalidResourceNodeError) as e:
        parse(raml)
    msg = ("Trying to assign traits that are not defined"
           "in the root of the API.",)
    assert msg == e.value.args


# TODO: move assert from parser to validate
def test_unsupported_trait_type_str():
    raml = load_raml("trait-unsupported-type-str.raml")
    with pytest.raises(AssertionError) as e:
        parse(raml)
    msg = ("Error parsing trait",)
    assert msg == e.value.args


def test_unsupported_trait_type_array_ints():
    raml = load_raml("trait-unsupported-type-array-ints.raml")
    with pytest.raises(errors.InvalidResourceNodeError) as e:
        parse(raml)
    msg = ("'12' needs to be a string referring to a trait, or a dictionary "
           "mapping parameter values to a trait",)
    assert msg == e.value.args


def test_too_many_assigned_resource_types():
    raml = load_raml("too-many-assigned-res-types.raml")
    with pytest.raises(errors.InvalidResourceNodeError) as e:
        parse(raml)
    msg = ("Too many resource types applied to '/foobar'.",)
    assert msg == e.value.args


#####
# Parameter Validators
#####

def test_invalid_request_header_param():
    raml = load_raml("invalid-parameter-type-header.raml")
    with pytest.raises(errors.InvalidParameterError) as e:
        parse(raml)
    msg = ("'invalidType' is not a valid primative parameter type",)
    assert msg == e.value.args


def test_invalid_body_mime_type():
    raml = load_raml("invalid-body-mime-type.raml")
    with pytest.raises(errors.InvalidParameterError) as e:
        parse(raml)
    msg = ("Unsupported MIME Media Type: 'invalid/mediatype'.",)
    assert msg == e.value.args


def test_invalid_body_schema():
    raml = load_raml("invalid-body-form-schema.raml")
    with pytest.raises(errors.InvalidParameterError) as e:
        parse(raml)
    msg = ("Body must define formParameters, not schema/example.",)
    assert msg == e.value.args


def test_invalid_body_example():
    raml = load_raml("invalid-body-form-example.raml")
    with pytest.raises(errors.InvalidParameterError) as e:
        parse(raml)
    msg = ("Body must define formParameters, not schema/example.",)
    assert msg == e.value.args


def test_invalid_body_no_form_params():
    raml = load_raml("invalid-body-no-form-params.raml")
    with pytest.raises(errors.InvalidParameterError) as e:
        parse(raml)
    msg = ("Body with mime_type 'application/x-www-form-urlencoded' requires "
           "formParameters.",)
    assert msg == e.value.args


def test_invalid_response_code_str():
    raml = load_raml("invalid-response-code-str.raml")
    with pytest.raises(errors.InvalidParameterError) as e:
        parse(raml)
    msg = (
        "Response code 'foo' must be an integer representing an HTTP code.",
    )
    assert msg == e.value.args


def test_invalid_response_code():
    raml = load_raml("invalid-response-code.raml")
    with pytest.raises(errors.InvalidParameterError) as e:
        parse(raml)
    msg = ("'299' not a valid HTTP response code.",)
    assert msg == e.value.args


#####
# Primative Validators
#####

def test_invalid_integer_number_type():
    raml = load_raml("invalid-integer-number-type.raml")
    with pytest.raises(errors.InvalidParameterError) as e:
        parse(raml)
    msg = ("invalidParamType must be either a number or integer to have "
           "minimum attribute set, not 'string'.",)
    assert msg == e.value.args


def test_invalid_string_type():
    raml = load_raml("invalid-string-type.raml")
    with pytest.raises(errors.InvalidParameterError) as e:
        parse(raml)
    msg = ("invalidParamType must be a string type to have min_length "
           "attribute set, not 'integer'.",)
    assert msg == e.value.args
