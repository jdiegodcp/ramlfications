# -*- coding: utf-8 -*-
"""
Tests for version-routed validation: RAML 1.0 rules, rejection of
1.0 constructs in 0.8 documents (and vice versa), and located,
collected error reporting.
"""

import os

import pytest

from ramlfications import errors, validate

from tests.base import RAML_10, VALIDATE_08

VALIDATE_10 = os.path.join(RAML_10, "validate")

raises = pytest.raises(errors.InvalidRAMLError)


def load_raml(filename):
    return os.path.join(VALIDATE_10, filename)


def _messages(excinfo):
    return [str(e) for e in excinfo.value.errors]


def test_valid_10_document():
    assert validate(load_raml("valid.raml")) is None


def test_raml10_constructs_rejected_in_08():
    raml = os.path.join(VALIDATE_08, "raml10-constructs.raml")
    with raises as e:
        validate(raml)
    msg = ("The following are RAML 1.0 constructs and are not valid "
           "in a RAML 0.8 document: types, uses.")
    assert msg in _messages(e)


def test_08_schemas_rejected_alongside_types_in_10():
    with raises as e:
        validate(load_raml("schemas-and-types.raml"))
    msg = ("A RAML 1.0 document cannot declare both 'schemas' "
           "(RAML 0.8) and 'types'; declare only 'types'.")
    assert msg in _messages(e)


def test_unresolved_type_reference():
    with raises as e:
        validate(load_raml("unresolved-type.raml"))
    messages = _messages(e)
    assert any("Unresolved data type 'Customer'" in m for m in messages)
    # the error is located: resource, method, body, and source file
    assert any("get /customers" in m for m in messages)
    assert any("response 200 body" in m for m in messages)
    assert any("unresolved-type.raml" in m for m in messages)


def test_annotation_value_must_conform_to_type():
    with raises as e:
        validate(load_raml("annotation-mismatch.raml"))
    messages = _messages(e)
    assert any(
        "Annotation '(rating)'" in m and "'integer'" in m
        for m in messages)
    assert any("get /items" in m for m in messages)


def test_multiple_errors_collected_together():
    with raises as e:
        validate(load_raml("multiple-errors.raml"))
    messages = _messages(e)
    assert len(messages) >= 2
    assert any("Unresolved data type 'Customer'" in m for m in messages)
    assert any("Annotation '(rating)'" in m for m in messages)


def test_error_in_library_identifies_included_file():
    with raises as e:
        validate(load_raml("uses-broken.raml"))
    messages = _messages(e)
    assert any(
        "bad.Broken" in m and "bad_lib.raml" in m for m in messages)
