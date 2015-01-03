#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

import os
import sys

from six import StringIO

from ramlfications import tree, loader, parser

from .base import BaseTestCase, EXAMPLES
from .data.fixtures import tree_fixtures


class TestPrintTree(BaseTestCase):
    def setUp(self):
        raml_str = os.path.join(EXAMPLES, "simple-tree.raml")
        loaded_raml = loader.RAMLLoader().load(raml_str)
        self.api = parser.parse_raml(loaded_raml, production=True, parse=True)
        self.held, sys.stdout = sys.stdout, StringIO()

    def test_get_tree(self):
        ttree = [r.path for r in tree._get_tree(self.api)]
        keys = ['/tracks', '/users/{user_id}/playlists', '/tracks/{id}',
                '/users/{user_id}/playlists/{playlist_id}']

        self.assertListEqual(sorted(ttree), sorted(keys))

        self.assertEqual(len(ttree), 4)

    def print_tree(self, expected_result, color, verbosity):
        resources = tree._get_tree(self.api)
        ordered_res = tree._order_resources(resources)
        tree._print_tree(self.api, ordered_res, color, verbosity)

        self.assertEqual(sys.stdout.getvalue(), expected_result)

    def test_pprint_tree_no_color(self):
        expected_result = tree_fixtures.tree_no_color
        self.print_tree(expected_result, None, 0)

    def test_pprint_tree_light(self):
        expected_result = tree_fixtures.tree_light
        self.print_tree(expected_result, 'light', 0)

    def test_pprint_tree_dark(self):
        expected_result = tree_fixtures.tree_dark
        self.print_tree(expected_result, 'dark', 0)

    def test_pprint_tree_light_v(self):
        expected_result = tree_fixtures.tree_light_v
        self.print_tree(expected_result, 'light', 1)

    def test_pprint_tree_light_vv(self):
        expected_result = tree_fixtures.tree_light_vv
        self.print_tree(expected_result, 'light', 2)

    def test_pprint_tree_light_vvv(self):
        expected_result = tree_fixtures.tree_light_vvv
        self.print_tree(expected_result, 'light', 3)
