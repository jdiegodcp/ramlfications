#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

import os
import unittest

import markdown2 as markdown

from ramlfications import raml, parameters
from ramlfications import parse
from .base import BaseTestCase, EXAMPLES


class TestAPIRoot(BaseTestCase):
    fixture = 'test_api_root.json'

    def parse(self, ramlfile):
        return parse(ramlfile)

    def setUp(self):
        self.f = self.fixture_data.get(self.fixture).get  # fixtures setup
        raml_file = os.path.join(EXAMPLES + "spotify-web-api.raml")
        self.api = parse(raml_file)

    def test_raml_root(self):
        self.assertIsInstance(self.api, raml.RAMLRoot)

    def test_title(self):
        title = "Spotify Web API Demo"
        self.assertEqual(self.api.title, title)

    def test_version(self):
        version = 'v1'
        self.assertEqual(self.api.version, version)

    def test_protocols(self):
        protocols = ["HTTPS"]
        self.assertEqual(self.api.protocols, protocols)

    def test_base_uri(self):
        base_uri = "https://api.spotify.com/v1"
        self.assertEqual(self.api.base_uri, base_uri)

    def test_base_uri_params(self):
        data = self.f('test_base_uri_parameters')
        raml_file = os.path.join(EXAMPLES, "base-uri-parameters.raml")
        api = self.parse(raml_file)

        results = api.base_uri_params

        for i, r in enumerate(results):
            self.assertIsInstance(r, parameters.URIParameter)
            self.assertEqual(r.name, list(data[i].keys())[0])
            self.assertEqual(r.description.raw,
                             list(data[i].values())[0].get('description'))
            self.assertEqual(repr(r.type), "<String(name='domainName')>")
            self.assertEqual(r.example,
                             list(data[i].values())[0].get('example'))
            self.assertEqual(r.display_name,
                             list(data[i].values())[0].get('displayName'))
            self.assertEqual(r.default,
                             list(data[i].values())[0].get('default'))

    def test_no_uri_parameters(self):
        raml_file = os.path.join(EXAMPLES + "simple.raml")
        api = self.parse(raml_file)

        self.assertIsNone(api.uri_params)

    def test_uri_parameters(self):
        data = self.f('test_uri_parameters')
        raml_file = os.path.join(EXAMPLES + 'base-uri-parameters.raml')
        api = self.parse(raml_file)
        results = api.uri_params

        for i, r in enumerate(results):
            self.assertIsInstance(r, parameters.URIParameter)
            self.assertEqual(r.name, list(data[i].keys())[0])
            self.assertEqual(r.description.raw,
                             list(data[i].values())[0].get('description'))
            self.assertEqual(repr(r.type), "<String(name='apiPath')>")
            self.assertEqual(r.example,
                             list(data[i].values())[0].get('example'))
            self.assertEqual(r.display_name,
                             list(data[i].values())[0].get('displayName'))

    def test_media_type(self):
        media_type = "application/json"
        self.assertEqual(self.api.media_type, media_type)

    def test_has_resource_types(self):
        resources = ['base', 'item', 'collection']

        results = self.api.resource_types

        for i, resource in enumerate(results):
            self.assertItemInList(resource.name, resources)
            self.assertIsInstance(resource, raml.ResourceType)
            repr_str = "<ResourceType(method='{0}', name='{1}')>".format(
                resource.method.upper(), resource.name)
            self.assertEqual(repr(resource), repr_str)

    def test_no_resource_types(self):
        raml_file = os.path.join(EXAMPLES + "simple-no-resource-types.raml")
        api = self.parse(raml_file)

        self.assertIsNone(api.resource_types)

    def test_has_resources(self):
        resources = self.api.resources
        self.assertIsInstance(resources, list)

        for resource in resources:
            self.assertIsInstance(resource, raml.Resource)

    def test_documentation(self):
        # TODO: add example that contains multiple examples
        expected_data = self.f('test_documentation')

        self.assertIsNotNone(self.api.documentation)
        self.assertIsInstance(self.api.documentation[0],
                              parameters.Documentation)
        self.assertEqual(self.api.documentation[0].title,
                         expected_data.get('title'))
        self.assertEqual(self.api.documentation[0].content.raw,
                         expected_data.get('content'))
        repr_str = "<Documentation(title='{0}')>".format(
            expected_data.get('title'))
        self.assertEqual(repr(self.api.documentation[0]), repr_str)

    def test_no_docs(self):
        raml_file = os.path.join(EXAMPLES + "simple-no-docs.raml")
        api = self.parse(raml_file)

        self.assertIsNone(api.documentation)

    def test_no_security_schemes(self):
        raml_file = os.path.join(EXAMPLES + "no-security-scheme.raml")
        api = self.parse(raml_file)

        self.assertIsNone(api.security_schemes)

    def test_has_traits(self):
        self.assertIsInstance(self.api.traits, list)
        for t in self.api.traits:
            self.assertIsInstance(t, raml.Trait)

    # TODO: break up/clean up
    def test_schemas(self):
        raml_file = os.path.join(EXAMPLES + "root-schemas.raml")
        api = self.parse(raml_file)

        result = api.schemas

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

        included_raml_file = os.path.join(EXAMPLES +
                                          "includes/simple.raml")
        api2 = self.parse(included_raml_file)

        self.assertEqual(result[0], api2.raml)

        expected_data = self.f('test_schema')

        self.assertDictEqual(result[1], expected_data)
        repr_str = '<RAMLRoot(raml_file="{0}")>'.format(raml_file)
        self.assertEqual(repr(api), repr_str)


