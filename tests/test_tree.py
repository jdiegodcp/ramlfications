#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

import os
import sys

from six import StringIO

from ramlfications import tree, parser, loader

from .base import BaseTestCase, EXAMPLES
from .data.fixtures import tree_fixtures


class TestPrintTree(BaseTestCase):
    def setUp(self):
        raml_file = os.path.join(EXAMPLES, "simple-tree.raml")
        loaded_file = loader.RAMLLoader(raml_file)
        self.api = parser.APIRoot(loaded_file)
        self.held, sys.stdout = sys.stdout, StringIO()

    def test_get_tree(self):
        ttree = tree._get_tree(self.api)
        keys = ['/tracks', '/users/{user_id}/playlists', '/tracks/{id}',
                '/users/{user_id}/playlists/{playlist_id}']

        self.assertListEqual(sorted(ttree.keys()), sorted(keys))

        self.assertEqual(len(ttree.values()), 4)

    def test_order_resources(self):
        resources = tree._get_tree(self.api)
        ordered_res = tree._order_resources(resources)

        expected_res = (
            "OrderedDict([('/tracks', [('GET', <Resource(name='/tracks')"
            ">)]), ('/tracks/{id}', [('GET', <Resource(name='/{id}')>)]), "
            "('/users/{user_id}/playlists', [('GET', <Resource(name="
            "'/users/{user_id}/playlists')>)]), ('/users/{user_id}/playlists/"
            "{playlist_id}', [('PUT', <Resource(name='/{playlist_id}')>)])])")
        self.assertEqual(str(ordered_res), expected_res)

    def test_pprint_tree_light(self):
        expected_result = tree_fixtures.tree_light

        resources = tree._get_tree(self.api)
        ordered_res = tree._order_resources(resources)
        tree.pprint_tree(self.api, ordered_res, 'light', 0)

        self.assertEqual(sys.stdout.getvalue(), expected_result)

    def test_pprint_tree_dark(self):
        expected_result = tree_fixtures.tree_dark

        resources = tree._get_tree(self.api)
        ordered_res = tree._order_resources(resources)
        tree.pprint_tree(self.api, ordered_res, 'dark', 0)

        self.assertEqual(sys.stdout.getvalue(), expected_result)

    def test_pprint_tree_light_v(self):
        expected_result = tree_fixtures.tree_light_v

        resources = tree._get_tree(self.api)
        ordered_res = tree._order_resources(resources)
        tree.pprint_tree(self.api, ordered_res, 'light', 1)

        self.assertEqual(sys.stdout.getvalue(), expected_result)

    def test_pprint_tree_light_vv(self):
        expected_result = tree_fixtures.tree_light_vv

        resources = tree._get_tree(self.api)
        ordered_res = tree._order_resources(resources)
        tree.pprint_tree(self.api, ordered_res, 'light', 2)

        self.assertEqual(sys.stdout.getvalue(), expected_result)

    def test_pprint_tree_light_vvv(self):
        # What does this test cover that the ones above do not?
        # Can you combine all the tests into one that covers 100% of
        # all tree code?
        expected_result = tree_fixtures.tree_light_vvv

        resources = tree._get_tree(self.api)
        ordered_res = tree._order_resources(resources)
        tree.pprint_tree(self.api, ordered_res, 'light', 3)

        self.assertEqual(sys.stdout.getvalue(), expected_result)
