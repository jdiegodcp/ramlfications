#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

import os

from ramlfications import utils

from .base import BaseTestCase


class TestEndpointOrder(BaseTestCase):
    def setUp(self):
        self.here = os.path.abspath(os.path.dirname(__file__))
        yaml_file = os.path.join(self.here, "examples/endpoint_order.yaml")
        self.endpoint = utils.EndpointOrder(yaml_file)

    def test_order(self):
        result = self.endpoint.order

        self.assertIsInstance(result, dict)

        expected_results = {
            'Albums': ['get-album', 'get-several-albums', 'get-album-tracks'],
            'Artists': ['get-artist', 'get-several-artists',
                        'get-artist-albums', 'get-artist-top-tracks',
                        'get-artist-related-artists'],
            'Tracks': ['get-track', 'get-several-tracks'],
            'Playlists': ['get-playlists', 'get-playlist',
                          'get-playlist-tracks', 'post-playlists',
                          'post-playlist-tracks', 'delete-playlist-tracks',
                          'put-playlist-tracks', 'put-playlist'],
            'User Profiles': ['get-users-profile', 'get-current-user'],
            'User Library': ['get-current-user-saved-tracks',
                             'get-current-user-contains-saved-tracks',
                             'put-current-user-saved-tracks',
                             'delete-current-user-saved-tracks'],
            'Search': ['get-search-item']
        }

        self.assertDictEqual(result, expected_results)

    def test_groupings(self):
        result = self.endpoint.groupings
        expected_results = ['Albums', 'Artists', 'Tracks', 'Playlists',
                            'User Profiles', 'User Library', 'Search']
        self.assertIsInstance(result, list)
        self.assertListEqual(result, expected_results)

    def test_no_yaml_file(self):
        yaml_file = '/foo/bar.yaml'
        self.assertRaises(utils.EndpointOrderError,
                          lambda: utils.EndpointOrder(yaml_file).order)