class TestResourceType(BaseTestCase):
    def setUp(self):
        #self.f = self.fixture_data.get(self.fixture).get  # fixtures setup
        raml_file = os.path.join(EXAMPLES + "spotify-web-api.raml")
        self.api = parse(raml_file)

    def parse(self, ramlfile):
        return parse(ramlfile)

    # TODO: clean up/break up
    def test_resource_type(self):
        raml_file = os.path.join(EXAMPLES + "resource-types.raml")
        api = self.parse(raml_file)
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
                'type': 'base'
            },
            'collection': {
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
                'type': 'base'
            }
        }

        http_methods = [
            'get', 'post', 'put', 'patch', 'delete', 'options',
            'trace', 'head', 'connect'
        ]

        for r in results:
            if r.optional:
                method = r.method + "?"
            else:
                method = r.method
            self.assertIsNone(r.usage)
            self.assertEqual(r.type, expected_data[r.name].get('type'))
            self.assertIsInstance(r.method, str)
            self.assertTrue(r.method in http_methods)
            if r.description:
                self.assertEqual(r.description.raw, expected_data.get(
                    r.name).get(method).get('description'))
            if r.description:
                self.assertEqual(r.description.html,
                                 markdown.markdown(expected_data.get(r.name)
                                                   .get(method)
                                                   .get('description')))


class TestSecurityScheme(BaseTestCase):
    fixture = "test_api_root.json"

    def setUp(self):
        self.f = self.fixture_data.get(self.fixture).get  # fixtures setup
        raml_file = os.path.join(EXAMPLES + "spotify-web-api.raml")
        self.api = parse(raml_file)

    def parse(self, ramlfile):
        return parse(ramlfile)

    # TODO: clean up/break up
    def test_security_schemes_oauth2(self):
        raml_file = os.path.join(EXAMPLES + "security-scheme.raml")
        api = self.parse(raml_file)

        scheme_name = "oauth_2_0"
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

        scheme = api.security_schemes[0]
        self.assertEqual(scheme.name, scheme_name)
        self.assertDictEqual(scheme.data, data)
        self.assertEqual(scheme.type, 'OAuth 2.0')
        self.assertEqual(scheme.description.raw,
                         data.get('description'))

        self.assertEqual(scheme.scopes, data['settings']['scopes'])
        self.assertEqual(scheme.authorization_uri,
                         data['settings']['authorizationUri'])
        self.assertEqual(scheme.access_token_uri,
                         data['settings']['accessTokenUri'])
        self.assertEqual(scheme.authorization_grants,
                         data['settings']['authorizationGrants'])

        described_by = scheme.described_by

        self.assertIsInstance(described_by, list)
        self.assertObjInList(parameters.Header, described_by)
        self.assertObjInList(parameters.Response, described_by)
        self.assertObjInList(parameters.QueryParameter, described_by)
        self.assertObjInList(parameters.URIParameter, described_by)
        self.assertObjInList(parameters.FormParameter, described_by)

        for scheme in api.security_schemes:
            self.assertIsInstance(scheme, parameters.SecurityScheme)

    def test_security_schemes_markdown_desc(self):
        raml_file = os.path.join(EXAMPLES + "markdown-desc-docs.raml")
        api = self.parse(raml_file)

        desc_results = api.security_schemes[0].description.html
        expected_results = ("<p>Spotify supports <a href=\"https://developer."
                            "spotify.com/web-api/authorization-guide/\">"
                            "OAuth 2.0</a>\nfor authenticating all API "
                            "requests.</p>\n")
        self.assertEqual(desc_results, expected_results)

    def test_security_schemes_oauth1(self):
        scheme_name = "oauth_1_0"
        data = self.f('test_security_schemes_oauth1')

        raml_file = os.path.join(EXAMPLES + 'security-schemes-oauth-1.raml')
        api = self.parse(raml_file)

        scheme = api.security_schemes[0]

        self.assertEqual(scheme.name, scheme_name)
        self.assertEqual(scheme.type, data['type'])
        self.assertIsNone(scheme.described_by)
        self.assertEqual(scheme.description.raw, data['description'])
        self.assertEqual(scheme.data, data)

        self.assertEqual(scheme.authorization_uri,
                         data['settings']['authorizationUri'])
        self.assertEqual(scheme.request_token_uri,
                         data['settings']['requestTokenUri'])
        self.assertEqual(scheme.token_credentials_uri,
                         data['settings']['tokenCredentialsUri'])

    def test_security_schemes_other(self):
        raml_file = os.path.join(EXAMPLES + "security-schemes-http-other.raml")
        api = self.parse(raml_file)

        schemes = api.security_schemes

        data = self.f('test_security_schemes_other')

        expected_basic = data.get('basic')
        expected_digest = data.get('digest')
        expected_other = data.get('other')

        self.assertDictEqual(schemes[0].data, expected_basic)
        self.assertDictEqual(schemes[1].data, expected_digest)
        self.assertDictEqual(schemes[2].data, expected_other)


