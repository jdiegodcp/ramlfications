#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

import os

from click.testing import CliRunner

from ramlfications import __main__ as main

from .base import BaseTestCase, EXAMPLES, VALIDATE


class TestMain(BaseTestCase):
    def setUp(self):
        self.runner = CliRunner()

    def _checkResult(self, exp_code, exp_msg, result):
        self.assertEqual(result.exit_code, exp_code)
        if exp_msg:
            self.assertEqual(result.output, exp_msg)

    def test_validate(self):
        """
        Successfully validate RAML file via CLI.
        """
        # For each test add a one-liner what you're testing.
        raml_file = os.path.join(EXAMPLES + "spotify-web-api.raml")
        exp_code = 0
        exp_msg = "Success! Valid RAML file: {0}\n".format(raml_file)
        result = self.runner.invoke(main.validate, [raml_file])
        self._checkResult(exp_code, exp_msg, result)

    def test_validate_fail(self):
        """
        Raise error for invalid RAML file via CLI when validating.
        """
        raml_file = os.path.join(VALIDATE + "no-title.raml")
        exp_code = 1
        exp_msg = "Error validating file {0}: {1}\n".format(
            raml_file, 'RAML File does not define an API title.')
        result = self.runner.invoke(main.validate, [raml_file])
        self._checkResult(exp_code, exp_msg, result)

    def test_tree(self):
        """
        Successfully print out tree of RAML file via CLI.
        """
        raml_file = os.path.join(EXAMPLES + "spotify-web-api.raml")
        exp_code = 0
        exp_msg = None
        result = self.runner.invoke(main.tree, [raml_file, "--color=light"])
        self._checkResult(exp_code, exp_msg, result)

    def test_tree_invalid(self):
        """
        Raise error for invalid RAML file via CLI when printing the tree.
        """
        raml_file = os.path.join(VALIDATE + "no-title.raml")
        exp_code = 1
        exp_msg = '"{0}" is not a valid RAML file: {1}\n'.format(
            raml_file, 'RAML File does not define an API title.')
        result = self.runner.invoke(main.tree, [raml_file, "--color=light"])
        self._checkResult(exp_code, exp_msg, result)
