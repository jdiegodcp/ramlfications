#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

import os

from click.testing import CliRunner

from ramlfications import __main__ as main


here = os.path.abspath(os.path.dirname(__file__))


def test_validate():
    raml_file = os.path.join(here, "examples/spotify-web-api.raml")
    runner = CliRunner()
    result = runner.invoke(main.validate, [raml_file])

    assert result.exit_code == 0
    assert result.output == "Success! Valid RAML file: {0}\n".format(raml_file)


def test_validate_fail():
    raml_file = os.path.join(here, "examples/validate/no-title.raml")
    runner = CliRunner()
    result = runner.invoke(main.validate, [raml_file])

    assert result.exit_code == 0
    assert result.output == "Error validating file {0}: {1}\n".format(
        raml_file, 'RAML File does not define an API title.')


def test_tree():
    raml_file = os.path.join(here, "examples/spotify-web-api.raml")
    runner = CliRunner()
    result = runner.invoke(main.tree, [raml_file, "--color=light"])

    assert result.exit_code == 0


def test_tree_invalid():
    raml_file = os.path.join(here, "examples/validate/no-title.raml")
    runner = CliRunner()
    result = runner.invoke(main.tree, [raml_file, "--color=light"])

    assert result.exit_code == 1
    assert result.output == '"{0}" is not a valid RAML File: {1}\n'.format(
        raml_file, 'RAML File does not define an API title.')
