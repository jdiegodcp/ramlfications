# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB
from __future__ import absolute_import, division, print_function

import os

import pytest

from ramlfications import errors
from ramlfications import validate

from .base import VALIDATE


raises = pytest.raises(errors.InvalidRAMLError)


# Search a list of errors for a specific error
def _error_exists(error_list, error_type, error_msg):
    for e in error_list:
        if isinstance(e, error_type) and e.args == error_msg:
            return True

    return False


def load_raml(filename):
    return os.path.join(VALIDATE + filename)


def load_config(filename):
    return os.path.join(VALIDATE + filename)


def test_default_to_validate():
    # Should validate even though it's set to "false" in config
    raml = "tests/data/validate/invalid-protocols.raml"
    config = "tests/data/validate/validation-off.ini"
    with raises as e:
        validate(raml, config)
    msg = ("'FTP' not a valid protocol for a RAML-defined API.",)
    assert _error_exists(e.value.errors, errors.InvalidRootNodeError, msg)


def test_default_to_validate_no_config():
    # Should validate even though it's set to "false" in config
    raml = "tests/data/validate/invalid-protocols.raml"
    with raises as e:
        validate(raml)
    msg = ("'FTP' not a valid protocol for a RAML-defined API.",)
    assert _error_exists(e.value.errors, errors.InvalidRootNodeError, msg)


def test_invalid_root_protocols():
    raml = "tests/data/validate/invalid-protocols.raml"
    config = "tests/data/validate/valid-config.ini"
    with raises as e:
        validate(raml, config)
    msg = ("'FTP' not a valid protocol for a RAML-defined API.",)
    assert _error_exists(e.value.errors, errors.InvalidRootNodeError, msg)


def test_undefined_version():
    raml = load_raml("no-version.raml")
    config = load_config("valid-config.ini")
    parsed_raml = validate(raml, config)
    assert not hasattr(parsed_raml, "errors")


