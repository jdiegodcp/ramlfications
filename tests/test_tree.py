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
        raml = loader.RAMLLoader().load(raml_file)
        self.api = parser.APIRoot(raml)
        self.held, sys.stdout = sys.stdout, StringIO()

    def test_get_tree(self):
        ttree = [r.path for r in tree._get_tree(self.api)]
        keys = ['/tracks', '/users/{user_id}/playlists', '/tracks/{id}',
                '/users/{user_id}/playlists/{playlist_id}']

        self.assertListEqual(sorted(ttree), sorted(keys))

        self.assertEqual(len(ttree), 4)

    # def test_order_resources(self):
    #     resources = tree._get_tree(self.api)
    #     ordered_res = tree._order_resources(resources)

    #     expected_res = (
    #         "OrderedDict([(<Resource(method='put', path='/users/{user_id}/"
    #         "playlists/{playlist_id}')>, [('PUT', <Resource(method='put', "
    #         "path='/users/{user_id}/playlists/{playlist_id}')>)]), "
    #         "(<Resource(method='get', path='/tracks/{id}')>, [('GET', "
    #         "<Resource(method='get', path='/tracks/{id}')>)]), "
    #         "(<Resource(method='get', path='/users/{user_id}/playlists')>, "
    #         "[('GET', <Resource(method='get', path='/users/{user_id}/playlists"
    #         "')>)]), (<Resource(method='get', path='/tracks')>, [('GET', "
    #         "<Resource(method='get', path='/tracks')>)])])"
    #     )
    #     self.assertEqual(str(ordered_res), expected_res)

    def pprint_tree(self, expected_result, color, verbosity):
        resources = tree._get_tree(self.api)
        ordered_res = tree._order_resources(resources)
        tree.pprint_tree(self.api, ordered_res, color, verbosity)

        self.assertEqual(sys.stdout.getvalue(), expected_result)

    def test_pprint_tree_no_color(self):
        expected_result = tree_fixtures.tree_no_color
        self.pprint_tree(expected_result, None, 0)

    def test_pprint_tree_light(self):
        expected_result = tree_fixtures.tree_light
        self.pprint_tree(expected_result, 'light', 0)

    def test_pprint_tree_dark(self):
        expected_result = tree_fixtures.tree_dark
        self.pprint_tree(expected_result, 'dark', 0)

    def test_pprint_tree_light_v(self):
        expected_result = tree_fixtures.tree_light_v
        self.pprint_tree(expected_result, 'light', 1)

    def test_pprint_tree_light_vv(self):
        expected_result = tree_fixtures.tree_light_vv
        self.pprint_tree(expected_result, 'light', 2)

    def test_pprint_tree_light_vvv(self):
        expected_result = tree_fixtures.tree_light_vvv
        self.pprint_tree(expected_result, 'light', 3)
