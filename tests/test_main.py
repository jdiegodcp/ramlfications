# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

import os

from click.testing import CliRunner
import pytest

from ramlfications import __main__ as main

from .base import EXAMPLES, VALIDATE


@pytest.fixture
def runner():
    return CliRunner()


def check_result(exp_code, exp_msg, result):
    assert result.exit_code == exp_code
    if exp_msg:
        assert result.output == exp_msg


def test_validate(runner):
    """
    Successfully validate RAML file via CLI.
    """
    raml_file = os.path.join(EXAMPLES + "complete-valid-example.raml")
    exp_code = 0
    exp_msg = "Success! Valid RAML file: {0}\n".format(raml_file)
    result = runner.invoke(main.validate, [raml_file])
    check_result(exp_code, exp_msg, result)


def test_validate_fail(runner):
    """
    Raise error for invalid RAML file via CLI when validating.
    """
    raml_file = os.path.join(VALIDATE + "no-title.raml")
    exp_code = 1
    exp_msg = "Error validating file {0}: {1}\n".format(
        raml_file, 'RAML File does not define an API title.')
    result = runner.invoke(main.validate, [raml_file])
    check_result(exp_code, exp_msg, result)


def test_tree(runner):
    """
    Successfully print out tree of RAML file via CLI.
    """
    raml_file = os.path.join(EXAMPLES + "complete-valid-example.raml")
    config_file = os.path.join(EXAMPLES + "test-config.ini")
    exp_code = 0
    exp_msg = None
    result = runner.invoke(main.tree, [raml_file, "--color=light",
                           "--config={0}".format(config_file)])
    check_result(exp_code, exp_msg, result)


def test_tree_invalid(runner):
    """
    Raise error for invalid RAML file via CLI when printing the tree.
    """
    raml_file = os.path.join(VALIDATE + "no-title.raml")
    exp_code = 1
    exp_msg = '"{0}" is not a valid RAML file: {1}\n'.format(
        raml_file, 'RAML File does not define an API title.')
    result = runner.invoke(main.tree, [raml_file, "--color=light"])
    check_result(exp_code, exp_msg, result)
