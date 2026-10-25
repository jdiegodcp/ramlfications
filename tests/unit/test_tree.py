# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

import os

import pytest

from ramlfications import tree, parser
from ramlfications.config import setup_config
from ramlfications.utils import load_file

from tests.base import RAML_08
from tests.data.fixtures import tree_fixtures


@pytest.fixture(scope="session")
def api():
    raml_str = os.path.join(RAML_08, "simple-tree.raml")
    loaded_raml = load_file(raml_str)
    config_file = os.path.join(RAML_08, "test-config.ini")
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


def test_print_tree_light_v(api, capsys):
    expected_result = tree_fixtures.tree_light_v
    print_tree(api, "light", 1)

    out, err = capsys.readouterr()
    assert out == expected_result


def test_print_tree_light_vv(api, capsys):
    expected_result = tree_fixtures.tree_light_vv
    print_tree(api, "light", 2)

    out, err = capsys.readouterr()

    assert out == expected_result


def test_print_tree_light_vvv(api, capsys):
    expected_result = tree_fixtures.tree_light_vvv
    print_tree(api, "light", 3)

    out, err = capsys.readouterr()

    assert out == expected_result


def test_tree_form_params_from_body(api, capsys):
    # formParameters declared under ``body: application/x-www-form-urlencoded``
    # (the only place RAML 0.8 allows them) are listed under the method
    print_tree(api, None, 2)

    out, err = capsys.readouterr()
    lines = out.splitlines()
    put = lines.index("|    ⌙ PUT")
    assert lines[put + 1:] == [
        "|       URI Params",
        "|        ⌙ user_id",
        "|        ⌙ playlist_id",
        "|       Form Params",
        "|        ⌙ name",
    ]


def test_form_params_model_unchanged(api):
    put = [r for r in api.resources if r.method == "put"][0]
    assert put.form_params is None
    assert [p.name for p in put.body[0].form_params] == ["name"]


def test_tree_form_params_deduplicated(tmpdir, capsys):
    # method-level form params first, then each body's, each name once
    raml_file = tmpdir.join("form.raml")
    raml_file.write("""#%RAML 0.8
title: Form params
baseUri: http://localhost
/form:
  post:
    formParameters:
      name:
        type: string
    body:
      application/x-www-form-urlencoded:
        formParameters:
          name:
            type: string
          age:
            type: integer
      multipart/form-data:
        formParameters:
          file:
            type: file
          age:
            type: integer
""")
    config = setup_config(os.path.join(RAML_08, "test-config.ini"))
    api = parser.parse_raml(load_file(str(raml_file)), config)
    print_tree(api, None, 2)

    out, err = capsys.readouterr()
    lines = out.splitlines()
    form = lines.index("|     Form Params")
    assert lines[form + 1:] == [
        "|      ⌙ name",
        "|      ⌙ age",
        "|      ⌙ file",
    ]
