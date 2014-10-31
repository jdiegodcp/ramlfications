#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

import os

from ramlfications import parser, loader, parameters
from ramlfications.parser import parse
from ramlfications.loader import load
from .base import BaseTestCase


class TestAPIRoot(BaseTestCase):
    def setup_parsed_raml(self, ramlfile):
        self.loaded_file = load(ramlfile)
        return parse(self.loaded_file)

    def setUp(self):
        self.here = os.path.abspath(os.path.dirname(__file__))
        raml_file = os.path.join(self.here, "examples/spotify-web-api.raml")
        self.loader = load(raml_file)
        self.api = parse(self.loader)

    def test_parse_function(self):
        result = parse(self.loader)

        self.assertIsInstance(result, parser.APIRoot)

    def test_no_raml_file(self):
        raml_file = '/foo/bar.raml'
        self.assertRaises(loader.RAMLLoaderError,
                          lambda: self.setup_parsed_raml(raml_file))

    def test_resources(self):
        resources = self.api.resources
        self.assertIsInstance(resources, dict)

        for resource in resources.values():
            self.assertIsInstance(resource, parser.Resource)

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
        api = self.setup_parsed_raml(raml_file)

        self.assertRaises(parser.RAMLParserError, lambda: api.base_uri)

    def test_uri_parameters(self):
        data = [{
            "apiPath": {
                "description": "This is the additional path for some api",
                "type": "string",
                "example": "barbaz",
                "displayName": "API Path"}
        }]

        raml_file = os.path.join(self.here,
                                 'examples/base-uri-parameters.raml')
        api = self.setup_parsed_raml(raml_file)
        results = api.uri_parameters

        for i, r in enumerate(results):
            self.assertIsInstance(r, parser.URIParameter)
            self.assertEqual(r.name, list(data[i].keys())[0])
            self.assertEqual(r.description_raw,
                             list(data[i].values())[0].get('description'))
            self.assertEqual(r.type,
                             list(data[i].values())[0].get('type'))
            self.assertEqual(r.example,
                             list(data[i].values())[0].get('example'))
            self.assertEqual(r.display_name,
                             list(data[i].values())[0].get('displayName'))

    def test_uri_parameters_throws_exception(self):
        raml_file = os.path.join(self.here,
                                 "examples/uri-parameters-error.raml")
        api = self.setup_parsed_raml(raml_file)

        self.assertRaises(parser.RAMLParserError, lambda: api.uri_parameters)

    def test_media_type(self):
        media_type = "application/json"
        self.assertEqual(self.api.media_type, media_type)

    def test_resource_types(self):
        resources = ['base', 'item', 'collection']

        results = self.api.resource_types

        for i, resource in enumerate(results):
            self.assertItemInList(resource.name, resources)

    def test_resource_type(self):
        raml_file = os.path.join(self.here, "examples/resource-types.raml")
        api = self.setup_parsed_raml(raml_file)
        results = api.resource_types

        expected_data = {
            'foo': {
                'get': {
                    'description': 'Get some foo'
                },
                'post': {
                    'description': 'Post some foo'
                }
            },
            'base': {
                'get?': {
                    'headers': {
                        'Accept': {
                            'description': "Is used to set specified media "
                                           "type.",
                            'type': 'string'
                        }
                    },
                    'responses': {
                        403: {
                            'description': "API rate limit exceeded. See "
                                           "http://developer.spotify.com/web-"
                                           "api/#rate-limiting for details.\n"
                        }
                    }
                },
                'post?': {
                    'headers': {
                        'Accept': {
                            'description': "Is used to set specified media "
                                           "type.",
                            'type': 'string'
                        }
                    },
                    'responses': {
                        403: {
                            'description': "API rate limit exceeded. See "
                                           "http://developer.spotify.com/web-"
                                           "api/#rate-limiting for details.\n"
                        }
                    }
                }
            },
            'item': {
                'get?': None,
                'type': 'base'
            },
            'collection': {
                'get?': None,
                'type': 'base'
            }
        }

        http_methods = ['get', 'post', 'put', 'patch', 'delete']

        for r in results:
            self.assertDictEqual(r.data, expected_data[r.name])
            self.assertIsNone(r.usage)
            self.assertEqual(r.type, expected_data[r.name].get('type'))
            self.assertIsInstance(r.methods, list)
            self.assertEqual(r.description_raw,
                             expected_data[r.name].get('description'))

            methods = r.methods
            exp_methods = {}

            for m in http_methods:
                if expected_data[r.name].get(m):
                    exp_methods[m] = expected_data[r.name].get(m)
                if expected_data[r.name].get(m + "?"):
                    exp_methods[m + "?"] = expected_data[r.name].get(m + "?")

            if exp_methods:
                for m in methods:
                    self.assertIsInstance(m, parameters.ResourceTypeMethod)
                    assert m.name in exp_methods
                    self.assertEqual(m.data, exp_methods[m.name])
                    optional = "?" in list(exp_methods.keys())[0]
                    self.assertEqual(m.optional, optional)

    def test_documentation(self):
        # TODO: add example that contains multiple examples
        title = "Spotify Web API Docs"
        content_raw = ("Welcome to the _Spotify Web API_ specification. "
                       "For more information about\nhow to use the API, "
                       "check out [developer site]"
                       "(https://developer.spotify.com/web-api/).\n")

        self.assertIsNotNone(self.api.documentation)
        self.assertIsInstance(self.api.documentation[0], parser.Documentation)
        self.assertEqual(self.api.documentation[0].title, title)
        self.assertEqual(self.api.documentation[0].content_raw, content_raw)

    def test_documentation_no_title(self):
        raml = "examples/docs-no-title-parameter.raml"
        raml_file = os.path.join(self.here, raml)
        api = self.setup_parsed_raml(raml_file)

        self.assertRaises(parser.RAMLParserError, lambda: api.documentation)

    def test_security_schemes_oauth2(self):
        raml = "examples/security-scheme.raml"
        raml_file = os.path.join(self.here, raml)
        api = self.setup_parsed_raml(raml_file)

        scheme = "oauth_2_0"
        data = {
            "describedBy": {
                'queryParameters': {
                    'foo': {
                        'description': 'Foo Query Parameter',
                        'example': 'fooooo',
                        'type': 'string'
                    }
                },
                'formParameters': {
                    'blarg': {
                        'description': 'Blarg Form Parameter',
                        'example': 'bllaaaarrgg',
                        'type': 'string'
                    }
                },
                'uriParameters': {
                    'bar': {
                        'description': 'Bar URI Parameter',
                        'example': 'baaaar',
                        'type': 'string'
                    },
                    'baz': {
                        'description': 'Baz URI Parameter',
                        'example': 'baaaaaz',
                        'type': 'string'
                    },
                },
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

        self.assertEqual(api.security_schemes[0].name, scheme)
        self.assertDictEqual(api.security_schemes[0].data, data)
        self.assertEqual(api.security_schemes[0].type, 'OAuth 2.0')
        self.assertEqual(api.security_schemes[0].description_raw,
                         data.get('description'))

        settings = api.security_schemes[0].settings
        self.assertIsInstance(settings, parameters.Oauth2Scheme)
        self.assertEqual(settings.scopes, data['settings']['scopes'])
        self.assertEqual(settings.authorization_uri,
                         data['settings']['authorizationUri'])
        self.assertEqual(settings.access_token_uri,
                         data['settings']['accessTokenUri'])
        self.assertEqual(settings.authorization_grants,
                         data['settings']['authorizationGrants'])

        described_by = api.security_schemes[0].described_by
        expected_described_by_keys = sorted(['headers',
                                            'responses',
                                            'query_parameters',
                                            'uri_parameters',
                                            'form_parameters'])
        self.assertListEqual(sorted(list(described_by.keys())),
                             expected_described_by_keys)
        self.assertIsInstance(described_by['headers'][0], parameters.Header)
        self.assertIsInstance(described_by['responses'][0],
                              parameters.Response)
        self.assertIsInstance(described_by['responses'][1],
                              parameters.Response)
        self.assertIsInstance(described_by['query_parameters'][0],
                              parameters.QueryParameter)
        self.assertIsInstance(described_by['uri_parameters'][0],
                              parameters.URIParameter)
        self.assertIsInstance(described_by['uri_parameters'][1],
                              parameters.URIParameter)
        self.assertIsInstance(described_by['form_parameters'][0],
                              parameters.FormParameter)

        for scheme in api.security_schemes:
            self.assertIsInstance(scheme, parameters.SecurityScheme)

    def test_no_security_schemes(self):
        raml_file = os.path.join(self.here, "examples/no-security-scheme.raml")
        api = self.setup_parsed_raml(raml_file)

        self.assertIsNone(api.security_schemes)

    def test_security_schemes_markdown_desc(self):
        raml = "examples/markdown-desc-docs.raml"
        raml_file = os.path.join(self.here, raml)
        api = self.setup_parsed_raml(raml_file)

        desc_results = api.security_schemes[0].description_html
        expected_results = ("<p>Spotify supports <a href=\"https://developer."
                            "spotify.com/web-api/authorization-guide/\">"
                            "OAuth 2.0</a>\nfor authenticating all API "
                            "requests.</p>\n")
        self.assertEqual(desc_results, expected_results)

    def test_traits(self):
        self.assertIsInstance(self.api.traits, list)
        for trait in self.api.traits:
            self.assertIsInstance(list(trait.values())[0],
                                  parser.QueryParameter)

    def test_security_schemes_oauth1(self):
        scheme_name = "oauth_1_0"
        data = {
            'description': ("OAuth 1.0 continues to be supported for all API "
                            "requests, but OAuth 2.0 is now preferred.\n"),
            'type': 'OAuth 1.0',
            'settings': {
                'requestTokenUri':
                    "https://api.dropbox.com/1/oauth/request_token",
                'authorizationUri':
                    "https://www.dropbox.com/1/oauth/authorize",
                'tokenCredentialsUri':
                    'https://api.dropbox.com/1/oauth/access_token'
            }
        }

        r = 'examples/security-schemes-oauth-1.raml'
        raml_file = os.path.join(self.here, r)
        api = self.setup_parsed_raml(raml_file)

        scheme = api.security_schemes[0]

        self.assertEqual(scheme.name, scheme_name)
        self.assertEqual(scheme.type, data['type'])
        self.assertIsNone(scheme.described_by)
        self.assertEqual(scheme.description_raw, data['description'])
        self.assertEqual(scheme.data, data)

        settings = scheme.settings
        self.assertIsInstance(settings, parameters.Oauth1Scheme)
        self.assertDictEqual(settings.settings, data['settings'])
        self.assertEqual(settings.authorization_uri,
                         data['settings']['authorizationUri'])
        self.assertEqual(settings.request_token_uri,
                         data['settings']['requestTokenUri'])
        self.assertEqual(settings.token_credentials_uri,
                         data['settings']['tokenCredentialsUri'])

    def test_security_schemes_other(self):
        raml = "examples/security-schemes-http-other.raml"
        raml_file = os.path.join(self.here, raml)
        api = self.setup_parsed_raml(raml_file)

        schemes = api.security_schemes

        expected_basic = {
            'description': ("The Foo Web API supports HTTP Basic "
                            "Authentication\n"),
            'type': 'Basic Authentication'
        }
        expected_digest = {
            'description': ("The Foo Web API supports HTTP Digest "
                            "Authentication\n"),
            'type': 'Digest Authentication'
        }
        expected_other = {
            'describedBy': {
                'headers': {
                    'X-Foo-Auth': {
                        'description': ("Foo's super awesome home-grown "
                                        "authentication.  Complete with\nour "
                                        "own home-grown cryptography! /s\n"),
                        'displayName': 'Foo Auth'
                    }
                }
            },
            'description': ("The Foo Web API supports its home-grown "
                            "authentication, Foo Auth\n"),
            'type': 'x-foo-auth'
        }

        self.assertDictEqual(schemes[0].data, expected_basic)
        self.assertDictEqual(schemes[1].data, expected_digest)
        self.assertDictEqual(schemes[2].data, expected_other)

    def test_get_parameters(self):
        raml = "examples/traits-resources-parameters.raml"
        raml_file = os.path.join(self.here, raml)
        api = self.setup_parsed_raml(raml_file)

        params = api.get_parameters()

        expected_data = {
            'resource_types': ['<<resourcePathName>>'],
            'traits': ['<<methodName>>']
        }

        self.assertDictEqual(params, expected_data)

    def test_schemas(self):
        raml_file = os.path.join(self.here, "examples/root-schemas.raml")
        api = self.setup_parsed_raml(raml_file)

        result = api.schemas

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

        included_raml_file = os.path.join(self.here,
                                          "examples/includes/simple.raml")
        api2 = self.setup_parsed_raml(included_raml_file)

        self.assertEqual(result[0], api2.raml)

        expected_data = {
            'CreatePlaylist': {
                'name': 'New Playlist',
                'public': False
            },
            'Playlist': {
                '$schema': 'http://json-schema.org/draft-03/schema',
                'properties': {
                    'api_link': {
                        'description': 'API resource address of the entity.',
                        'type': 'string'
                    },
                    'collaborative': {
                        'description': ("True if the owner allows other users "
                                        "to modify the playlist."),
                        'type': 'boolean'
                    },
                    'description': {
                        'description': 'A description of the playlist.',
                        'type': 'string'
                    },
                    'followers_count': {
                        'description': ("The number of users following the "
                                        "playlist."),
                        'type': 'number'
                    },
                    'id': {
                        'description': 'ID of the playlist.',
                        'type': 'string'
                    },
                    'image': {
                        'description': ("URL of a picture associated with the "
                                        "playlist."),
                        'type': 'string'
                    },
                    'items': {
                        'description': ("Contents of the playlist (an array "
                                        "of Track objects)."),
                        'items': {
                            '$ref': 'Track.json'
                        },
                        'type': 'array'
                    },
                    'link': {
                        'description': 'HTTP link of the entity.',
                        'type': 'string'
                    },
                    'name': {
                        'description': 'Name of the playlist.',
                        'type': 'string'
                    },
                    'owner': {
                        '$ref': 'User.json',
                        'description': 'User who owns the playlist.'
                    },
                    'published': {
                        'description': ("Indicates whether the playlist is "
                                        "publicly discoverable. This does not "
                                        "restrict access for users who already"
                                        " know the playlist's URI."),
                        'type': 'boolean'
                    },
                    'uri': {
                        'description': 'Spotify URI of the entity.',
                        'type': 'string'
                    }
                },
                'type': 'object'
            }
        }
        self.assertDictEqual(result[1], expected_data)


class TestDocumentation(BaseTestCase):
    def setup_parsed_raml(self, ramlfile):
        self.loaded_file = load(ramlfile)
        return parse(self.loaded_file)

    def setUp(self):
        self.here = os.path.abspath(os.path.dirname(__file__))
        raml_file = os.path.join(self.here,
                                 "examples/multiple_documentation.raml")
        self.loader = load(raml_file)
        self.api = parse(self.loader)

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
            self.assertIsInstance(doc, parser.Documentation)

        for i, docs in enumerate(self.api.documentation):
            self.assertEqual(docs.title, titles[i])
            self.assertEqual(docs.content_raw, contents[i])

    def test_docs_markdown(self):
        raml_file = os.path.join(self.here, "examples/markdown-desc-docs.raml")
        api = self.setup_parsed_raml(raml_file)
        documentation = api.documentation[0]

        expected_content = ("Welcome to the _Spotify Web API_ specification. "
                            "For more information about\nhow to use the API, "
                            "check out [developer site]"
                            "(https://developer.spotify.com/web-api/).\n")
        expected_html = ("<p>Welcome to the <em>Spotify Web API</em> "
                         "specification. For more information about\nhow to "
                         "use the API, check out <a href=\"https://developer."
                         "spotify.com/web-api/\">developer site</a>.</p>\n")

        self.assertEqual(documentation.content_raw, expected_content)
        self.assertEqual(documentation.content_html, expected_html)


class TestResource(BaseTestCase):
    def setup_parsed_raml(self, ramlfile):
        self.loaded_file = load(ramlfile)
        return parse(self.loaded_file)

    def setUp(self):
        self.here = os.path.abspath(os.path.dirname(__file__))
        raml_file = os.path.join(self.here, "examples/spotify-web-api.raml")
        self.loader = load(raml_file)
        self.api = parse(self.loader)
        self.resources = self.api.resources

    def test_has_path(self):
        for resource in self.resources.values():
            self.assertIsNotNone(resource.path)

    def test_paths(self):
        raml_file = os.path.join(self.here, "examples/simple.raml")
        api = self.setup_parsed_raml(raml_file)
        resources = api.resources

        expected_paths = ['/tracks', '/search', '/tracks/{id}']

        self.assertEqual(len(resources.values()), len(expected_paths))

        for resource in resources.values():
            self.assertItemInList(resource.path, expected_paths)

    def test_absolute_path(self):
        raml_file = os.path.join(self.here,
                                 "examples/base-uri-parameters.raml")
        api = self.setup_parsed_raml(raml_file)
        resource = api.resources['get-foo']

        expected_path = 'https://{domainName}.github.com/{apiPath}/foo'
        self.assertEqual(resource.absolute_path, expected_path)

    def test_repr(self):
        raml_file = os.path.join(self.here, "examples/simple.raml")
        api = self.setup_parsed_raml(raml_file)
        resources = api.resources

        expected_resources = {
            'get-several-tracks': '< Resource: GET /tracks >',
            'get-search-item': '< Resource: GET /search >',
            'get-track': '< Resource: GET /tracks/{id} >'
        }

        for k, res in list(resources.items()):
            self.assertEqual(repr(res), expected_resources[k])

    def test_has_display_name(self):
        for resource in self.resources.values():
            self.assertIsNotNone(resource.display_name)

    def test_display_name_not_defined(self):
        raml_file = os.path.join(self.here, "examples/no-display-name.raml")
        api = self.setup_parsed_raml(raml_file)
        resource = list(api.resources.values())[0]

        self.assertEqual(resource.display_name, '/tracks')
        self.assertEqual(resource.name, resource.display_name)

    def test_has_description(self):
        for resource in self.resources.values():
            self.assertIsNotNone(resource.description_raw)

    def test_description_markdown(self):
        raml = "examples/markdown-desc-docs.raml"
        raml_file = os.path.join(self.here, raml)
        api = self.setup_parsed_raml(raml_file)
        resource = api.resources.get('get-artist')

        html_result = resource.description_html
        expected_result = ("<p><a href=\"https://developer.spotify.com/web-"
                           "api/get-artist/\">Get an Artist</a></p>\n")

        self.assertEqual(html_result, expected_result)

    def test_method(self):
        raml_file = os.path.join(self.here, "examples/simple.raml")
        api = self.setup_parsed_raml(raml_file)
        resources = api.resources

        methods = ['get', 'post']

        for resource in resources.values():
            self.assertItemInList(resource.method, methods)

    def test_protocols(self):
        raml_file = os.path.join(self.here, "examples/protocols.raml")
        resource = self.setup_parsed_raml(raml_file).resources.get(
            'get-tracks')

        expected_protocols = ['HTTP', 'HTTPS']

        self.assertListEqual(resource.protocols, expected_protocols)

    def test_body(self):
        raml_file = os.path.join(self.here, "examples/simple-body.raml")
        api = self.setup_parsed_raml(raml_file)
        resource = api.resources['post-playlists']

        expected_data = {
            'example': {
                'name': 'foo',
                'public': False
            },
            'schema': {
                'name': 'New Playlist',
                'public': False
            }
        }

        expected_example = {'name': 'foo', 'public': False}

        self.assertIsInstance(resource.body, list)
        self.assertEqual(len(resource.body), 1)
        self.assertEqual(repr(resource.body[0]),
                         '< Request Body: application/json >')
        self.assertDictEqual(resource.body[0].data, expected_data)
        self.assertDictEqual(resource.body[0].example, expected_example)
        self.assertEqual(resource.body[0].mime_type, "application/json")
        self.assertEqual(resource.body[0].name, "application/json")

    def test_responses(self):
        raml_file = os.path.join(self.here, "examples/responses.raml")
        resource = self.setup_parsed_raml(raml_file).resources.get(
            'get-popular-media')

        expected_resp_data = {
            200: {
                'body': {
                    'application/json': {
                        'schema': {
                            'name': 'New Playlist',
                            'public': False
                        }
                    }
                }
            },
            503: {
                'body': {
                    'application/json': {
                        'schema': {'name': 'foo', 'public': False}
                    }
                },
                'description': ("The service is currently unavailable or you "
                                "exceeded the maximum requests\nper hour "
                                "allowed to your application.\n"),
                'headers': {
                    'X-waiting-period': {
                        'description': ("The number of seconds to wait before "
                                        "you can attempt to make a request "
                                        "again.\n"),
                        'example': 34,
                        'maximum': 3600,
                        'minimum': 1,
                        'required': True,
                        'type': 'integer'
                    }
                }
            }
        }

        responses = resource.responses

        for resp in responses:
            self.assertDictEqual(resp.data, expected_resp_data[resp.code])
            self.assertIsInstance(resp, parser.Response)
            self.assertEqual(resp.description_raw,
                             expected_resp_data[resp.code].get('description'))
            self.assertIsInstance(resp.resp_content_types, list)

        exp_headers = expected_resp_data[503]['headers']['X-waiting-period']

        for resp in responses:
            headers = resp.headers
            for h in headers:
                self.assertIsInstance(h, parser.Header)
                self.assertDictEqual(h.data, exp_headers)

    def test_headers(self):
        raml_file = os.path.join(self.here, "examples/headers.raml")
        resources = self.setup_parsed_raml(raml_file).resources

        # only one node
        resource = resources['post-job']
        results = resource.headers

        expected_data = {
            'x-Zencoder-job-metadata-{*}': {
                'description': ("Field names prefixed with x-Zencoder-job-"
                                "metadata- contain user-specified metadata.\n"
                                "The API does not validate or use this data. "
                                "All metadata headers will be stored\nwith the"
                                " job and returned to the client when this "
                                "resource is queried.\n"),
                'displayName': 'Job Metadata'
            },
            'Zencoder-Api-Key': {
                'description': ("The API key for your Zencoder account. You "
                                "can find your API key at\nhttps://app."
                                "zencoder.com/api. You can also regenerate "
                                "your API key on\nthat page.\n"),
                'displayName': 'ZEncoder API Key',
                'example': 'abcdefghijabcdefghijabcdefghij',
                'maxLength': 30,
                'minLength': 30,
                'required': True,
                'type': 'string'
            }
        }

        self.assertIsInstance(results, list)
        for item in results:
            self.assertItemInList(item.item, list(expected_data.keys()))
            self.assertIsInstance(item, parser.Header)
            self.assertDictEqual(item.data, expected_data[item.name])

    def test_data(self):
        raml_file = os.path.join(self.here, "examples/simple.raml")
        api = self.setup_parsed_raml(raml_file)
        resources = api.resources

        expected_data = [
            {
                '/{id}': {
                    'displayName': 'track',
                    'get': {
                        'description': ("[Get a Track](https://developer."
                                        "spotify.com/web-api/get-track/)\n")
                    },
                    'uriParameters': {
                        'id': {
                            'displayName': 'Spotify Track ID',
                            'example': '1zHlj4dQ8ZAtrayhuDDmkY',
                            'type': 'string'
                        }
                    }
                },
                'displayName': 'several-tracks',
                'get': {
                    'description': ("[Get Several Tracks]"
                                    "(https://developer.spotify.com/web-api/"
                                    "get-several-tracks/)\n"),
                    'queryParameters': {
                        'ids': {
                            'description': 'A comma-separated list of IDs',
                            'displayName': 'Spotify Track IDs',
                            'example': ("7ouMYWpwJ422jRcDASZB7P,"
                                        "4VqPOruhp5EdPBeR92t6lQ,"
                                        "2takcwOaAZWiXQijPHIx7B"),
                            'required': True,
                            'type': 'string'
                        }
                    }
                }
            }, {
                'displayName': 'search-item',
                'get': {
                    'description': ("[Search for an Item]"
                                    "(https://developer.spotify.com/web-api/"
                                    "search-item/)\n"),
                    'is': ['paged'],
                    'queryParameters': {
                        'q': {
                            'description': ("The search query's keywords (and "
                                            "optional field filters). The "
                                            "search is not case-sensitive: "
                                            "'roadhouse' will match "
                                            "'Roadhouse', 'roadHouse', etc. "
                                            "Keywords will be matched in any "
                                            "order unless surrounded by quotes"
                                            ", thus q=roadhouse&20blues will "
                                            "match both 'Blues Roadhouse' and "
                                            "'Roadhouse of the Blues'. "
                                            "Quotation marks can be used to "
                                            "limit the match to a phrase: "
                                            "q=roadhouse&20blues will match "
                                            "'My Roadhouse Blues' but not "
                                            "'Roadhouse of the Blues'. By "
                                            "default, results are returned "
                                            "when a match is found in any "
                                            "field of the target object type. "
                                            "Searches can be made more "
                                            "specific by specifying an album, "
                                            "artist or track field filter. For"
                                            " example q=album:gold%20artist:"
                                            "abba&type=album will search for "
                                            "albums with the text 'gold' in "
                                            "the album name and the text "
                                            "'abba' in an artist name. Other "
                                            "possible field filters, depending"
                                            " on object types being searched, "
                                            "include year, genre, upc, and "
                                            "isrc. For example, q=damian%20"
                                            "genre:reggae-pop&type=artist. The"
                                            " asterisk (*) character can, with"
                                            " some limitations, be used as a "
                                            "wildcard (maximum: 2 per query). "
                                            "It will match a variable number "
                                            "of non-white-space characters. It"
                                            " cannot be used in a quoted "
                                            "phrase, in a field filter, or as "
                                            "the first character of the "
                                            "keyword string."),
                            'displayName': 'Query',
                            'example': 'Muse',
                            'required': True,
                            'type': 'string'
                        },
                        'type': {
                            'description': ("A comma-separated list of item "
                                            "types to search across. Search "
                                            "results will include hits from "
                                            "all the specified item types; for"
                                            " example q=name:abacab&type="
                                            "album,track will return both "
                                            "albums and tracks with \"abacab\""
                                            " in their name."),
                            'displayName': 'Item Type',
                            'enum': ['album', 'artist', 'track'],
                            'example': 'artist',
                            'required': True,
                            'type': 'string'
                        }
                    }
                }
            }, {
                'displayName': 'track',
                'get': {
                    'description': ("[Get a Track]"
                                    "(https://developer.spotify.com/web-api/"
                                    "get-track/)\n")
                },
                'uriParameters': {
                    'id': {
                        'displayName': 'Spotify Track ID',
                        'example': '1zHlj4dQ8ZAtrayhuDDmkY',
                        'type': 'string'
                    }
                }
            },
        ]

        for resource in resources.values():
            self.assertItemInList(resource.data, expected_data)

    def test_parent(self):
        raml_file = os.path.join(self.here, "examples/simple.raml")
        api = self.setup_parsed_raml(raml_file)
        resources = api.resources

        expected_parent = '/tracks'

        for resource in resources.values():
            if resource.parent:
                self.assertEqual(resource.parent.name, expected_parent)
            else:
                self.assertEqual(resource.parent, None)

    def test_traits_resources(self):
        raml_file = os.path.join(self.here, "examples/simple-traits.raml")
        api = self.setup_parsed_raml(raml_file)
        resources = api.resources

        for resource in resources.values():
            expected_dict = {'usage': None, 'name': 'collection'}
            self.assertDictEqual(resource.resource_type, expected_dict)
            if resource.method == 'get':
                self.assertEqual(resource.traits, ['paged'])

    def test_secured_by(self):
        raml_file = os.path.join(self.here, "examples/simple-traits.raml")
        api = self.setup_parsed_raml(raml_file)
        resources = api.resources

        for resource in resources.values():
            self.assertIsNotNone(resource.secured_by)
            for s in resource.secured_by:
                self.assertEqual(s['name'], 'oauth_2_0')
                self.assertIsInstance(s['scheme'], parameters.SecurityScheme)
                self.assertEqual(s['type'], 'OAuth 2.0')
                self.assertEqual(s['scopes'], ['playlist-read-private'])
                self.assertEqual(repr(s['scheme']),
                                 '< Security Scheme: OAuth 2.0 >')

    def test_scopes(self):
        raml_file = os.path.join(self.here, "examples/simple-traits.raml")
        api = self.setup_parsed_raml(raml_file)
        resources = api.resources

        scopes = ['playlist-modify-public',
                  'playlist-modify-private',
                  'playlist-read-private']

        for resource in resources.values():
            for s in resource.secured_by:
                self.assertIsNotNone(s['scopes'])

                for scope in s['scopes']:
                    self.assertItemInList(scope, scopes)

    def test_scopes_2(self):
        raml_file = os.path.join(self.here,
                                 "examples/multiple-security-schemes.raml")
        api = self.setup_parsed_raml(raml_file)
        resource = api.resources['get-current-user']

        scopes = ['user-read-private']

        self.assertListEqual(resource.scopes, scopes)

    def test_base_uri_params(self):
        raml_file = os.path.join(self.here,
                                 'examples/base-uri-parameters.raml')
        api = self.setup_parsed_raml(raml_file)

        resources = api.resources

        foo = resources['get-foo']
        foo_results = foo.base_uri_params

        data = [{
            "domainName": {
                "description": "Foo API Subdomain",
                "type": "string",
                "example": "foo-api"
                }
        }]

        for i, r in enumerate(foo_results):
            self.assertItemInList(r.item, list(data[i].keys())[0])
            self.assertIsInstance(r, parser.URIParameter)
            self.assertEqual(r.name, list(data[i].keys())[0])
            self.assertEqual(r.description_raw,
                             list(data[i].values())[0].get('description'))
            self.assertEqual(r.type,
                             list(data[i].values())[0].get('type'))
            self.assertEqual(r.example,
                             list(data[i].values())[0].get('example'))
            self.assertEqual(r.display_name,
                             list(data[i].values())[0].get('displayName'))

        bar = resources['get-bar']
        bar_results = bar.base_uri_params

        for i, r in enumerate(bar_results):
            self.assertIsInstance(r, parser.URIParameter)
            self.assertEqual(r.name, list(data[i].keys())[0])
            self.assertEqual(r.description_raw,
                             list(data[i].values())[0].get('description'))
            self.assertEqual(r.type,
                             list(data[i].values())[0].get('type'))
            self.assertEqual(r.example,
                             list(data[i].values())[0].get('example'))
            self.assertEqual(r.display_name,
                             list(data[i].values())[0].get('displayName'))

    def test_query_params(self):
        raml_file = os.path.join(self.here, "examples/simple.raml")
        api = self.setup_parsed_raml(raml_file)
        resources = api.resources

        search = resources['get-search-item']
        tracks = resources['get-several-tracks']
        track = resources['get-track']

        search_q_params = search.query_params
        tracks_q_params = tracks.query_params
        track_q_params = track.query_params

        self.assertEqual(track_q_params, [])

        expected_search_q_params = ['q', 'type']
        expected_search_data = {
            'q': {
                'description': ("The search query's keywords (and optional "
                                "field filters). The search is not "
                                "case-sensitive: 'roadhouse' will match "
                                "'Roadhouse', 'roadHouse', etc. Keywords will "
                                "be matched in any order unless surrounded by "
                                "quotes, thus q=roadhouse&20blues will match "
                                "both 'Blues Roadhouse' and 'Roadhouse of the "
                                "Blues'. Quotation marks can be used to limit "
                                "the match to a phrase: q=roadhouse&20blues "
                                "will match 'My Roadhouse Blues' but not "
                                "'Roadhouse of the Blues'. By default, results"
                                " are returned when a match is found in any "
                                "field of the target object type. Searches can"
                                " be made more specific by specifying an "
                                "album, artist or track field filter. For "
                                "example q=album:gold%20artist:abba&type=album"
                                " will search for albums with the text 'gold' "
                                "in the album name and the text 'abba' in an "
                                "artist name. Other possible field filters, "
                                "depending on object types being searched, "
                                "include year, genre, upc, and isrc. For "
                                "example, q=damian%20genre:reggae-pop&type="
                                "artist. The asterisk (*) character can, with "
                                "some limitations, be used as a wildcard "
                                "(maximum: 2 per query). It will match a "
                                "variable number of non-white-space characters"
                                ". It cannot be used in a quoted phrase, in a "
                                "field filter, or as the first character of "
                                "the keyword string."),
                'displayName': 'Query',
                'example': 'Muse',
                'required': True,
                'type': 'string'
            },
            'type': {
                'description': ("A comma-separated list of item types to "
                                "search across. Search results will include "
                                "hits from all the specified item types; for "
                                "example q=name:abacab&type=album,track will "
                                "return both albums and tracks with \"abacab\""
                                " in their name."),
                'displayName': 'Item Type',
                'enum': ['album', 'artist', 'track'],
                'example': 'artist',
                'required': True,
                'type': 'string'
            }
        }
        for param in search_q_params:
            self.assertIsInstance(param, parser.QueryParameter)
            self.assertItemInList(param.item, expected_search_q_params)
            self.assertItemInList(param.name, expected_search_q_params)
            self.assertDictEqual(param.data, expected_search_data[param.name])
            self.assertEqual(param.required,
                             expected_search_data[param.name]['required'])
            self.assertEqual(param.example,
                             expected_search_data[param.name]['example'])
            self.assertEqual(param.description_raw,
                             expected_search_data[param.name]['description'])
            self.assertEqual(param.type,
                             expected_search_data[param.name]['type'])
            self.assertEqual(param.display_name,
                             expected_search_data[param.name]['displayName'])
            self.assertEqual(param.enum,
                             expected_search_data[param.name].get('enum'))

        expected_tracks_q_param = 'ids'
        expected_tracks_data = {
            'description': 'A comma-separated list of IDs',
            'displayName': 'Spotify Track IDs',
            'example': ("7ouMYWpwJ422jRcDASZB7P,"
                        "4VqPOruhp5EdPBeR92t6lQ,"
                        "2takcwOaAZWiXQijPHIx7B"),
            'required': True,
            'type': 'string'
        }

        for param in tracks_q_params:
            self.assertIsInstance(param, parser.QueryParameter)
            self.assertEqual(param.name, expected_tracks_q_param)
            self.assertDictEqual(param.data, expected_tracks_data)
            self.assertEqual(param.required, expected_tracks_data['required'])
            self.assertEqual(param.example, expected_tracks_data['example'])
            self.assertEqual(param.description_raw,
                             expected_tracks_data['description'])
            self.assertEqual(param.type, expected_tracks_data['type'])
            self.assertEqual(param.display_name,
                             expected_tracks_data['displayName'])
            self.assertEqual(param.enum,
                             expected_tracks_data.get('enum'))
            self.assertIsNone(param.default)
            self.assertIsNone(param.pattern)
            self.assertIsNone(param.min_length)
            self.assertIsNone(param.max_length)
            self.assertIsNone(param.minimum)
            self.assertIsNone(param.maximum)
            self.assertIsNone(param.repeat)

    def test_uri_params(self):
        raml_file = os.path.join(self.here, "examples/simple.raml")
        api = self.setup_parsed_raml(raml_file)
        resources = api.resources

        search = resources['get-search-item']
        tracks = resources['get-several-tracks']
        track = resources['get-track']

        search_u_params = search.uri_params
        tracks_u_params = tracks.uri_params
        track_u_params = track.uri_params

        self.assertEqual(tracks_u_params, [])
        self.assertEqual(search_u_params, [])

        expected_track_u_param = 'id'
        expected_track_data = {
            'displayName': 'Spotify Track ID',
            'example': '1zHlj4dQ8ZAtrayhuDDmkY',
            'type': 'string',
        }

        for param in track_u_params:
            self.assertIsInstance(param, parser.URIParameter)
            self.assertEqual(param.item, expected_track_u_param)
            self.assertEqual(param.name, expected_track_u_param)
            # assuming all URI params are true
            self.assertEqual(param.required, True)
            self.assertEqual(param.example, expected_track_data['example'])

            self.assertEqual(param.display_name,
                             expected_track_data['displayName'])
            self.assertEqual(param.type, expected_track_data['type'])
            self.assertIsNone(param.description_raw)
            self.assertIsNone(param.enum)

    def test_form_params(self):
        raml_file = os.path.join(self.here, "examples/form-parameters.raml")
        api = self.setup_parsed_raml(raml_file)
        resources = api.resources

        tracks = resources['post-several-tracks']

        form_params = tracks.form_params

        expected_form_data = {
            'ids': {
                "displayName": "Spotify Track IDs",
                "type": "string",
                "description": "A comma-separated list of IDs",
                "required": True,
                "example": ("7ouMYWpwJ422jRcDASZB7P,"
                            "4VqPOruhp5EdPBeR92t6lQ,"
                            "2takcwOaAZWiXQijPHIx7B")
            },
            'fooname': {
                "displayName": "Foo Name",
                "type": "string",
                "description": "A name of foo",
                "required": True,
                "example": "foobar baz"
            }
        }
        expected_form_params = ['ids', 'fooname']

        for param in form_params:
            self.assertIsInstance(param, parser.FormParameter)
            self.assertItemInList(param.item, expected_form_params)
            self.assertItemInList(param.name, expected_form_params)
            self.assertEqual(param.display_name,
                             expected_form_data[param.name]['displayName'])
            self.assertEqual(param.type,
                             expected_form_data[param.name]['type'])
            self.assertEqual(param.description_raw,
                             expected_form_data[param.name]['description'])
            self.assertEqual(param.required,
                             expected_form_data[param.name]['required'])
            self.assertEqual(param.example,
                             expected_form_data[param.name]['example'])
            # should all be none since it's not set in example RAML
            self.assertIsNone(param.default)
            self.assertIsNone(param.enum)
            self.assertIsNone(param.pattern)
            self.assertIsNone(param.min_length)
            self.assertIsNone(param.max_length)
            self.assertIsNone(param.minimum)
            self.assertIsNone(param.maximum)
            self.assertIsNone(param.repeat)

    def test_param_markdown_desc(self):
        raml = "examples/markdown-desc-docs.raml"
        raml_file = os.path.join(self.here, raml)
        api = self.setup_parsed_raml(raml_file)

        resource = api.resources.get('get-artist-top-tracks')
        param = resource.query_params[0]
        html_result = param.description_html
        expected_result = ("<p>The country (<a href=\"http://en.wikipedia.org"
                           "/wiki/ISO_3166-1\">an ISO 3166-1 alpha-2 country "
                           "code</a>)</p>\n")

        self.assertEqual(html_result, expected_result)

    def test_req_content_types(self):
        raml_file = os.path.join(self.here, "examples/req-content-type.raml")
        api = self.setup_parsed_raml(raml_file)
        resources = api.resources

        post_playlist = resources['post-playlists']

        expected_post_playlist_schema = {
            "name": "New Playlist",
            "public": False
        }
        expected_post_playlist_example = {"foo": "bar"}

        expected_content_types = ['application/json',
                                  'application/x-www-form-urlencoded',
                                  'multipart/form-data']

        for c_type in post_playlist.req_content_types:
            self.assertIsInstance(c_type, parser.ContentType)
            self.assertItemInList(c_type.name, expected_content_types)
            if c_type.name is 'application/json':
                self.assertDictEqual(c_type.schema,
                                     expected_post_playlist_schema)
                self.assertDictEqual(c_type.example,
                                     expected_post_playlist_example)
