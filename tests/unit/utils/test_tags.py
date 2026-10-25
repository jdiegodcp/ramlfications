# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB


import pytest

from ramlfications.utils import tags


PAIRINGS = [
    ("user", "users"),
    ("track", "tracks"),
    ("space", "spaces"),
    ("bass", "basses"),
    ("goose", "geese"),
    ("foot", "feet"),
    ("ethos", "ethoses")
]


def test_pluralize():
    for p in PAIRINGS:
        exp = p[1]
        ret = tags.pluralize(p[0])
        assert exp == ret


def test_singularize():
    for p in PAIRINGS:
        exp = p[0]
        ret = tags.singularize(p[1])
        assert exp == ret


# words already in the requested form are returned unchanged
KEEP_FORM = PAIRINGS + [
    ("status", "statuses"),
    ("datum", "data"),
    ("news", "news"),
    ("series", "series"),
]


def test_singularize_keeps_singular():
    for singular, _ in KEEP_FORM:
        assert tags.singularize(singular) == singular


def test_pluralize_keeps_plural():
    for _, plural in KEEP_FORM:
        assert tags.pluralize(plural) == plural


@pytest.mark.parametrize("func,value,expected", [
    # the RAML 1.0 specification's examples
    ("uppercase", "userId", "USERID"),
    ("lowercase", "userId", "userid"),
    ("lowercamelcase", "UserId", "userId"),
    ("uppercamelcase", "userId", "UserId"),
    ("lowerunderscorecase", "userId", "user_id"),
    ("upperunderscorecase", "userId", "USER_ID"),
    ("lowerhyphencase", "userId", "user-id"),
    ("upperhyphencase", "userId", "USER-ID"),
    # words split at separators and case changes
    ("lowercamelcase", "user_id", "userId"),
    ("uppercamelcase", "user-id", "UserId"),
    ("lowerunderscorecase", "HTTPServer", "http_server"),
])
def test_case_functions(func, value, expected):
    assert getattr(tags, func)(value) == expected
