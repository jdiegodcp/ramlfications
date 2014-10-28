#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function
from cStringIO import StringIO

import os
import sys

from ramlfications import tree, parser

from .base import BaseTestCase


class TestPrintTree(BaseTestCase):
    def setUp(self):
        self.here = os.path.abspath(os.path.dirname(__file__))
        raml_file = "examples/spotify-web-api-form-params.raml"
        raml_file = os.path.join(self.here, raml_file)
        self.api = parser.APIRoot(raml_file)
        self.held, sys.stdout = sys.stdout, StringIO()

    def test_get_tree(self):
        ttree = tree.get_tree(self.api)
        keys = ['/tracks', '/albums', '/tracks/{id}', '/artists/{id}',
                '/users/{user_id}/playlists/{playlist_id}', '/me',
                '/users/{user_id}/playlists', '/artists/{id}/albums',
                '/me/tracks/contains', '/artists/{id}/top-tracks',
                '/users/{user_id}/playlists/{playlist_id}/tracks',
                '/albums/{id}', '/albums/{id}/tracks', '/users/{user_id}',
                '/search', '/artists', '/me/tracks',
                '/artists/{id}/related-artists']

        self.assertListEqual(ttree.keys(), keys)

        values = ("""[[('GET', < Resource: GET /tracks >)], [('GET', \
< Resource: GET /albums >)], [('GET', < Resource: GET /tracks/{id} >)], \
[('GET', < Resource: GET /artists/{id} >)], [('GET', \
< Resource: GET /users/{user_id}/playlists/{playlist_id} >), \
('PUT', < Resource: PUT /users/{user_id}/playlists/{playlist_id} >)], \
[('GET', < Resource: GET /me >)], [('GET', < Resource: \
GET /users/{user_id}/playlists >), ('POST', < Resource: \
POST /users/{user_id}/playlists >)], [('GET', < Resource: \
GET /artists/{id}/albums >)], [('GET', < Resource: GET \
/me/tracks/contains >)], [('GET', < Resource: GET \
/artists/{id}/top-tracks >)], [('GET', < Resource: \
GET /users/{user_id}/playlists/{playlist_id}/tracks >), \
('POST', < Resource: POST /users/{user_id}/playlists/{playlist_id}/tracks >), \
('PUT', < Resource: PUT /users/{user_id}/playlists/{playlist_id}/tracks >), \
('DELETE', < Resource: DELETE /users/{user_id}/playlists/{playlist_id}/\
tracks >)], [('GET', < Resource: GET /albums/{id} >)], \
[('GET', < Resource: GET /albums/{id}/tracks >)], \
[('GET', < Resource: GET /users/{user_id} >)], \
[('GET', < Resource: GET /search >)], [('GET', < Resource: GET /artists >)], \
[('GET', < Resource: GET /me/tracks >), ('PUT', < Resource: PUT /me/tracks >),\
 ('DELETE', < Resource: DELETE /me/tracks >)], \
[('GET', < Resource: GET /artists/{id}/related-artists >)]]""")
        self.assertEqual(str(ttree.values()), values)

    def test_order_resources(self):
        resources = tree.get_tree(self.api)
        ordered_res = tree.order_resources(resources)

        expected_res = ("""OrderedDict([('/albums', \
[('GET', < Resource: GET /albums >)]), ('/albums/{id}', \
[('GET', < Resource: GET /albums/{id} >)]), \
('/albums/{id}/tracks', [('GET', < Resource: GET /albums/{id}/tracks >)]), \
('/artists', [('GET', < Resource: GET /artists >)]), ('/artists/{id}', \
[('GET', < Resource: GET /artists/{id} >)]), ('/artists/{id}/albums', \
[('GET', < Resource: GET /artists/{id}/albums >)]), \
('/artists/{id}/related-artists', [('GET', < Resource: GET \
/artists/{id}/related-artists >)]), ('/artists/{id}/top-tracks', \
[('GET', < Resource: GET /artists/{id}/top-tracks >)]), \
('/me', [('GET', < Resource: GET /me >)]), \
('/me/tracks', [('GET', < Resource: GET /me/tracks >), \
('PUT', < Resource: PUT /me/tracks >), \
('DELETE', < Resource: DELETE /me/tracks >)]), \
('/me/tracks/contains', [('GET', < Resource: GET /me/tracks/contains >)]), \
('/search', [('GET', < Resource: GET /search >)]), \
('/tracks', [('GET', < Resource: GET /tracks >)]), \
('/tracks/{id}', [('GET', < Resource: GET /tracks/{id} >)]), \
('/users/{user_id}', [('GET', < Resource: GET /users/{user_id} >)]), \
('/users/{user_id}/playlists', \
[('GET', < Resource: GET /users/{user_id}/playlists >), \
('POST', < Resource: POST /users/{user_id}/playlists >)]), \
('/users/{user_id}/playlists/{playlist_id}', \
[('GET', < Resource: GET /users/{user_id}/playlists/{playlist_id} >), \
('PUT', < Resource: PUT /users/{user_id}/playlists/{playlist_id} >)]), \
('/users/{user_id}/playlists/{playlist_id}/tracks', \
[('GET', < Resource: GET /users/{user_id}/playlists/{playlist_id}/tracks >), \
('POST', < Resource: POST /users/{user_id}/playlists/{playlist_id}/tracks >), \
('PUT', < Resource: PUT /users/{user_id}/playlists/{playlist_id}/tracks >), \
('DELETE', < Resource: DELETE /users/{user_id}/playlists/{playlist_id}/tracks \
>)])])""")
        self.assertEqual(str(ordered_res), expected_res)

    def test_pprint_tree_light(self):
        expected_result = ("""\
\033[1;39m===============\033[1;m\n\
\033[1;32mSpotify Web API\033[1;m\n\
\033[1;39m===============\033[1;m\n\
\033[1;32mBase URI: https://api.spotify.com/v1\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /albums\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /albums/{id}\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m    – /albums/{id}/tracks\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /artists\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /artists/{id}\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m    – /artists/{id}/albums\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m    – /artists/{id}/related-artists\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m    – /artists/{id}/top-tracks\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /me\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /me/tracks\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m    – /me/tracks/contains\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /search\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /tracks\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /tracks/{id}\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /users/{user_id}\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /users/{user_id}/playlists\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /users/{user_id}/playlists/{playlist_id}\033\
[1;m\n\
\033[1;39m|\033[1;m\033[1;33m    – /users/{user_id}/playlists/{playlist_id}\
/tracks\033[1;m\n\
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
\033[1;30m|\033[1;m\033[1;36m– /albums\033[1;m\n\
\033[1;30m|\033[1;m\033[1;36m  – /albums/{id}\033[1;m\n\
\033[1;30m|\033[1;m\033[1;36m    – /albums/{id}/tracks\033[1;m\n\
\033[1;30m|\033[1;m\033[1;36m– /artists\033[1;m\n\
\033[1;30m|\033[1;m\033[1;36m  – /artists/{id}\033[1;m\n\
\033[1;30m|\033[1;m\033[1;36m    – /artists/{id}/albums\033[1;m\n\
\033[1;30m|\033[1;m\033[1;36m    – /artists/{id}/related-artists\033[1;m\n\
\033[1;30m|\033[1;m\033[1;36m    – /artists/{id}/top-tracks\033[1;m\n\
\033[1;30m|\033[1;m\033[1;36m– /me\033[1;m\n\
\033[1;30m|\033[1;m\033[1;36m  – /me/tracks\033[1;m\n\
\033[1;30m|\033[1;m\033[1;36m    – /me/tracks/contains\033[1;m\n\
\033[1;30m|\033[1;m\033[1;36m– /search\033[1;m\n\
\033[1;30m|\033[1;m\033[1;36m– /tracks\033[1;m\n\
\033[1;30m|\033[1;m\033[1;36m  – /tracks/{id}\033[1;m\n\
\033[1;30m|\033[1;m\033[1;36m– /users/{user_id}\033[1;m\n\
\033[1;30m|\033[1;m\033[1;36m– /users/{user_id}/playlists\033[1;m\n\
\033[1;30m|\033[1;m\033[1;36m  – /users/{user_id}/playlists/{playlist_id}\
\033[1;m\n\
\033[1;30m|\033[1;m\033[1;36m    – /users/{user_id}/playlists/{playlist_id}\
/tracks\033[1;m\n\
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
\033[1;39m|\033[1;m\033[1;33m– /albums\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /albums/{id}\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m    – /albums/{id}/tracks\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m      ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /artists\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /artists/{id}\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m    – /artists/{id}/albums\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m      ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m    – /artists/{id}/related-artists\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m      ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m    – /artists/{id}/top-tracks\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m      ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /me\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /me/tracks\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ PUT\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ DELETE\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m    – /me/tracks/contains\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m      ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /search\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /tracks\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /tracks/{id}\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /users/{user_id}\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /users/{user_id}/playlists\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ POST\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /users/{user_id}/playlists/{playlist_id}\
\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ PUT\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m    – /users/{user_id}/playlists/{playlist_id}\
/tracks\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m      ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m      ⌙ POST\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m      ⌙ PUT\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m      ⌙ DELETE\033[1;m\n\
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
\033[1;39m|\033[1;m\033[1;33m– /albums\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m     \033[1;31mQuery Params\033[1;m\n\
\033[1;39m|\033[1;m      ⌙ \033[1;31mids\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /albums/{id}\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m       \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31mid\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m    – /albums/{id}/tracks\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m      ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m         \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31mid\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /artists\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m     \033[1;31mQuery Params\033[1;m\n\
\033[1;39m|\033[1;m      ⌙ \033[1;31mids\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /artists/{id}\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m       \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31mid\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m    – /artists/{id}/albums\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m      ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m         \033[1;31mQuery Params\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31mcountry\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31malbum_type\033[1;m\n\
\033[1;39m|\033[1;m         \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31mid\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m    – /artists/{id}/related-artists\
\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m      ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m         \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31mid\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m    – /artists/{id}/top-tracks\
\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m      ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m         \033[1;31mQuery Params\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31mcountry\033[1;m\n\
\033[1;39m|\033[1;m         \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31mid\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /me\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /me/tracks\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ PUT\033[1;m\n\
\033[1;39m|\033[1;m       \033[1;31mQuery Params\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31mids\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ DELETE\033[1;m\n\
\033[1;39m|\033[1;m       \033[1;31mQuery Params\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31mids\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m    – /me/tracks/contains\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m      ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m         \033[1;31mQuery Params\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31mids\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /search\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m     \033[1;31mQuery Params\033[1;m\n\
\033[1;39m|\033[1;m      ⌙ \033[1;31mq\033[1;m\n\
\033[1;39m|\033[1;m      ⌙ \033[1;31mtype\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /tracks\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m     \033[1;31mQuery Params\033[1;m\n\
\033[1;39m|\033[1;m      ⌙ \033[1;31mids\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /tracks/{id}\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m       \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31mid\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /users/{user_id}\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m     \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m      ⌙ \033[1;31muser_id\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /users/{user_id}/playlists\
\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m     \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m      ⌙ \033[1;31muser_id\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ POST\033[1;m\n\
\033[1;39m|\033[1;m     \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m      ⌙ \033[1;31muser_id\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /users/{user_id}/playlists/\
{playlist_id}\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m       \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31muser_id\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31mplaylist_id\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ PUT\033[1;m\n\
\033[1;39m|\033[1;m       \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31muser_id\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31mplaylist_id\033[1;m\n\
\033[1;39m|\033[1;m       \033[1;31mForm Params\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31mname\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31mpublic\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m    – /users/{user_id}/playlists/\
{playlist_id}/tracks\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m      ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m         \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31muser_id\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31mplaylist_id\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m      ⌙ POST\033[1;m\n\
\033[1;39m|\033[1;m         \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31muser_id\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31mplaylist_id\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m      ⌙ PUT\033[1;m\n\
\033[1;39m|\033[1;m         \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31muser_id\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31mplaylist_id\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m      ⌙ DELETE\033[1;m\n\
\033[1;39m|\033[1;m         \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31muser_id\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31mplaylist_id\033[1;m\n\
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
\033[1;39m|\033[1;m\033[1;33m– /albums\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m     \033[1;31mQuery Params\033[1;m\n\
\033[1;39m|\033[1;m      ⌙ \033[1;31mids: Spotify Album IDs\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /albums/{id}\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m       \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31mid: Spotify Album ID\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m    – /albums/{id}/tracks\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m      ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m         \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31mid: Spotify Album ID\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /artists\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m     \033[1;31mQuery Params\033[1;m\n\
\033[1;39m|\033[1;m      ⌙ \033[1;31mids: Spotify Artist IDs\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /artists/{id}\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m       \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31mid: Spotify Artist ID\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m    – /artists/{id}/albums\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m      ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m         \033[1;31mQuery Params\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31mcountry: Country\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31malbum_type: Album Type\033[1;m\n\
\033[1;39m|\033[1;m         \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31mid: Spotify Artist ID\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m    – /artists/{id}/related-artists\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m      ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m         \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31mid: Spotify Artist ID\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m    – /artists/{id}/top-tracks\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m      ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m         \033[1;31mQuery Params\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31mcountry: Country\033[1;m\n\
\033[1;39m|\033[1;m         \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31mid: Spotify Artist ID\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /me\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /me/tracks\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ PUT\033[1;m\n\
\033[1;39m|\033[1;m       \033[1;31mQuery Params\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31mids: Spotify Track IDs\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ DELETE\033[1;m\n\
\033[1;39m|\033[1;m       \033[1;31mQuery Params\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31mids: Spotify Track IDs\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m    – /me/tracks/contains\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m      ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m         \033[1;31mQuery Params\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31mids: Spotify Track IDs\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /search\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m     \033[1;31mQuery Params\033[1;m\n\
\033[1;39m|\033[1;m      ⌙ \033[1;31mq: Query\033[1;m\n\
\033[1;39m|\033[1;m      ⌙ \033[1;31mtype: Item Type\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /tracks\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m     \033[1;31mQuery Params\033[1;m\n\
\033[1;39m|\033[1;m      ⌙ \033[1;31mids: Spotify Track IDs\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /tracks/{id}\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m       \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31mid: Spotify Track ID\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /users/{user_id}\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m     \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m      ⌙ \033[1;31muser_id: User ID\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m– /users/{user_id}/playlists\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m     \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m      ⌙ \033[1;31muser_id: User ID\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m  ⌙ POST\033[1;m\n\
\033[1;39m|\033[1;m     \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m      ⌙ \033[1;31muser_id: User ID\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m  – /users/{user_id}/playlists/{playlist_id}\
\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m       \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31muser_id: User ID\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31mplaylist_id: Playlist ID\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m    ⌙ PUT\033[1;m\n\
\033[1;39m|\033[1;m       \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31muser_id: User ID\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31mplaylist_id: Playlist ID\033[1;m\n\
\033[1;39m|\033[1;m       \033[1;31mForm Params\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31mname: Playlist Name\033[1;m\n\
\033[1;39m|\033[1;m        ⌙ \033[1;31mpublic: Public\033[1;m\n\
\033[1;39m|\033[1;m\033[1;33m    – /users/{user_id}/playlists/{playlist_id}\
/tracks\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m      ⌙ GET\033[1;m\n\
\033[1;39m|\033[1;m         \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31muser_id: User ID\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31mplaylist_id: Playlist ID\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m      ⌙ POST\033[1;m\n\
\033[1;39m|\033[1;m         \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31muser_id: User ID\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31mplaylist_id: Playlist ID\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m      ⌙ PUT\033[1;m\n\
\033[1;39m|\033[1;m         \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31muser_id: User ID\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31mplaylist_id: Playlist ID\033[1;m\n\
\033[1;39m|\033[1;m\033[1;34m      ⌙ DELETE\033[1;m\n\
\033[1;39m|\033[1;m         \033[1;31mURI Params\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31muser_id: User ID\033[1;m\n\
\033[1;39m|\033[1;m          ⌙ \033[1;31mplaylist_id: Playlist ID\033[1;m\n\
""")
        resources = tree.get_tree(self.api)
        ordered_res = tree.order_resources(resources)
        tree.pprint_tree(self.api, ordered_res, 'light', 3)

        self.assertEqual(sys.stdout.getvalue(), expected_result)