def test_invalid_version_base_uri():
    raml = load_raml("no-version-base-uri.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)
    msg = ("RAML File's baseUri includes {version} parameter but no "
           "version is defined.",)
    assert _error_exists(e.value.errors, errors.InvalidRootNodeError, msg)


def test_undefined_base_uri_and_title():
    raml = load_raml("no-base-uri-no-title.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)
    assert len(e.value.errors) == 2
    assert isinstance(e.value.errors[0], errors.InvalidRootNodeError)
    assert isinstance(e.value.errors[1], errors.InvalidRootNodeError)


def test_invalid_base_uri_not_defined():
    raml = load_raml("no-base-uri.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)
    msg = ("RAML File does not define the baseUri.",)
    assert _error_exists(e.value.errors, errors.InvalidRootNodeError, msg)


def test_invalid_base_uri_wrong_type():
    raml = load_raml("invalid-base-uri-params.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)
    msg = ("Validation errors were found.",)
    msg1 = ("baseUriParameter 'domainName' must be a string",)
    assert e.value.args == msg
    assert _error_exists(e.value.errors, errors.InvalidRootNodeError, msg1)


def test_invalid_base_uri_optional():
    raml = load_raml("optional-base-uri-params.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)
    msg = ("baseUriParameter 'domainName' must be required",)
    assert _error_exists(e.value.errors, errors.InvalidRootNodeError, msg)


def test_invalid_uri_params_version():
    raml = load_raml("version-in-uri-params.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)
    msg = ("'version' can only be defined in baseUriParameters.",)
    assert _error_exists(e.value.errors, errors.InvalidRootNodeError, msg)


def test_invalid_no_title():
    raml = load_raml("no-title.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)
    msg = ('RAML File does not define an API title.',)
    assert _error_exists(e.value.errors, errors.InvalidRootNodeError, msg)


def test_invalid_docs_not_list():
    raml = load_raml("docs-not-list.raml")
    config = load_config("valid-config.ini")
    with pytest.raises(AssertionError) as e:
        validate(raml, config)
    assert ("Error parsing documentation",) == e.value.args


def test_invalid_docs_no_title():
    raml = load_raml("docs-no-title.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)
    msg = ("API Documentation requires a title.",)
    assert _error_exists(e.value.errors, errors.InvalidRootNodeError, msg)


def test_invalid_docs_no_content():
    raml = load_raml("docs-no-content.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)
    msg = ("API Documentation requires content defined.",)
    assert _error_exists(e.value.errors, errors.InvalidRootNodeError, msg)


def test_assigned_undefined_resource_type():
    raml = load_raml("undefined-resource-type-str.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)
    msg = ("Resource Type 'undefined' is assigned to '/foo' but is not "
           "defined in the root of the API.",)
    assert _error_exists(e.value.errors, errors.InvalidResourceNodeError, msg)


def test_no_resources_defined():
    raml = load_raml("no-resources.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)
    msg = ("API does not define any resources.",)
    assert _error_exists(e.value.errors, errors.InvalidRootNodeError, msg)


def test_invalid_media_type():
    raml = load_raml("invalid-media-type.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)
    msg = ("Unsupported MIME Media Type: 'awesome/sauce'.",)
    assert _error_exists(e.value.errors, errors.InvalidRootNodeError, msg)


# TODO: move assert from parser to validate
def test_invalid_trait_obj():
    raml = load_raml("trait-unsupported-obj.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)
    msg = ("The assigned traits, '12', needs to be either an array of strings "
           "or dictionaries mapping parameter values to the trait",)
    assert _error_exists(e.value.errors, errors.InvalidResourceNodeError, msg)


def test_traits_undefined():
    raml = load_raml("trait-undefined.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)
    msg = ("Trait 'undefined' is assigned to '/users/{user_id}/playlists' "
           "but is not defined in the root of the API.",)
    assert _error_exists(e.value.errors, errors.InvalidResourceNodeError, msg)


def test_no_traits_defined():
    raml = load_raml("no-traits-defined.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)
    msg = ("Trying to assign traits that are not defined"
           "in the root of the API.",)
    assert _error_exists(e.value.errors, errors.InvalidResourceNodeError, msg)


def test_unsupported_trait_type_array_ints():
    raml = load_raml("trait-unsupported-type-array-ints.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)
    msg = ("'12' needs to be a string referring to a trait, or a dictionary "
           "mapping parameter values to a trait",)
    assert _error_exists(e.value.errors, errors.InvalidResourceNodeError, msg)


def test_too_many_assigned_resource_types():
    raml = load_raml("too-many-assigned-res-types.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)
    msg = ("Too many resource types applied to '/foobar'.",)
    assert _error_exists(e.value.errors, errors.InvalidResourceNodeError, msg)


#####
# Parameter Validators
#####
def test_invalid_request_header_param():
    raml = load_raml("invalid-parameter-type-header.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)
    msg = ("'invalidType' is not a valid primative parameter type",)
    assert _error_exists(e.value.errors, errors.InvalidParameterError, msg)


def test_invalid_body_mime_type():
    raml = load_raml("invalid-body-mime-type.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)
    msg = ("Unsupported MIME Media Type: 'invalid/mediatype'.",)
    assert _error_exists(e.value.errors, errors.InvalidParameterError, msg)


def test_invalid_body_schema():
    raml = load_raml("invalid-body-form-schema.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)
    msg = ("Validation errors were found.",)
    msg1 = ("Body must define formParameters, not schema/example.",)
    msg2 = ("Body with mime_type 'application/x-www-form-urlencoded' "
            "requires formParameters.",)
    assert msg == e.value.args
    assert _error_exists(e.value.errors, errors.InvalidParameterError, msg1)
    assert _error_exists(e.value.errors, errors.InvalidParameterError, msg2)


def test_invalid_body_example():
    raml = load_raml("invalid-body-form-example.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)

    msg = ("Validation errors were found.",)
    msg1 = ("Body must define formParameters, not schema/example.",)
    msg2 = ("Body with mime_type 'application/x-www-form-urlencoded' "
            "requires formParameters.",)
    assert msg == e.value.args
    assert _error_exists(e.value.errors, errors.InvalidParameterError, msg1)
    assert _error_exists(e.value.errors, errors.InvalidParameterError, msg2)


def test_invalid_body_no_form_params():
    raml = load_raml("invalid-body-no-form-params.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)
    msg = ("Body with mime_type 'application/x-www-form-urlencoded' requires "
           "formParameters.",)
    assert _error_exists(e.value.errors, errors.InvalidParameterError, msg)


def test_invalid_response_code_str():
    raml = load_raml("invalid-response-code-str.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)
    msg = (
        "Response code 'foo' must be an integer representing an HTTP code.",
    )
    assert _error_exists(e.value.errors, errors.InvalidParameterError, msg)


def test_invalid_response_code():
    raml = load_raml("invalid-response-code.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)
    msg = ("'299' not a valid HTTP response code.",)
    assert _error_exists(e.value.errors, errors.InvalidParameterError, msg)


#####
# Primative Validators
#####

def test_invalid_integer_number_type():
    raml = load_raml("invalid-integer-number-type.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)
    msg = ("invalidParamType must be either a number or integer to have "
           "minimum attribute set, not 'string'.",)
    assert _error_exists(e.value.errors, errors.InvalidParameterError, msg)


def test_invalid_string_type():
    raml = load_raml("invalid-string-type.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)
    msg = ("invalidParamType must be a string type to have min_length "
           "attribute set, not 'integer'.",)
    assert _error_exists(e.value.errors, errors.InvalidParameterError, msg)


#####
# ResourceType, Trait, and Security Scheme validators
#####

def test_empty_mapping_res_type():
    raml = load_raml("empty-mapping-resource-type.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)

    msg = ("The resourceType 'emptyType' requires definition.",)
    assert _error_exists(e.value.errors, errors.InvalidResourceNodeError, msg)


def test_empty_mapping_trait():
    raml = load_raml("empty-mapping-trait.raml")
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)

    msg = ("The trait 'emptyTrait' requires definition.",)
    assert _error_exists(e.value.errors, errors.InvalidResourceNodeError, msg)


def test_empty_mapping_sec_scheme_settings():
    _raml = "empty-mapping-security-scheme-settings.raml"
    raml = load_raml(_raml)
    config = load_config("valid-config.ini")
    with raises as e:
        validate(raml, config)
    msg = ("'settings' for security scheme 'EmptySettingsScheme' require "
           "definition.",)
    assert _error_exists(e.value.errors, errors.InvalidSecuritySchemeError,
                         msg)
