# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB

import pytest

from ramlfications.errors import InvalidRAMLStructureError
from ramlfications.utils.common import (
    merge_dicts, resource_path_name, substitute_parameters
)


def test_merge_dicts_nested():
    child = {"headers": {"X-Own": {"description": "own"}}}
    parent = {"headers": {"X-Own": {"description": "parent",
                                    "required": True},
                          "X-Inherited": {"description": "inherited"}},
              "description": "parent desc"}
    merged = merge_dicts(child, parent)
    assert merged == {
        "headers": {"X-Own": {"description": "own", "required": True},
                    "X-Inherited": {"description": "inherited"}},
        "description": "parent desc",
    }


def test_merge_dicts_inherits_scalar_into_empty_child():
    # e.g. a ``description`` inherited through ``type: <type with type:>``
    assert merge_dicts({}, "text") == "text"


def test_merge_dicts_own_scalar_wins():
    assert merge_dicts("own", "text") == "own"


@pytest.mark.parametrize("path,version,expected", [
    ("/users/{id}", "0.8", "{id}"),
    ("/users/{id}", "1.0", "users"),
    ("/users/{id}/posts", "1.0", "posts"),
    ("/{id}", "1.0", "{id}"),
    ("/root/widget-d", "1.0", "widget-d"),
])
def test_resource_path_name(path, version, expected):
    assert resource_path_name(path, version) == expected


def test_merge_dicts_lists_not_merged():
    # lists (e.g. ``protocols``) behave like scalars: nearest non-empty wins
    assert merge_dicts(["HTTP"], ["HTTPS"]) == ["HTTP"]
    assert merge_dicts([], ["HTTPS"]) == ["HTTPS"]
    assert merge_dicts({"a": 1}, ["HTTPS"]) == {"a": 1}


def test_merge_dicts_empty_parent_keeps_child():
    assert merge_dicts({"a": 1}, {}) == {"a": 1}
    assert merge_dicts("own", None) == "own"


def test_substitute_adjacent_placeholders():
    data = {"a": "<<item>>/<<other>>"}
    result = substitute_parameters(data, {"item": "job", "other": "x"})
    assert result == {"a": "job/x"}


@pytest.mark.parametrize("text,expected", [
    # each placeholder ends at its own ``>>``, whatever is next to it
    ("<<thing>>-<<resourcePathName>>", "gizmo-widgets"),
    ("<<resourcePathName>>/<<thing>>", "widgets/gizmo"),
    ("<<thing>><<resourcePathName>>", "gizmowidgets"),
    ("<<thing | !pluralize>>-<<resourcePathName>>", "gizmos-widgets"),
    ("<< thing >> and <<thing>>", "gizmo and gizmo"),
    # spacing variants inside the brackets
    ("<<thing|!pluralize>>", "gizmos"),
    ("<< thing | !pluralize >>", "gizmos"),
    ("<<thing >>", "gizmo"),
    # a longer name is a different parameter
    ("<<thing-x>>", "<<thing-x>>"),
])
def test_substitute_placeholder_forms(text, expected):
    params = {"thing": "gizmo", "resourcePathName": "widgets"}
    result = substitute_parameters({"a": text}, params)
    assert result == {"a": expected}


RAML10_FUNCTION_LIST = (
    "!singularize, !pluralize, !uppercase, !lowercase, !lowercamelcase, "
    "!uppercamelcase, !lowerunderscorecase, !upperunderscorecase, "
    "!lowerhyphencase, !upperhyphencase"
)


@pytest.mark.parametrize("raml_version,func,msg", [
    ("0.8", "uppercase",
     "'!uppercase' is a RAML 1.0 parameter function and is not valid in a "
     "RAML 0.8 document."),
    ("0.8", "upercase",
     "'!upercase' is not a RAML parameter function. Valid functions: "
     "!singularize, !pluralize."),
    ("1.0", "upercase",
     "'!upercase' is not a RAML parameter function. Valid functions: "
     + RAML10_FUNCTION_LIST + "."),
    # module attributes of ``tags`` are not parameter functions
    ("1.0", "inflect",
     "'!inflect' is not a RAML parameter function. Valid functions: "
     + RAML10_FUNCTION_LIST + "."),
])
def test_substitute_function_errors(raml_version, func, msg):
    data = {"a": "<<thing | !%s>>" % func}
    with pytest.raises(InvalidRAMLStructureError) as e:
        substitute_parameters(data, {"thing": "gizmo"}, raml_version)
    assert str(e.value) == msg


@pytest.mark.parametrize("raml_version,func,expected", [
    ("0.8", "pluralize", "gizmos"),
    ("1.0", "uppercase", "GIZMO"),
    (None, "upperhyphencase", "GIZMO"),
])
def test_substitute_allowed_functions(raml_version, func, expected):
    data = {"a": "<<thing | !%s>>" % func}
    result = substitute_parameters(data, {"thing": "gizmo"}, raml_version)
    assert result == {"a": expected}


# a value given as a YAML number is transformed as text, like a plain
# ``<<thing>>`` placeholder already writes it
@pytest.mark.parametrize("func,value,expected", [
    ("uppercase", 5, "5"),
    ("lowercamelcase", 5, "5"),
    ("singularize", 5, "5"),
    ("uppercase", 2.5, "2.5"),
    ("uppercase", True, "TRUE"),
])
def test_substitute_function_on_non_string_value(func, value, expected):
    data = {"a": "<<thing | !%s>>" % func}
    result = substitute_parameters(data, {"thing": value}, "1.0")
    assert result == {"a": expected}


def test_substitute_pluralize_number_does_not_crash():
    # English has no plural of "5"; inflect's answer ("5S") is not asserted,
    # only that the result is text instead of an exception
    result = substitute_parameters(
        {"a": "<<thing | !pluralize>>"}, {"thing": 5}, "1.0")
    assert isinstance(result["a"], str)


def test_substitute_non_string_value_without_function():
    result = substitute_parameters({"a": "<<thing>>"}, {"thing": 5})
    assert result == {"a": "5"}
