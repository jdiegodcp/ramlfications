# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB
from __future__ import absolute_import, division, print_function

import os

import pytest

from ramlfications import tree, parser
from ramlfications.config import setup_config
from ramlfications.utils import load_file

from .base import EXAMPLES
from .data.fixtures import tree_fixtures


@pytest.fixture(scope="session")
def api():
    raml_str = os.path.join(EXAMPLES, "simple-tree.raml")
    loaded_raml = load_file(raml_str)
    config_file = os.path.join(EXAMPLES + "test-config.ini")
    config = setup_config(config_file)
    return parser.parse_raml(loaded_raml, config)


def print_tree(root, color, verbosity):
    resources = tree._get_tree(root)
    return tree._print_tree(root, resources, color, verbosity)


def test_print_tree_no_color(api, capsys):
    expected_result = tree_fixtures.tree_no_color
    print_tree(api, None, 0)

    out, err = capsys.readouterr()

    assert out == expected_result


def test_print_tree_light(api, capsys):
    expected_result = tree_fixtures.tree_light
    print_tree(api, "light", 0)

    out, err = capsys.readouterr()

    assert out == expected_result


def test_print_tree_dark(api, capsys):
    expected_result = tree_fixtures.tree_dark
    print_tree(api, "dark", 0)

    out, err = capsys.readouterr()

    assert out == expected_result


@pytest.mark.skipif(1 == 1, reason="HALP! I AM COLORBLIND")
def test_print_tree_light_v(api, capsys):
    expected_result = tree_fixtures.tree_light_v
    print_tree(api, "light", 1)

    out, err = capsys.readouterr()
    assert out == expected_result


@pytest.mark.skipif(1 == 1, reason="HALP! I AM COLORBLIND")
def test_print_tree_light_vv(api, capsys):
    expected_result = tree_fixtures.tree_light_vv
    print_tree(api, "light", 2)

    out, err = capsys.readouterr()

    assert out == expected_result


@pytest.mark.skipif(1 == 1, reason="HALP! I AM COLORBLIND")
def test_print_tree_light_vvv(api, capsys):
    expected_result = tree_fixtures.tree_light_vvv
    print_tree(api, "light", 3)

    out, err = capsys.readouterr()

    assert out == expected_result
