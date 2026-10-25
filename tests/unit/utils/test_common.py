# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB

import pytest

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


@pytest.mark.xfail(strict=True, reason=(
    "PATTERN's `[^\\s|]*` after the parameter name runs to the last `>>`, "
    "so `<<item>>/<<other>>` becomes 'job' instead of 'job/x'"))
def test_substitute_adjacent_placeholders():
    data = {"a": "<<item>>/<<other>>"}
    result = substitute_parameters(data, {"item": "job", "other": "x"})
    assert result == {"a": "job/x"}
