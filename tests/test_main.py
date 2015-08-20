# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

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
    raml_file = os.path.join(EXAMPLES, "complete-valid-example.raml")
    exp_code = 0
    exp_msg = "Success! Valid RAML file: {0}\n".format(raml_file)
    result = runner.invoke(main.validate, [raml_file])
    check_result(exp_code, exp_msg, result)


def test_validate_fail(runner):
    """
    Raise error for invalid RAML file via CLI when validating.
    """
    raml_file = os.path.join(VALIDATE, "no-base-uri-no-title.raml")
    exp_code = 1
    exp_msg_1 = "Error validating file {0}: \n".format(raml_file)
    exp_msg_2 = 'RAML File does not define an API title.'
    exp_msg_3 = 'RAML File does not define the baseUri.'

    result = runner.invoke(main.validate, [raml_file])

    assert result.exit_code == exp_code
    assert exp_msg_1 in result.output
    assert exp_msg_2 in result.output
    assert exp_msg_3 in result.output


def test_tree(runner):
    """
    Successfully print out tree of RAML file via CLI.
    """
    raml_file = os.path.join(EXAMPLES, "complete-valid-example.raml")
    config_file = os.path.join(EXAMPLES, "test-config.ini")
    exp_code = 0
    exp_msg = None
    result = runner.invoke(main.tree, [raml_file, "--color=light",
                           "--config={0}".format(config_file)])
    check_result(exp_code, exp_msg, result)


def test_tree_invalid(runner):
    """
    Raise error for invalid RAML file via CLI when printing the tree.
    """
    raml_file = os.path.join(VALIDATE, "no-title.raml")
    config_file = os.path.join(VALIDATE, "valid-config.ini")
    exp_code = 1
    exp_msg = '"{0}" is not a valid RAML file: \n\t{1}: {2}\n'.format(
        raml_file, 'InvalidRootNodeError',
        'RAML File does not define an API title.')
    result = runner.invoke(main.tree, [raml_file, "--color=light",
                           "--config={0}".format(config_file)])
    check_result(exp_code, exp_msg, result)


def test_update(runner, mocker):
    """
    Successfully update supported mime types
    """
    json_file = "ramlfications/data/supported_mime_types.json"
    parent = os.path.dirname(os.path.pardir)
    json_path = os.path.join(parent, json_file)

    start_mtime = os.path.getmtime(json_path)

    from ramlfications import utils
    mocker.patch("ramlfications.utils.update_mime_types")
    mocker.patch("ramlfications.utils._save_updated_mime_types")

    runner.invoke(main.update)

    utils.update_mime_types.assert_called_once()
    utils._save_updated_mime_types.assert_called_once()

    end_mtime = os.path.getmtime(json_path)

    # sanity check that data was not written to file
    assert start_mtime == end_mtime
