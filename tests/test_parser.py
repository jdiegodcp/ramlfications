#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

import os
import unittest

from ramlfications import parser


class TestAPIMetadata(unittest.TestCase):
    maxDiff = None

    if not hasattr(unittest.TestCase, 'assertDictEqual'):
        # assertEqual uses for dicts
        def assertDictEqual(self, d1, d2, msg=None):
            for k, v1 in d1.iteritems():
                assert k in d2
                v2 = d2[k]
                self.assertEqual(v1, v2, msg)
            return True

    if not hasattr(unittest.TestCase, 'assertIsNotNone'):
        def assertIsNotNone(self, value, *args):
            self.assertNotEqual(value, None, *args)

    def setUp(self):
        self.here = os.path.abspath(os.path.dirname(__file__))
        raml_file = os.path.join(self.here, "examples/spotify-web-api.raml")
        self.api = parser.APIRoot(raml_file)

    def test_no_raml_file(self):
        raml_file = '/foo/bar.raml'
        self.assertRaises(parser.RAMLParserError,
                          lambda: parser.APIRoot(raml_file))

    def test_nodes(self):
        nodes = self.api.nodes
        assert isinstance(nodes, dict)

        for node in nodes.values():
            assert isinstance(node, parser.Node)

    def test_title(self):
        title = "Spotify Web API"
        self.assertEqual(self.api.title, title)

    def test_protocols(self):
        protocols = ["HTTPS"]
        self.assertEqual(self.api.protocols, protocols)

    def test_base_uri(self):
        base_uri = "https://api.spotify.com/v1"
        self.assertEqual(self.api.base_uri, base_uri)

    def test_base_uri_throws_exception(self):
        raml_file = os.path.join(self.here, "examples/no-version.raml")
        api = parser.APIRoot(raml_file)

        self.assertRaises(parser.RAMLParserError, lambda: api.base_uri)

    def test_media_type(self):
        media_type = "application/json"
        self.assertEqual(self.api.media_type, media_type)

    # def test_resource_types(self):
    #     resources = ['base', 'item', 'collection']

    #     results = self.api.resource_types

    #     for i, resource in enumerate(results):
    #         self.assertEqual(resource.name, resources[i])

    def test_documentation(self):
        # TODO: add example that contains multiple examples
        title = "Spotify Web API Docs"
        content = ("Welcome to the _Spotify Web API_ specification. "
                   "For more information about\nhow to use the API, "
                   "check out [developer site]"
                   "(https://developer.spotify.com/web-api/).\n")

        self.assertIsNotNone(self.api.documentation)
        assert isinstance(self.api.documentation[0], parser.Documentation)
        self.assertEqual(self.api.documentation[0].title, title)
        self.assertEqual(self.api.documentation[0].content, content)

    def test_security_schemes(self):
        scheme = "oauth_2_0"
        data = {
            "describedBy": {
                "headers": {
                    "Authorization": {
                        "description": ("Used to send a valid OAuth 2 access "
                                        "token.\n"),
                        "type": "string"
                    }
                },
                "responses": {
                    401: {
                        "description": ("Bad or expired token. This can happen"
                                        " if the user revoked a token or\nthe "
                                        "access token has expired. You should "
                                        "re-authenticate the user.\n")
                    },
                    403: {
                        "description": ("Bad OAuth request (wrong consumer "
                                        "key, bad nonce, expired\ntimestamp..."
                                        "). Unfortunately, re-authenticating "
                                        "the user won't help here.\n")
                    }
                }
            },
            "description": ("Spotify supports OAuth 2.0 for authenticating all"
                            " API requests.\n"),
            "settings": {
                "accessTokenUri": "https://accounts.spotify.com/api/token",
                "authorizationGrants": ["code", "token"],
                "authorizationUri": "https://accounts.spotify.com/authorize",
                "scopes": ["playlist-read-private",
                           "playlist-modify-public",
                           "playlist-modify-private",
                           "user-library-read",
                           "user-library-modify",
                           "user-read-private",
                           "user-read-email"]
            },
            "type": "OAuth 2.0"
        }
        self.assertEqual(self.api.security_schemes[0].name, scheme)
        self.assertDictEqual(self.api.security_schemes[0].data, data)

        for scheme in self.api.security_schemes:
            assert isinstance(scheme, parser.SecurityScheme)

    # def test_traits(self):
    #     assert isinstance(self.api.traits, list)
    #     for trait in self.api.traits:
    #         assert isinstance(trait.values()[0], parser.QueryParameter)


class TestDocumentation(unittest.TestCase):
    # TODO: add test for markdown parsing
    if not hasattr(unittest.TestCase, 'assertIsNotNone'):
        def assertIsNotNone(self, value, *args):
            self.assertNotEqual(value, None, *args)

    def setUp(self):
        here = os.path.abspath(os.path.dirname(__file__))
        raml_file = os.path.join(here, "examples/multiple_documentation.raml")
        self.api = parser.APIRoot(raml_file)

    def test_docs(self):
        titles = ["Getting Started",
                  "Basics of Authentication",
                  "Rendering Data as Graphs",
                  "Overview"]
        contents = ["Dummy content on getting started",
                    "Dummy content on the basics of authentication",
                    "Dummy content on rendering data as graphs",
                    ("This is the [markdown](http://foo.com) file that gets "
                     "included with tests.")]

        for doc in self.api.documentation:
            assert isinstance(doc, parser.Documentation)

        for i, docs in enumerate(self.api.documentation):
            self.assertEqual(docs.title, titles[i])
            self.assertEqual(docs.content, contents[i])


class TestNode(unittest.TestCase):
    if not hasattr(unittest.TestCase, 'assertIsNotNone'):
        def assertIsNotNone(self, value, *args):
            self.assertNotEqual(value, None, *args)

    def setUp(self):
        self.here = os.path.abspath(os.path.dirname(__file__))
        raml_file = os.path.join(self.here, "examples/spotify-web-api.raml")
        self.api = parser.APIRoot(raml_file)
        self.nodes = self.api.nodes

    def test_has_path(self):
        for node in self.nodes.values():
            self.assertIsNotNone(node.path)

    def test_has_display_name(self):
        for node in self.nodes.values():
            self.assertIsNotNone(node.display_name)

    def test_has_description(self):
        for node in self.nodes.values():
            self.assertIsNotNone(node.description)
