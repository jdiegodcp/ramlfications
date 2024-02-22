# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB
from __future__ import absolute_import, division, print_function


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
