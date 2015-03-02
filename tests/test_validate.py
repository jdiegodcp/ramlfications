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
    msg = "'FTP' not a valid protocol for a RAML-defined API."
    assert e.value.message == msg


def test_invalid_version_not_defined():
    raml = load_raml("no-version.raml")
    with raises as e:
        parse(raml)
    msg = 'RAML File does not define an API version.'
    assert e.value.message == msg


def test_invalid_version_base_uri():
    raml = load_raml("no-version-base-uri.raml")
    with raises as e:
        parse(raml)
    msg = ("RAML File's baseUri includes {version} parameter but no "
           "version is defined.")
    assert e.value.message == msg


def test_invalid_base_uri_not_defined():
    raml = load_raml("no-base-uri.raml")
    with raises as e:
        parse(raml)
    msg = "RAML File does not define the baseUri."
    assert e.value.message == msg


def test_invalid_base_uri_default_not_defined():
    raml = load_raml("no-default-base-uri-params.raml")
    with raises as e:
        parse(raml)
    msg = ("The 'default' parameter is not set for base URI "
           "parameter 'domainName'")
    assert e.value.message == msg


def test_invalid_uri_params_version():
    raml = load_raml("version-in-uri-params.raml")
    with raises as e:
        parse(raml)
    msg = "'version' can only be defined in baseUriParameters."
    assert e.value.message == msg


def test_invalid_no_title():
    raml = load_raml("no-title.raml")
    with raises as e:
        parse(raml)
    assert 'RAML File does not define an API title.' == e.value.message


def test_invalid_docs_not_list():
    raml = load_raml("docs-not-list.raml")
    with pytest.raises(AssertionError) as e:
        parse(raml)
    assert "Error parsing documentation" == e.value.message


def test_invalid_docs_no_title():
    raml = load_raml("docs-no-title.raml")
    with raises as e:
        parse(raml)
    assert "API Documentation requires a title." == e.value.message


def test_invalid_docs_no_content():
    raml = load_raml("docs-no-content.raml")
    with raises as e:
        parse(raml)
    assert "API Documentation requires content defined." == e.value.message


def test_assigned_undefined_resource_type():
    raml = load_raml("undefined-resource-type-str.raml")
    with pytest.raises(errors.InvalidResourceNodeError) as e:
        parse(raml)
    msg = ("Resource Type 'undefined' is assigned to '/foo' but is not "
           "defined in the root of the API.")
    assert msg == e.value.message


def test_no_resources_defined():
    raml = load_raml("no-resources.raml")
    with pytest.raises(errors.InvalidRootNodeError) as e:
        parse(raml)
    assert "API does not define any resources." == e.value.message


def test_invalid_media_type():
    raml = load_raml("invalid-media-type.raml")
    with pytest.raises(errors.InvalidRootNodeError) as e:
        parse(raml)
    assert "Unsupported MIME Media Type: 'awesome/sauce'." == e.value.message


# TODO: move assert from parser_wip to validate_wip
def test_invalid_trait_obj():
    raml = load_raml("trait-unsupported-obj.raml")
    with pytest.raises(AssertionError) as e:
        parse(raml)
    msg = "Error parsing trait"
    assert msg == e.value.message


def test_traits_undefined():
    raml = load_raml("trait-undefined.raml")
    with pytest.raises(errors.InvalidResourceNodeError) as e:
        parse(raml)
    msg = ("Trait 'undefined' is assigned to '/users/{user_id}/playlists' "
           "but is not defined in the root of the API.")
    assert msg == e.value.message


def test_no_traits_defined():
    raml = load_raml("no-traits-defined.raml")
    with pytest.raises(errors.InvalidResourceNodeError) as e:
        parse(raml)
    msg = ("Trying to assign traits that are not defined"
           "in the root of the API.")
    assert msg == e.value.message


# TODO: move assert from parser_wip to validate_wip
def test_unsupported_trait_type_str():
    raml = load_raml("trait-unsupported-type-str.raml")
    with pytest.raises(AssertionError) as e:
        parse(raml)
    msg = "Error parsing trait"
    assert msg == e.value.message


# TODO: move assert from parser_wip to validate_wip
def test_unsupported_trait_type_array_ints():
    raml = load_raml("trait-unsupported-type-array-ints.raml")
    with pytest.raises(errors.InvalidResourceNodeError) as e:
        parse(raml)
    msg = ("'12' needs to be a string referring to a trait, or a dictionary "
           "mapping parameter values to a trait")
    assert msg == e.value.message


def test_too_many_assigned_resource_types():
    raml = load_raml("too-many-assigned-res-types.raml")
    with pytest.raises(errors.InvalidResourceNodeError) as e:
        parse(raml)
    msg = ("Too many resource types applied to '/foobar'.")
    assert msg == e.value.message
