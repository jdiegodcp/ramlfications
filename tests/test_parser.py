#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

import os
import markdown2 as markdown

from ramlfications import parser, loader, parameters
from ramlfications import parse
from .base import BaseTestCase, EXAMPLES


class TestAPIRoot(BaseTestCase):
    fixture = 'test_api_root.json'

    def setup_parsed_raml(self, ramlfile):
        return parse(ramlfile)

    def setUp(self):
        self.f = self.fixture_data.get(self.fixture).get  # fixtures setup
        raml_file = os.path.join(EXAMPLES + "spotify-web-api.raml")
        self.api = parse(raml_file)

    def test_parse_function(self):
        self.assertIsInstance(self.api, parser.APIRoot)

    def test_no_raml_file(self):
        raml_file = '/foo/bar.raml'
        self.assertRaises(loader.LoadRamlFileError,
                          lambda: self.setup_parsed_raml(raml_file))

    def test_resources(self):
        resources = self.api.resources
        self.assertIsInstance(resources, dict)

        for resource in resources.values():
            self.assertIsInstance(resource, parser.Resource)

    def test_title(self):
        title = "Spotify Web API Demo"
        self.assertEqual(self.api.title, title)

    def test_protocols(self):
        protocols = ["HTTPS"]
        self.assertEqual(self.api.protocols, protocols)

    def test_base_uri(self):
        base_uri = "https://api.spotify.com/v1"
        self.assertEqual(self.api.base_uri, base_uri)

    def test_base_uri_throws_exception(self):
        raml_file = os.path.join(EXAMPLES + "no-version.raml")
        api = self.setup_parsed_raml(raml_file)

        self.assertRaises(parser.RAMLParserError, lambda: api.base_uri)

    def test_uri_parameters(self):
        data = self.f('test_uri_parameters')
        raml_file = os.path.join(EXAMPLES + 'base-uri-parameters.raml')
        api = self.setup_parsed_raml(raml_file)
        results = api.uri_parameters

        for i, r in enumerate(results):
            self.assertIsInstance(r, parser.URIParameter)
            self.assertEqual(r.name, list(data[i].keys())[0])
            self.assertEqual(r.description.raw,
                             list(data[i].values())[0].get('description'))
            self.assertEqual(repr(r.type), "<String(name='apiPath')>")
            self.assertEqual(r.example,
                             list(data[i].values())[0].get('example'))
            self.assertEqual(r.display_name,
                             list(data[i].values())[0].get('displayName'))

    def test_uri_parameters_throws_exception(self):
        raml_file = os.path.join(EXAMPLES + "uri-parameters-error.raml")
        api = self.setup_parsed_raml(raml_file)

        self.assertRaises(parser.RAMLParserError, lambda: api.uri_parameters)

    def test_no_uri_parameters(self):
        raml_file = os.path.join(EXAMPLES + "simple.raml")
        api = self.setup_parsed_raml(raml_file)

        self.assertIsNone(api.uri_parameters)

    def test_media_type(self):
        media_type = "application/json"
        self.assertEqual(self.api.media_type, media_type)

    def test_resource_types(self):
        resources = ['base', 'item', 'collection']

        results = self.api.resource_types

        for i, resource in enumerate(results):
            self.assertItemInList(resource.name, resources)
            self.assertIsInstance(resource, parameters.ResourceType)
            repr_str = "<ResourceType(name='{0}')>".format(resource.name)
            self.assertEqual(repr(resource), repr_str)
            for m in resource.methods:
                self.assertIsInstance(m, parameters.ResourceTypeMethod)
                repr_str = "<ResourceTypeMethod(name='{0}')>".format(m.name)
                self.assertEqual(repr(m), repr_str)

    def test_resource_type(self):
        raml_file = os.path.join(EXAMPLES + "resource-types.raml")
        api = self.setup_parsed_raml(raml_file)
        results = api.resource_types

        # TODO: figure out how to setup fixtures where keys can be Ints
        # expected_data = self.fixture_data.get(
        #   self.fixtures[0]).get('test_resource_type')

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
            self.assertEqual(r.description.raw,
                             expected_data[r.name].get('description'))
            if r.description.raw:
                self.assertEqual(r.description.html,
                                 markdown.markdown(expected_data[r.name].get(
                                                   'description')))

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

    def test_no_resource_types(self):
        raml_file = os.path.join(EXAMPLES + "simple-no-resource-types.raml")
        api = self.setup_parsed_raml(raml_file)

        self.assertIsNone(api.resource_types)

    def test_documentation(self):
        # TODO: add example that contains multiple examples
        expected_data = self.f('test_documentation')

        self.assertIsNotNone(self.api.documentation)
        self.assertIsInstance(self.api.documentation[0], parser.Documentation)
        self.assertEqual(self.api.documentation[0].title,
                         expected_data.get('title'))
        self.assertEqual(self.api.documentation[0].content.raw,
                         expected_data.get('content'))
        repr_str = "<Documentation(title='{0}')>".format(
            expected_data.get('title'))
        self.assertEqual(repr(self.api.documentation[0]), repr_str)

    def test_documentation_no_title(self):
        raml_file = os.path.join(EXAMPLES + "docs-no-title-parameter.raml")
        api = self.setup_parsed_raml(raml_file)

        self.assertRaises(parser.RAMLParserError, lambda: api.documentation)

    def test_no_docs(self):
        raml_file = os.path.join(EXAMPLES + "simple-no-docs.raml")
        api = self.setup_parsed_raml(raml_file)

        self.assertIsNone(api.documentation)

    def test_security_schemes_oauth2(self):
        raml_file = os.path.join(EXAMPLES + "security-scheme.raml")
        api = self.setup_parsed_raml(raml_file)

        scheme = "oauth_2_0"
        # Can you move all these long data types/strings you use
        # throughout this file into data files in the "examples"
        # directory?
        # This file is way too long.
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
        self.assertEqual(api.security_schemes[0].description.raw,
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
        raml_file = os.path.join(EXAMPLES + "no-security-scheme.raml")
        api = self.setup_parsed_raml(raml_file)

        self.assertIsNone(api.security_schemes)

    def test_security_schemes_markdown_desc(self):
        raml_file = os.path.join(EXAMPLES + "markdown-desc-docs.raml")
        api = self.setup_parsed_raml(raml_file)

        desc_results = api.security_schemes[0].description.html
        expected_results = ("<p>Spotify supports <a href=\"https://developer."
                            "spotify.com/web-api/authorization-guide/\">"
                            "OAuth 2.0</a>\nfor authenticating all API "
                            "requests.</p>\n")
        self.assertEqual(desc_results, expected_results)

    def test_traits(self):
        self.assertIsInstance(self.api.traits, dict)
        for k, v in list(self.api.traits.items()):
            self.assertIsInstance(v, dict)

    def test_security_schemes_oauth1(self):
        scheme_name = "oauth_1_0"
        data = self.f('test_security_schemes_oauth1')

        raml_file = os.path.join(EXAMPLES + 'security-schemes-oauth-1.raml')
        api = self.setup_parsed_raml(raml_file)

        scheme = api.security_schemes[0]

        self.assertEqual(scheme.name, scheme_name)
        self.assertEqual(scheme.type, data['type'])
        self.assertIsNone(scheme.described_by)
        self.assertEqual(scheme.description.raw, data['description'])
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
        raml_file = os.path.join(EXAMPLES + "security-schemes-http-other.raml")
        api = self.setup_parsed_raml(raml_file)

        schemes = api.security_schemes

        data = self.f('test_security_schemes_other')

        expected_basic = data.get('basic')
        expected_digest = data.get('digest')
        expected_other = data.get('other')

        self.assertDictEqual(schemes[0].data, expected_basic)
        self.assertDictEqual(schemes[1].data, expected_digest)
        self.assertDictEqual(schemes[2].data, expected_other)

    def test_get_parameters(self):
        raml = "traits-resources-parameters.raml"
        raml_file = os.path.join(EXAMPLES + raml)
        api = self.setup_parsed_raml(raml_file)

        params = api.get_parameters()

        expected_data = {
            'resource_types': ['<<resourcePathName>>'],
            'traits': ['<<methodName>>']
        }

        self.assertDictEqual(params, expected_data)

    def test_schemas(self):
        raml_file = os.path.join(EXAMPLES + "root-schemas.raml")
        api = self.setup_parsed_raml(raml_file)

        result = api.schemas

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

        included_raml_file = os.path.join(EXAMPLES +
                                          "includes/simple.raml")
        api2 = self.setup_parsed_raml(included_raml_file)

        self.assertEqual(result[0], api2.raml)

        expected_data = self.f('test_schema')

        self.assertDictEqual(result[1], expected_data)
        repr_str = '<APIRoot(raml_file="{0}")>'.format(raml_file)
        self.assertEqual(repr(api), repr_str)


class TestDocumentation(BaseTestCase):
    fixture = 'test_documentation.json'

    def setup_parsed_raml(self, ramlfile):
        return parse(ramlfile)

    def setUp(self):
        self.f = self.fixture_data.get(self.fixture).get  # fixtures setup
        raml_file = os.path.join(EXAMPLES + "multiple_documentation.raml")
        self.api = parse(raml_file)

    def test_docs(self):
        data = self.f('test_docs')
        titles = data.get('titles')
        contents = data.get('contents')

        for doc in self.api.documentation:
            self.assertIsInstance(doc, parser.Documentation)

        for i, docs in enumerate(self.api.documentation):
            self.assertEqual(docs.title, titles[i])
            self.assertEqual(docs.content.raw, contents[i])

    def test_docs_markdown(self):
        raml_file = os.path.join(EXAMPLES + "markdown-desc-docs.raml")
        api = self.setup_parsed_raml(raml_file)
        documentation = api.documentation[0]

        data = self.f('test_docs_markdown')

        expected_content = data.get('content')
        expected_html = data.get('html')

        self.assertEqual(documentation.content.raw, expected_content)
        self.assertEqual(documentation.content.html, expected_html)


class TestResource(BaseTestCase):
    fixture = 'test_resource.json'

    def setup_parsed_raml(self, ramlfile):
        return parse(ramlfile)

    def setUp(self):
        self.f = self.fixture_data.get(self.fixture).get  # fixtures setup
        raml_file = os.path.join(EXAMPLES + "spotify-web-api.raml")
        self.api = parse(raml_file)
        self.resources = self.api.resources

    def test_has_path(self):
        for resource in self.resources.values():
            self.assertIsNotNone(resource.path)

    def test_paths(self):
        raml_file = os.path.join(EXAMPLES + "simple.raml")
        api = self.setup_parsed_raml(raml_file)
        resources = api.resources

        expected_paths = ['/tracks', '/search', '/tracks/{id}']

        self.assertEqual(len(resources.values()), len(expected_paths))

        for resource in resources.values():
            self.assertItemInList(resource.path, expected_paths)

    def test_absolute_path(self):
        raml_file = os.path.join(EXAMPLES + "base-uri-parameters.raml")
        api = self.setup_parsed_raml(raml_file)
        resource = api.resources['get-foo']

        expected_path = 'https://{domainName}.github.com/{apiPath}/foo'
        self.assertEqual(resource.absolute_path, expected_path)

    def test_has_display_name(self):
        for resource in self.resources.values():
            self.assertIsNotNone(resource.display_name)

    def test_display_name_not_defined(self):
        raml_file = os.path.join(EXAMPLES + "no-display-name.raml")
        api = self.setup_parsed_raml(raml_file)
        resource = list(api.resources.values())[0]

        self.assertEqual(resource.display_name, '/tracks')
        self.assertEqual(resource.name, resource.display_name)

    def test_has_description(self):
        for resource in self.resources.values():
            self.assertIsNotNone(resource.description.raw)

    def test_description_markdown(self):
        raml_file = os.path.join(EXAMPLES + "markdown-desc-docs.raml")
        api = self.setup_parsed_raml(raml_file)
        resource = api.resources.get('get-artist')

        html_result = resource.description.html
        expected_result = ("<p><a href=\"https://developer.spotify.com/web-"
                           "api/get-artist/\">Get an Artist</a></p>\n")

        self.assertEqual(html_result, expected_result)

    def test_no_description(self):
        raml_file = os.path.join(EXAMPLES + "resource-no-desc.raml")
        api = self.setup_parsed_raml(raml_file)
        resource = api.resources.get('get-artist')

        raw_desc = resource.description.raw
        html_desc = resource.description.html
        self.assertEqual(raw_desc, None)
        self.assertEqual(html_desc, None)

    def test_method(self):
        raml_file = os.path.join(EXAMPLES + "simple.raml")
        api = self.setup_parsed_raml(raml_file)
        resources = api.resources

        methods = ['get', 'post']

        for resource in resources.values():
            self.assertItemInList(resource.method, methods)

    def test_protocols(self):
        raml_file = os.path.join(EXAMPLES + "protocols.raml")
        resource = self.setup_parsed_raml(raml_file).resources.get(
            'get-tracks')

        expected_protocols = ['HTTP', 'HTTPS']

        self.assertListEqual(resource.protocols, expected_protocols)

    def test_body(self):
        raml_file = os.path.join(EXAMPLES + "simple-body.raml")
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
                         "<Body(name='application/json')>")
        self.assertDictEqual(resource.body[0].data, expected_data)
        self.assertDictEqual(resource.body[0].schema, expected_data['schema'])
        self.assertDictEqual(resource.body[0].example, expected_example)
        self.assertEqual(resource.body[0].mime_type, "application/json")
        self.assertEqual(resource.body[0].name, "application/json")

    def test_responses(self):
        raml_file = os.path.join(EXAMPLES + "responses.raml")
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

        desc_html = ("<p>The service is currently unavailable or you "
                     "exceeded the maximum requests\nper hour "
                     "allowed to your application.</p>\n")

        responses = resource.responses

        for resp in responses:
            self.assertDictEqual(resp.data, expected_resp_data[resp.code])
            self.assertDictEqual(resp.body, expected_resp_data[resp.code].get(
                                 'body'))
            self.assertIsInstance(resp, parser.Response)
            self.assertEqual(repr(resp),
                             "<Response(code='{0}')>".format(resp.code))
            self.assertEqual(resp.description.raw,
                             expected_resp_data[resp.code].get('description'))
            if resp.description.raw:
                self.assertEqual(resp.description.html, desc_html)
            self.assertIsInstance(resp.resp_content_types, list)

        exp_headers = expected_resp_data[503]['headers']['X-waiting-period']

        for resp in responses:
            headers = resp.headers
            for h in headers:
                self.assertIsInstance(h, parser.Header)
                self.assertDictEqual(h.data, exp_headers)

    def test_raises_incorrect_response_code(self):
        raml_file = os.path.join(EXAMPLES + "invalid-resp-code.raml")
        api = self.setup_parsed_raml(raml_file)
        resource = api.resources['get-popular-media']

        self.assertRaises(parser.RAMLParserError, lambda: resource.responses)

    def test_headers(self):
        raml_file = os.path.join(EXAMPLES + "headers.raml")
        resources = self.setup_parsed_raml(raml_file).resources

        # only one node
        resource = resources['post-job']
        results = resource.headers

        expected_data = self.f('test_headers')

        self.assertIsInstance(results, list)
        for item in results:
            self.assertItemInList(item.name, list(expected_data.keys()))
            self.assertIsInstance(item, parser.Header)
            self.assertDictEqual(item.data, expected_data[item.name])

    def test_data(self):
        raml_file = os.path.join(EXAMPLES + "simple.raml")
        api = self.setup_parsed_raml(raml_file)
        resources = api.resources

        expected_data = self.f('test_data')

        for resource in resources.values():
            self.assertItemInList(resource.data, expected_data)

    def test_parent(self):
        raml_file = os.path.join(EXAMPLES + "simple.raml")
        api = self.setup_parsed_raml(raml_file)
        resources = api.resources

        expected_parent = '/tracks'

        for resource in resources.values():
            if resource.parent:
                self.assertEqual(resource.parent.name, expected_parent)
            else:
                self.assertEqual(resource.parent, None)

    def test_traits_resources(self):
        raml_file = os.path.join(EXAMPLES + "simple-traits.raml")
        api = self.setup_parsed_raml(raml_file)
        resources = api.resources

        for resource in resources.values():
            expected_dict = {'usage': None, 'name': 'collection'}
            self.assertDictEqual(resource.resource_type, expected_dict)
            if resource.method == 'get':
                self.assertEqual(resource.traits, ['paged'])

    def test_resource_types_too_many(self):
        raml_file = os.path.join(EXAMPLES + "mapped-types-too-many.raml")
        api = self.setup_parsed_raml(raml_file)
        magazines = api.resources["get-/magazines"]

        self.assertRaises(parser.RAMLParserError,
                          lambda: magazines.resource_type)

    def test_resource_types_invalid_mapped_type(self):
        raml = "mapped-types-incorrect-resource-type.raml"
        raml_file = os.path.join(EXAMPLES + raml)
        api = self.setup_parsed_raml(raml_file)

        magazines = api.resources['get-/magazines']
        books = api.resources['get-/books']

        self.assertRaises(parser.RAMLParserError,
                          lambda: magazines.resource_type)

        self.assertRaises(parser.RAMLParserError,
                          lambda: books.resource_type)

    def test_mapped_traits(self):
        raml_file = os.path.join(EXAMPLES + "mapped-traits-types.raml")
        api = self.setup_parsed_raml(raml_file)

        first = api.resource_types[0]
        second = api.resource_types[1]

        first_expected_name = 'searchableCollection'
        second_expected_name = 'collection'

        first_res = api.resources['get-/books']
        second_res = api.resources['get-/magazines']

        first_expected_data = self.f('test_mapped_traits').get('first')
        second_expected_data = self.f('test_mapped_traits').get('second')

        self.assertEqual(first.name, first_expected_name)
        self.assertEqual(second.name, second_expected_name)

        self.assertDictEqual(first_res.resource_type, first_expected_data)
        self.assertDictEqual(second_res.resource_type, second_expected_data)

    def test_secured_by(self):
        raml_file = os.path.join(EXAMPLES + "simple-traits.raml")
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
                                 "<Security Scheme(name='oauth_2_0')>")

    def test_no_secured_by(self):
        raml_file = os.path.join(EXAMPLES +
                                 "simple-no-secured-by.raml")
        resources = self.setup_parsed_raml(raml_file).resources

        for res in resources.values():
            self.assertIsNone(res.secured_by)

    def test_method_scopes(self):
        raml_file = os.path.join(EXAMPLES + "simple-secured-by-method.raml")
        api = self.setup_parsed_raml(raml_file)
        get_tracks = api.resources['get-several-tracks']
        expected_scopes = ["user-read-email"]

        for s in get_tracks.secured_by:
            self.assertIsNotNone(s['scopes'])

            for scope in s['scopes']:
                self.assertItemInList(scope, expected_scopes)

    def test_scopes(self):
        raml_file = os.path.join(EXAMPLES + "simple-traits.raml")
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
        raml_file = os.path.join(EXAMPLES +
                                 "multiple-security-schemes.raml")
        api = self.setup_parsed_raml(raml_file)
        resource = api.resources['get-current-user']

        scopes = ['user-read-private']

        self.assertListEqual(resource.scopes, scopes)

    def test_base_uri_params(self):
        raml_file = os.path.join(EXAMPLES + 'base-uri-parameters.raml')
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
            self.assertItemInList(r.name, list(data[i].keys())[0])
            self.assertIsInstance(r, parser.URIParameter)
            self.assertEqual(repr(r),
                             "<URIParameter(name='{0}')>".format(r.name))
            self.assertEqual(r.name, list(data[i].keys())[0])
            self.assertEqual(r.description.raw,
                             list(data[i].values())[0].get('description'))
            self.assertEqual(repr(r.type), "<String(name='domainName')>")
            self.assertEqual(r.example,
                             list(data[i].values())[0].get('example'))
            self.assertEqual(r.display_name,
                             list(data[i].values())[0].get('displayName',
                                                           'domainName'))

        bar = resources['get-bar']
        bar_results = bar.base_uri_params

        for i, r in enumerate(bar_results):
            self.assertIsInstance(r, parser.URIParameter)
            self.assertEqual(repr(r),
                             "<URIParameter(name='{0}')>".format(r.name))
            self.assertEqual(r.name, list(data[i].keys())[0])
            self.assertEqual(r.description.raw,
                             list(data[i].values())[0].get('description'))
            self.assertEqual(repr(r.type), "<String(name='domainName')>")
            self.assertEqual(r.example,
                             list(data[i].values())[0].get('example'))
            self.assertEqual(r.display_name,
                             list(data[i].values())[0].get('displayName',
                                                           'domainName'))

    def test_query_params(self):
        raml_file = os.path.join(EXAMPLES + "simple.raml")
        api = self.setup_parsed_raml(raml_file)
        resources = api.resources

        search = resources['get-search-item']
        tracks = resources['get-several-tracks']
        track = resources['get-track']

        search_q_params = search.query_params
        tracks_q_params = tracks.query_params
        track_q_params = track.query_params

        self.assertEqual(track_q_params, None)

        expected_search_q_params = ['q', 'type', 'limit', 'offset']
        expected_search_data = self.f('test_query_params')

        for param in search_q_params:
            self.assertIsInstance(param, parser.QueryParameter)
            self.assertEqual(repr(param),
                             "<QueryParameter(name='{0}')>".format(param.name))
            self.assertItemInList(param.name, expected_search_q_params)
            self.assertDictEqual(param.data, expected_search_data[param.name])
            self.assertEqual(param.required,
                             expected_search_data[param.name]['required'])
            self.assertEqual(param.example,
                             expected_search_data[param.name]['example'])
            self.assertEqual(param.description.raw,
                             expected_search_data[param.name]['description'])
            self.assertEqual(param.display_name,
                             expected_search_data[param.name]['displayName'])

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
            self.assertEqual(repr(param),
                             "<QueryParameter(name='{0}')>".format(param.name))
            self.assertEqual(param.name, expected_tracks_q_param)
            self.assertDictEqual(param.data, expected_tracks_data)
            self.assertEqual(param.required, expected_tracks_data['required'])
            self.assertEqual(param.example, expected_tracks_data['example'])
            self.assertEqual(param.description.raw,
                             expected_tracks_data['description'])
            self.assertEqual(repr(param.type), "<String(name='{0}')>".format(
                             param.name))
            self.assertEqual(param.display_name,
                             expected_tracks_data['displayName'])
            self.assertEqual(param.type.enum,
                             expected_tracks_data.get('enum'))
            self.assertIsNone(param.default)
            self.assertIsNone(param.type.pattern)
            self.assertIsNone(param.type.min_length)
            self.assertIsNone(param.type.max_length)

    def test_uri_params(self):
        raml_file = os.path.join(EXAMPLES + "simple.raml")
        api = self.setup_parsed_raml(raml_file)
        resources = api.resources

        search = resources['get-search-item']
        tracks = resources['get-several-tracks']
        track = resources['get-track']

        search_u_params = search.uri_params
        tracks_u_params = tracks.uri_params
        track_u_params = track.uri_params

        self.assertIsNone(tracks_u_params)
        self.assertIsNone(search_u_params)

        expected_track_u_param = 'id'
        expected_track_data = {
            'displayName': 'Spotify Track ID',
            'example': '1zHlj4dQ8ZAtrayhuDDmkY',
            'type': 'string',
        }

        for param in track_u_params:
            self.assertIsInstance(param, parser.URIParameter)
            self.assertEqual(repr(param), "<URIParameter(name='{0}')>".format(
                             param.name))
            self.assertEqual(param.name, expected_track_u_param)
            # assuming all URI params are true
            self.assertEqual(param.required, True)
            self.assertEqual(param.example, expected_track_data['example'])

            self.assertEqual(param.display_name,
                             expected_track_data['displayName'])
            self.assertEqual(repr(param.type), "<String(name='id')>")
            self.assertIsNone(param.description.raw)

    def test_primative_type_integer(self):
        raml_file = os.path.join(EXAMPLES + "primative-param-types.raml")
        api = self.setup_parsed_raml(raml_file)
        resource = api.resources.get('get-bar')
        param = resource.query_params.pop()

        expected_data = self.f('test_primative_type_integer')

        self.assertEqual(repr(param.type), "<IntegerNumber(name='limit')>")
        self.assertDictEqual(param.data, expected_data)

    def test_form_params(self):
        raml_file = os.path.join(EXAMPLES + "form-parameters.raml")
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
            self.assertEqual(repr(param), "<FormParameter(name='{0}')>".format(
                             param.name))
            self.assertItemInList(param.name, expected_form_params)
            self.assertEqual(param.display_name,
                             expected_form_data[param.name]['displayName'])
            self.assertEqual(repr(param.type), "<String(name='{0}')>".format(
                             param.name))
            self.assertEqual(param.description.raw,
                             expected_form_data[param.name]['description'])
            self.assertEqual(param.required,
                             expected_form_data[param.name]['required'])
            self.assertEqual(param.example,
                             expected_form_data[param.name]['example'])
            # should be none since it's not set in example RAML
            self.assertIsNone(param.default)

    def test_param_markdown_desc(self):
        raml_file = os.path.join(EXAMPLES + "markdown-desc-docs.raml")
        api = self.setup_parsed_raml(raml_file)

        resource = api.resources.get('get-artist-top-tracks')
        param = resource.query_params[0]
        html_result = param.description.html
        expected_result = ("<p>The country (<a href=\"http://en.wikipedia.org"
                           "/wiki/ISO_3166-1\">an ISO 3166-1 alpha-2 country "
                           "code</a>)</p>\n")

        self.assertEqual(html_result, expected_result)

    def test_req_content_types(self):
        raml_file = os.path.join(EXAMPLES + "req-content-type.raml")
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
            self.assertEqual(repr(c_type), "<ContentType(name='{0}')>".format(
                             c_type.name))
            self.assertItemInList(c_type.name, expected_content_types)
            if c_type.name is 'application/json':
                self.assertDictEqual(c_type.schema,
                                     expected_post_playlist_schema)
                self.assertDictEqual(c_type.example,
                                     expected_post_playlist_example)