class TestDocumentation(BaseTestCase):
    fixture = 'test_documentation.json'

    def parse(self, ramlfile):
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
            self.assertIsInstance(doc, parameters.Documentation)

        for i, docs in enumerate(self.api.documentation):
            self.assertEqual(docs.title, titles[i])
            self.assertEqual(docs.content.raw, contents[i])

    def test_docs_markdown(self):
        raml_file = os.path.join(EXAMPLES + "markdown-desc-docs.raml")
        api = self.parse(raml_file)
        documentation = api.documentation[0]

        data = self.f('test_docs_markdown')

        expected_content = data.get('content')
        expected_html = data.get('html')

        self.assertEqual(documentation.content.raw, expected_content)
        self.assertEqual(documentation.content.html, expected_html)


class TestTrait(BaseTestCase):

    def parse(self, ramlfile):
        return parse(ramlfile)

    def setup(self):
        raml_file = os.path.join(EXAMPLES, "spotify-web-api.raml")
        self.api = parse(raml_file)
        self.resources = self.api.resources

    def test_trait_instance(self):
        raml_file = os.path.join(EXAMPLES, "simple-traits.raml")
        api = self.parse(raml_file)
        traits = api.traits

        for t in traits:
            self.assertIsInstance(t, raml.Trait)

    def test_trait_usage(self):
        raml_file = os.path.join(EXAMPLES, "trait-usage.raml")
        api = self.parse(raml_file)
        trait = api.traits[0]

        exp_usage = "Apply this trait to any method that supports pagination"

        self.assertEqual(trait.usage, exp_usage)


