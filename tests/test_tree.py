#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

import os
import sys

from ramlfications._compat import StringIO
from ramlfications import tree, parser, loader

from .base import BaseTestCase


class TestPrintTree(BaseTestCase):
    def setUp(self):
        self.here = os.path.abspath(os.path.dirname(__file__))
        raml_file = "examples/simple-tree.raml"
        raml_file = os.path.join(self.here, raml_file)
        loaded_file = loader.load(raml_file)
        self.api = parser.APIRoot(loaded_file)
        self.held, sys.stdout = sys.stdout, StringIO()

    def test_get_tree(self):
        ttree = tree.get_tree(self.api)
        keys = ['/tracks', '/users/{user_id}/playlists', '/tracks/{id}',
                '/users/{user_id}/playlists/{playlist_id}']

        self.assertListEqual(sorted(ttree.keys()), sorted(keys))

        self.assertEqual(len(ttree.values()), 4)

    def test_order_resources(self):
        resources = tree.get_tree(self.api)
        ordered_res = tree.order_resources(resources)

        expected_res = ("""OrderedDict([('/tracks', \
[('GET', <Resource(name='/tracks')>)]), ('/tracks/{id}', \
[('GET', <Resource(name='/{id}')>)]), \
('/users/{user_id}/playlists', \
[('GET', <Resource(name='/users/{user_id}/playlists')>)]), \
('/users/{user_id}/playlists/{playlist_id}', \
[('PUT', <Resource(name='/{playlist_id}')>)])])\
""")
        self.assertEqual(str(ordered_res), expected_res)

    def test_pprint_tree_light(self):
        expected_result = ("""\
\033[1;39m===============\033[1;m\n\
\033[1;32mSpotify Web API\033[1;m\n\
\033[1;39m===============\033[1;m\n\
\033[1;32mBase URI: https://api.spotify.com/v1\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /tracks\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /tracks/{id}\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /users/{user_id}/playlists\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /users/{user_id}/playlists/{playlist_id}\033\
[1;m\n\
""")
        resources = tree.get_tree(self.api)
        ordered_res = tree.order_resources(resources)
        tree.pprint_tree(self.api, ordered_res, 'light', 0)

        self.assertEqual(sys.stdout.getvalue(), expected_result)

    def test_pprint_tree_dark(self):
        expected_result = ("""\
\033[1;30m===============\033[1;m\n\
\033[1;35mSpotify Web API\033[1;m\n\
\033[1;30m===============\033[1;m\n\
\033[1;35mBase URI: https://api.spotify.com/v1\033[1;m\n\
\033[1;30m|\033[1;m\033[1;36m– /tracks\033[1;m\n\
\033[1;30m|\033[1;m\033[1;36m  – /tracks/{id}\033[1;m\n\
\033[1;30m|\033[1;m\033[1;36m– /users/{user_id}/playlists\033[1;m\n\
\033[1;30m|\033[1;m\033[1;36m  – /users/{user_id}/playlists/{playlist_id}\
\033[1;m\n\
""")
        resources = tree.get_tree(self.api)
        ordered_res = tree.order_resources(resources)
        tree.pprint_tree(self.api, ordered_res, 'dark', 0)

        self.assertEqual(sys.stdout.getvalue(), expected_result)

    def test_pprint_tree_light_v(self):
        expected_result = ("""\
\033[1;39m===============\033[1;m\n\
\033[1;32mSpotify Web API\033[1;m\n\
\033[1;39m===============\033[1;m\n\
\033[1;32mBase URI: https://api.spotify.com/v1\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /tracks\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /tracks/{id}\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /users/{user_id}/playlists\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /users/{user_id}/playlists/{playlist_id}\
\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ PUT\033[1;m\n\
""")
        resources = tree.get_tree(self.api)
        ordered_res = tree.order_resources(resources)
        tree.pprint_tree(self.api, ordered_res, 'light', 1)

        self.assertEqual(sys.stdout.getvalue(), expected_result)

    def test_pprint_tree_light_vv(self):
        expected_result = ("""\
\033[1;39m===============\033[1;m\n\
\033[1;32mSpotify Web API\033[1;m\n\
\033[1;39m===============\033[1;m\n\
\033[1;32mBase URI: https://api.spotify.com/v1\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /tracks\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m     \033[1;31mQuery Params\033[1;m\n\
\033[1;39m|\033[1;m      ⌙ \033[1;31mids\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /tracks/{id}\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m       \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31mid\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /users/{user_id}/playlists\
\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m     \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m      ⌙ \033[1;31muser_id\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /users/{user_id}/playlists/\
{playlist_id}\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ PUT\033[1;m\n\
\033[1;39m|\033[1;m       \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31muser_id\033[1;m\n\
\033[1;39m|\033[1;m       \033[1;31mForm Params\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31mname\033[1;m\n\
""")
        resources = tree.get_tree(self.api)
        ordered_res = tree.order_resources(resources)
        tree.pprint_tree(self.api, ordered_res, 'light', 2)

        self.assertEqual(sys.stdout.getvalue(), expected_result)

    def test_pprint_tree_light_vvv(self):
        expected_result = ("""\
\033[1;39m===============\033[1;m\n\
\033[1;32mSpotify Web API\033[1;m\n\
\033[1;39m===============\033[1;m\n\
\033[1;32mBase URI: https://api.spotify.com/v1\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /tracks\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m     \033[1;31mQuery Params\033[1;m\n\
\033[1;39m|\033[1;m      ⌙ \033[1;31mids: Spotify Track IDs\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /tracks/{id}\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m       \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31mid: Spotify Track ID\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /users/{user_id}/playlists\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m     \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m      ⌙ \033[1;31muser_id: User ID\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /users/{user_id}/playlists/{playlist_id}\
\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ PUT\033[1;m\n\
\033[1;39m|\033[1;m       \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31muser_id: User ID\033[1;m\n\
\033[1;39m|\033[1;m       \033[1;31mForm Params\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31mname: Playlist Name\033[1;m\n\
""")
        resources = tree.get_tree(self.api)
        ordered_res = tree.order_resources(resources)
        tree.pprint_tree(self.api, ordered_res, 'light', 3)

        self.assertEqual(sys.stdout.getvalue(), expected_result)
