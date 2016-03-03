# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

import os
from textwrap import dedent

from click.testing import CliRunner
import pytest

from ramlfications import __main__ as main

from .base import EXAMPLES, VALIDATE


MAIN_USAGE = 'Usage: main [OPTIONS] COMMAND [ARGS]...\n\n'
TREE_USAGE = 'Usage: tree [OPTIONS] RAMLFILE\n\n'
UPDATE_USAGE = 'Usage: update [OPTIONS]\n\n'
VALIDATE_USAGE = 'Usage: validate [OPTIONS] RAMLFILE\n\n'

MAIN_HELP = MAIN_USAGE + """\
  Yet Another RAML Parser

Options:
  -h, --help  Show this message and exit.

Commands:
  tree      Visualize the RAML file as a tree.
  update    Update RAMLfications' supported MIME types...
  validate  Validate a RAML file.
"""

TREE_HELP = TREE_USAGE + """\
  Visualize the RAML file as a tree.

Options:
  -C, --color [dark|light]  Color theme 'light' for dark-screened backgrounds
  -o, --output FILENAME     Save tree output to file
  -v, --verbose             Include methods for each endpoint
  -V, --validate            Validate RAML file
  -c, --config PATH         Additionally supported items beyond RAML spec.
  -h, --help                Show this message and exit.
"""

UPDATE_HELP = UPDATE_USAGE + """\
  Update RAMLfications' supported MIME types from IANA.

Options:
  -h, --help  Show this message and exit.
"""

VALIDATE_HELP = VALIDATE_USAGE + """\
  Validate a RAML file.

Options:
  -c, --config PATH  Additionally supported items beyond RAML spec.
  -h, --help         Show this message and exit.
"""


@pytest.fixture
def runner():
    return CliRunner()


def check_result(exp_code, exp_msg, result):
    assert result.exit_code == exp_code
    if exp_msg:
        assert result.output == exp_msg


def _handles_no_file(runner, usage_prefix, cli):
    """
    Assertion helper: Command complains about a missing file argument.
    """
    result = runner.invoke(cli, [])
    expected = usage_prefix + 'Error: Missing argument "ramlfile".\n'
    check_result(2, expected, result)


def _handles_nonexistent_file(runner, usage_prefix, cli):
    """
    Assertion helper: Command complains about a nonexistent file.
    """
    for args in [['nonexistent'], ['nonexistent', 'extra']]:
        result = runner.invoke(cli, args)
        expected = usage_prefix + (
            'Error: Invalid value for "ramlfile": '
            'Path "nonexistent" does not exist.\n')
        check_result(2, expected, result)


def _handles_file_extra_arg(runner, usage_prefix, cli):
    """
    Assertion helper: Command complains about extraneous file arguments.
    """
    existing_file = os.path.join(EXAMPLES, "complete-valid-example.raml")
    result = runner.invoke(cli, [existing_file, 'extra'])
    expected = usage_prefix + 'Error: Got unexpected extra argument (extra)\n'
    check_result(2, expected, result)


@pytest.mark.parametrize('args', [[], ['-h'], ['--help']])
def test_main_help(runner, args):
    """
    Show the main usage help.
    """
    result = runner.invoke(main.main, args)
    check_result(0, MAIN_HELP, result)


@pytest.mark.parametrize('args', [['-h'], ['--help']])
def test_validate_help(runner, args):
    """
    Show the validate command usage help.
    """
    result = runner.invoke(main.validate, args)
    check_result(0, VALIDATE_HELP, result)


def test_validate_bad_file_handling(runner):
    """
    The validate command handles bad file arguments.
    """
    _handles_no_file(runner, VALIDATE_USAGE, main.validate)
    _handles_nonexistent_file(runner, VALIDATE_USAGE, main.validate)
    _handles_file_extra_arg(runner, VALIDATE_USAGE, main.validate)


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


@pytest.mark.parametrize('args', [['-h'], ['--help']])
def test_tree_help(runner, args):
    """
    Show the tree command usage help.
    """
    result = runner.invoke(main.tree, args)
    check_result(0, TREE_HELP, result)


def test_tree_bad_file_handling(runner):
    """
    The tree command handles bad file arguments.
    """
    _handles_no_file(runner, TREE_USAGE, main.tree)
    _handles_nonexistent_file(runner, TREE_USAGE, main.tree)
    _handles_file_extra_arg(runner, TREE_USAGE, main.tree)


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


@pytest.mark.parametrize('args', [['-h'], ['--help']])
def test_update_help(runner, args):
    """
    Show the update command usage help.
    """
    result = runner.invoke(main.update, args)
    check_result(0, UPDATE_HELP, result)


def test_update_unexpected_arg(runner):
    """
    The update command rejects unexpected extra arguments.
    """
    result = runner.invoke(main.update, ['surprise'])
    expected = UPDATE_USAGE + (
        'Error: Got unexpected extra argument (surprise)\n')
    check_result(2, expected, result)


def test_update(runner, mocker):
    """
    Successfully update supported mime types
    """
    json_file = "ramlfications/data/supported_mime_types.json"
    parent = os.path.dirname(os.path.pardir)
    json_path = os.path.join(parent, json_file)

    start_mtime = os.path.getmtime(json_path)

    # Minimal parseable registry document, with two dummy MIME types
    dummy_xml = dedent("""\
        <?xml version='1.0' encoding='UTF-8'?>
        <registry xmlns="http://www.iana.org/assignments" id="media-types">

          <registry id="examples">
            <title>examples</title>
            <record>
              <name>dummy1</name>
            </record>
            <record>
              <file type="template">examples/dummy2</file>
            </record>
          </registry>

          <registry id="audio"><title>audio</title></registry>
          <registry id="application"><title>application</title></registry>
          <registry id="image"><title>image</title></registry>
          <registry id="message"><title>message</title></registry>
          <registry id="model"><title>model</title></registry>
          <registry id="multipart"><title>multipart</title></registry>
          <registry id="text"><title>text</title></registry>
          <registry id="video"><title>video</title></registry>
        </registry>
    """)

    from ramlfications import utils
    mocker.patch("ramlfications.utils.download_url", return_value=dummy_xml)
    mocker.patch("ramlfications.utils._save_updated_mime_types")

    runner.invoke(main.update, catch_exceptions=False)

    utils.download_url.assert_called_once_with(
        'https://www.iana.org/assignments/media-types/media-types.xml')
    utils._save_updated_mime_types.assert_called_once_with(
        os.path.realpath(json_path),
        ['examples/dummy1', 'examples/dummy2'])

    end_mtime = os.path.getmtime(json_path)

    # sanity check that data was not written to file
    assert start_mtime == end_mtime