class TestResource(BaseTestCase):
    fixture = 'test_resource.json'

    def parse(self, ramlfile):
        api = parse(ramlfile)
        return api

    def setUp(self):
        self.f = self.fixture_data.get(self.fixture).get  # fixtures setup
        raml_file = os.path.join(EXAMPLES, "spotify-web-api.raml")
        self.api = parse(raml_file)
        self.resources = self.api.resources

    def test_has_path(self):
        for resource in self.resources:
            self.assertIsNotNone(resource.path)

    def test_paths(self):
        raml_file = os.path.join(EXAMPLES + "simple.raml")
        api = self.parse(raml_file)
        resources = api.resources

        expected_paths = ['/tracks', '/search', '/tracks/{id}']

        self.assertEqual(len(resources), len(expected_paths))

        for resource in resources:
            self.assertItemInList(resource.path, expected_paths)

    def test_absolute_uri(self):
        raml_file = os.path.join(EXAMPLES + "base-uri-parameters.raml")
        api = self.parse(raml_file)
        resource = api.resources[0]

        expected_path = 'https://{domainName}.github.com/{apiPath}/foo'
        self.assertEqual(resource.absolute_uri, expected_path)

    def test_has_display_name(self):
        for resource in self.resources:
            self.assertIsNotNone(resource.display_name)

    def test_display_name_not_defined(self):
        raml_file = os.path.join(EXAMPLES + "no-display-name.raml")
        api = self.parse(raml_file)
        resource = api.resources[0]

        self.assertEqual(resource.display_name, '/tracks')
        self.assertEqual(resource.name, resource.display_name)

    def test_has_description(self):
        for resource in self.resources:
            self.assertIsNotNone(resource.description.raw)

    def test_description_markdown(self):
        raml_file = os.path.join(EXAMPLES + "markdown-desc-docs.raml")
        api = self.parse(raml_file)
        resource = api.resources[1]

        html_result = resource.description.html
        expected_result = ("<p><a href=\"https://developer.spotify.com/web-"
                           "api/get-artist/\">Get an Artist</a></p>\n")

        self.assertEqual(html_result, expected_result)

    @unittest.skip("FIXME")
    def test_no_description(self):
        raml_file = os.path.join(EXAMPLES + "resource-no-desc.raml")
        api = self.parse(raml_file)
        resource = api.resources[0]

        self.assertIsNone(resource.description)

    def test_method(self):
        raml_file = os.path.join(EXAMPLES + "simple.raml")
        api = self.parse(raml_file)
        resources = api.resources

        methods = ['get', 'post']

        for resource in resources:
            self.assertItemInList(resource.method, methods)

    def test_protocols(self):
        raml_file = os.path.join(EXAMPLES + "protocols.raml")
        resource = self.parse(raml_file).resources[0]

        expected_protocols = ['HTTP', 'HTTPS']

        self.assertListEqual(resource.protocols, expected_protocols)

    def test_body(self):
        raml_file = os.path.join(EXAMPLES + "simple-body.raml")
        api = self.parse(raml_file)
        resource = api.resources[0]

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
                         "<Body(mime='application/json')>")
        self.assertDictEqual(resource.body[0].data, expected_data)
        self.assertDictEqual(resource.body[0].schema, expected_data['schema'])
        self.assertDictEqual(resource.body[0].example, expected_example)
        self.assertEqual(resource.body[0].mime_type, "application/json")

    def test_body_form_mimetypes(self):
        raml_file = os.path.join(EXAMPLES + "simple-body.raml")
        api = self.parse(raml_file)
        form_encoded = api.resources[1].body[0]
        multipart = api.resources[2].body[0]

        self.assertEqual(repr(form_encoded),
                         "<Body(mime='application/x-www-form-urlencoded')>")
        self.assertEqual(repr(multipart), "<Body(mime='multipart/form-data')>")
        self.assertIsNone(form_encoded.schema)
        self.assertIsNone(multipart.schema)

    def test_responses(self):
        raml_file = os.path.join(EXAMPLES + "responses.raml")
        resource = self.parse(raml_file).resources[0]

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
            self.assertIsInstance(resp.body, parameters.Body)
            self.assertEqual(repr(resp.body),
                             "<Body(mime='application/json')>")
            self.assertIsInstance(resp, parameters.Response)
            self.assertEqual(repr(resp),
                             "<Response(code='{0}')>".format(resp.code))
            self.assertEqual(resp.description.raw,
                             expected_resp_data[resp.code].get('description'))
            if resp.description.raw:
                self.assertEqual(resp.description.html, desc_html)

        exp_headers = expected_resp_data[503]['headers']['X-waiting-period']

        response_503 = responses[1]
        headers = response_503.headers
        for h in headers:
            self.assertIsInstance(h, parameters.Header)
            self.assertDictEqual(h.data, exp_headers)

    def test_headers(self):
        raml_file = os.path.join(EXAMPLES + "headers.raml")
        resources = self.parse(raml_file).resources

        resource = resources[0]
        results = resource.headers

        expected_data = self.f('test_headers')

        self.assertIsInstance(results, list)
        for item in results:
            self.assertItemInList(item.name, list(expected_data.keys()))
            self.assertIsInstance(item, parameters.Header)
            self.assertDictEqual(item.data, expected_data[item.name])

    def test_data(self):
        raml_file = os.path.join(EXAMPLES + "simple.raml")
        api = self.parse(raml_file)
        resources = api.resources

        expected_data = self.f('test_data')

        for resource in resources:
            self.assertItemInList(resource.data, expected_data)

    def test_parent(self):
        raml_file = os.path.join(EXAMPLES + "simple.raml")
        api = self.parse(raml_file)
        resources = api.resources

        expected_parent = '/tracks'

        for resource in resources:
            if resource.parent:
                self.assertEqual(resource.parent.name, expected_parent)
            else:
                self.assertEqual(resource.parent, None)

    @unittest.skip("FIXME")
    def test_traits_resources(self):
        raml_file = os.path.join(EXAMPLES + "simple-traits.raml")
        api = self.parse(raml_file)
        resource = api.resources[0]

        self.assertIsInstance(resource.resource_type, raml.ResourceType)
        self.assertEqual(resource.resource_type.name, 'collection')
        self.assertEqual([t.name for t in resource.traits], ['paged'])

    def test_mapped_traits(self):
        raml_file = os.path.join(EXAMPLES + "mapped-traits-types.raml")
        api = self.parse(raml_file)

        first = api.resource_types[0]
        second = api.resource_types[1]

        first_expected_name = 'searchableCollection'
        second_expected_name = 'collection'

        second_res = api.resources[3]

        second_expected_data = self.f('test_mapped_traits').get('second')

        self.assertEqual(first.name, first_expected_name)
        self.assertEqual(second.name, second_expected_name)

        self.assertEqual(second_res.description.raw,
                         second_expected_data.get('description'))

    @unittest.skip("FIXME: I don't think method traits are getting parsed")
    def test_mapped_form_traits(self):
        raml_file = os.path.join(EXAMPLES + "mapped-traits-types.raml")
        api = self.parse(raml_file)
        resource = api.resources[2]
        form_param = resource.form_params[0]
        self.assertEqual(form_param.name, "aFormTrait")

    def test_secured_by(self):
        raml_file = os.path.join(EXAMPLES + "simple-traits.raml")
        api = self.parse(raml_file)
        resources = api.resources

        for resource in resources:
            self.assertIsNotNone(resource.secured_by)

    def test_no_secured_by(self):
        raml_file = os.path.join(EXAMPLES +
                                 "simple-no-secured-by.raml")
        resources = self.parse(raml_file).resources

        for res in resources:
            self.assertIsNone(res.secured_by)

    def test_not_secured(self):
        raml_file = os.path.join(EXAMPLES + "simple.raml")
        api = self.parse(raml_file)
        resource = api.resources[0]
        self.assertIsNone(resource.secured_by)

    def test_base_uri_params(self):
        raml_file = os.path.join(EXAMPLES + 'base-uri-parameters.raml')
        api = self.parse(raml_file)

        resources = api.resources

        foo = resources[0]
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
            self.assertIsInstance(r, parameters.URIParameter)
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

        bar = resources[1]
        bar_results = bar.base_uri_params

        for i, r in enumerate(bar_results):
            self.assertIsInstance(r, parameters.URIParameter)
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
        api = self.parse(raml_file)
        resources = api.resources

        search = resources[0]
        tracks = resources[1]
        track = resources[2]

        search_q_params = search.query_params
        tracks_q_params = tracks.query_params
        track_q_params = track.query_params

        self.assertEqual(track_q_params, None)

        expected_search_q_params = ['q', 'type', 'limit', 'offset']
        expected_search_data = self.f('test_query_params')

        for param in search_q_params:
            self.assertIsInstance(param, parameters.QueryParameter)
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
            self.assertIsInstance(param, parameters.QueryParameter)
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
        api = self.parse(raml_file)
        resources = api.resources

        search = resources[0]
        tracks = resources[1]
        track = resources[2]

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
            self.assertIsInstance(param, parameters.URIParameter)
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
        api = self.parse(raml_file)
        resource = api.resources[0]
        param = resource.query_params.pop()

        expected_data = self.f('test_primative_type_integer')

        self.assertEqual(repr(param.type), "<IntegerNumber(name='limit')>")
        self.assertDictEqual(param.data, expected_data)
        self.assertEqual(param.type.minimum, expected_data.get('minimum'))
        self.assertEqual(param.type.maximum, expected_data.get('maximum'))
        self.assertIsInstance(param.example, int)

    def test_primative_type_number(self):
        raml_file = os.path.join(EXAMPLES + "primative-param-types.raml")
        api = self.parse(raml_file)
        resource = api.resources[5]
        param = resource.query_params.pop()

        expected_data = self.f('test_primative_type_number')

        self.assertEqual(repr(param.type),
                         "<IntegerNumber(name='numberParam')>")
        self.assertDictEqual(param.data, expected_data)
        self.assertEqual(param.type.minimum, expected_data.get('minimum'))
        self.assertEqual(param.type.maximum, expected_data.get('maximum'))
        self.assertIsInstance(param.example, float)

    def test_primative_type_boolean(self):
        raml_file = os.path.join(EXAMPLES + "primative-param-types.raml")
        api = self.parse(raml_file)
        resource = api.resources[3]
        param = resource.query_params.pop()

        expected_data = self.f('test_primative_type_boolean')

        self.assertEqual(repr(param.type), "<Boolean(name='booleanParam')>")
        self.assertDictEqual(param.data, expected_data)
        self.assertEqual(param.type.repeat, expected_data.get('repeat'))
        self.assertIsInstance(param.default, bool)

    def test_primative_type_date(self):
        raml_file = os.path.join(EXAMPLES + "primative-param-types.raml")
        api = self.parse(raml_file)
        resource = api.resources[1]
        param = resource.query_params.pop()

        expected_data = self.f('test_primative_type_date')

        self.assertEqual(repr(param.type), "<Date(name='dateParam')>")
        self.assertDictEqual(param.data, expected_data)

    def test_primative_type_file(self):
        raml_file = os.path.join(EXAMPLES + "primative-param-types.raml")
        api = self.parse(raml_file)
        resource = api.resources[6]
        param = resource.query_params.pop()

        expected_data = self.f('test_primative_type_file')

        self.assertEqual(repr(param.type), "<File(name='fileParam')>")
        self.assertDictEqual(param.data, expected_data)
        self.assertEqual(param.type.repeat, expected_data.get('repeat'))

    def test_primative_type_string(self):
        raml_file = os.path.join(EXAMPLES + "primative-param-types.raml")
        api = self.parse(raml_file)
        resource = api.resources[4]
        param = resource.query_params.pop()

        expected_data = self.f('test_primative_type_string')

        self.assertEqual(repr(param.type), "<String(name='ids')>")
        self.assertDictEqual(param.data, expected_data)

    def test_form_params(self):
        raml_file = os.path.join(EXAMPLES + "form-parameters.raml")
        api = self.parse(raml_file)
        resources = api.resources

        tracks = resources[0]

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
            self.assertIsInstance(param, parameters.FormParameter)
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
        api = self.parse(raml_file)

        resource = api.resources[2]
        param = resource.query_params[0]
        html_result = param.description.html
        expected_result = ("<p>The country (<a href=\"http://en.wikipedia.org"
                           "/wiki/ISO_3166-1\">an ISO 3166-1 alpha-2 country "
                           "code</a>)</p>\n")

        self.assertEqual(html_result, expected_result)

    def test_req_media_types(self):
        raml_file = os.path.join(EXAMPLES + "req-content-type.raml")
        api = self.parse(raml_file)
        resources = api.resources

        post_playlist = resources[0]

        expected_post_playlist_schema = {
            "name": "New Playlist",
            "public": False
        }
        expected_post_playlist_example = {"foo": "bar"}

        expected_content_types = ['application/json',
                                  'application/x-www-form-urlencoded',
                                  'multipart/form-data']

        for c_type in post_playlist.media_types:
            self.assertItemInList(c_type, expected_content_types)
            if c_type is 'application/json':
                self.assertDictEqual(c_type.schema,
                                     expected_post_playlist_schema)
                self.assertDictEqual(c_type.example,
                                     expected_post_playlist_example)

    @unittest.skip("FIXME: __get_secured_by doesn't parse this file")
    def test_security_schemes(self):
        raml_file = os.path.join(EXAMPLES, "applied-security-scheme.raml")
        api = self.parse(raml_file)
        print(api.resources[0].method)
        applied_schemes = api.resources[0].security_schemes
        exp_data = self.f('test_applied_security_scheme')
        exp_desc = exp_data.get("description")
        self.assertIsInstance(applied_schemes, list)

        for s in applied_schemes:
            self.assertIsInstance(s, parameters.SecurityScheme)
            self.assertEqual(s.name, 'oauth_2_0')
            self.assertDictEqual(s.data, exp_data)
            self.assertEqual(s.type, 'OAuth 2.0')
            self.assertIsInstance(s.described_by, dict)
            self.assertEqual(s.description.raw, exp_desc)
            self.assertIsNotNone(s.settings)
            self.assertHasAttr(s, 'authorizationUri')
            self.assertHasAttr(s, 'accessTokenUri')
            self.assertHasAttr(s, 'authorizationGrants')
            self.asserthasAttr(s, 'scopes')
