#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function

__all__ = ["APIRoot", "Resource", "RAMLParserError"]

import json
import re

from six.moves import BaseHTTPServer as httpserver

try:
    from collections import OrderedDict
except ImportError:  # pragma: no cover
    from ordereddict import OrderedDict

from .parameters import (
    ContentType, FormParameter, URIParameter,
    QueryParameter, Header, Response, ResourceType,
    Documentation, SecuritySchemes, Body, DescriptiveContent
)
from .utils import find_params


HTTP_RESP_CODES = httpserver.BaseHTTPRequestHandler.responses.keys()


class RAMLParserError(Exception):
    pass


class APIRoot(object):
    """
    The Root of the API object

    :param obj load_object: Loaded RAML from ``ramlfications.load(ramlfile)``
    """
    def __init__(self, load_object):
        # The line below can throw an exception but that's not documented.
        # I find it awkward too as I don't like it when constructors
        # throw exceptions.
        self.raml = load_object.load()
        self.raml_file = load_object.name

    @property
    def resources(self):
        """
        Returns a dict of RAML resources/endpoints, with keys set to the
        method + resource display name (e.g. ``get-item``) and values set
        to the ``Resource`` object.
        """
        resource_stack = ResourceStack(self, self.raml).yield_resources()
        resource = OrderedDict()
        for res in resource_stack:
            key_name = res.method + "-" + res.display_name
            resource[key_name] = res
        return resource

    @property
    def title(self):
        """
        Returns the title property defined in the root section of the API.
        """
        return self.raml.get('title')

    @property
    def version(self):
        """
        Returns the API version.
        """
        return self.raml.get('version')

    @property
    def protocols(self):
        """
        Returns the supported protocols of the API.  If not set, then
        grabbed from ``base_uri``.
        """
        protocol = re.findall(r"(https|http)", self.base_uri)
        return self.raml.get('protocols', protocol)

    @property
    def base_uri(self):
        """
        Returns the base URI of API.

        **Note:** optional during development, required after implementation.

        :raises RAMLParserError: if no ``version`` is defined but is\
        referenced in the ``baseUri`` parameter.
        """
        # Default base_uri to '' in the get method, then get rid of
        # the if-statement one line below.
        base_uri = self.raml.get('baseUri')
        if base_uri:
            if "{version}" in base_uri:
                try:
                    return base_uri.replace("{version}", self.raml['version'])
                except KeyError:
                    # Akward formatting. Break the line below after the
                    # opening parens.
                    raise RAMLParserError("No API Version defined even though "
                                          "version is referred in the baseUri")
            else:
                return base_uri
        return None

    @property
    def uri_parameters(self):
        """
        Returns URI Parameters available for the baseUri and all
        resources/endpoints.  Returns ``None`` if no URI parameters
        are defined.

        :raises RAMLParserError: if ``version`` is defined (``version``
        can only be used in ``baseUriParameters``).
        """
        uri_params = self.raml.get('uriParameters', {})
        params = []
        for k, v in list(uri_params.items()):
            if k == 'version':
                raise RAMLParserError("'version' can only be defined "
                                      "in baseUriParameters")
            params.append((URIParameter(k, v)))
        return params or None

    @property
    def base_uri_parameters(self):
        """
        Returns URI Parameters for meant specifically for the ``base_uri``.
        Returns ``None`` if no base URI parameters are defined.

        **Note:** optional during development, required after implementation.
        """
        base_uri_params = self.raml.get('baseUriParameters', {})
        uri_params = []
        for k, v in list(base_uri_params.items()):
            uri_params.append((URIParameter(k, v)))
        return uri_params or None

    @property
    def media_type(self):
        """
        Returns the supported Media Types of the API.  Returns ``None``
        if no media types are defined.

        Valid media types:

        * ``text/yaml``, ``text/x-yaml``, ``application/yaml``,\
         ``application/x-yaml``
        * Any defined in http://www.iana.org/assignments/media-types
        * A custom type that follows the regex:\
        ``application\/[A-Za-z.-0-1]*+?(json|xml)``

        """
        return self.raml.get('mediaType')

    @property
    def resource_types(self):
        """
        Returns defined Resource Types.  Returns ``None if no resource
        types are defined.
        """
        resource_types = self.raml.get('resourceTypes', {})
        resources = []
        for resource in resource_types:
            resources.append(ResourceType(list(resource.keys())[0],
                                          list(resource.values())[0]))
        return resources or None

    @property
    def documentation(self):
        """
        Returns a list of Documentation objects meant for user documentation
        of the for the API, or ``None`` if no documentation is defined.

        :raises RAMLParserError: if can not parse documentation.
        """
        documentation = self.raml.get('documentation', [])
        if not isinstance(documentation, list):
            msg = "Error parsing documentation"
            raise RAMLParserError(msg)
        docs = []
        for doc in documentation:
            doc = Documentation(doc.get('title'), doc.get('content'))
            docs.append(doc)
        return docs or None

    @property
    def security_schemes(self):
        """
        Returns a list of SecurityScheme objects supported by the API,
        or ``None`` if none are defined.

        Valid security schemes are: OAuth 1.0, OAuth 2.0, Basic Authentication,
         Digest Authentication, and API-defined auth with ``x-{other}``.
        """
        return SecuritySchemes(self.raml).security_schemes

    @property
    def traits(self):
        """
        Returns a list of traits, or ``None`` if non are defined.
        """
        traits = self.raml.get('traits', [])
        trait_params = []
        for trait in traits:
            for key, value in list(trait.items()):
                items = value.get('queryParameters')
                for k, v in list(items.items()):
                    trait_params.append({key: QueryParameter(k, v)})
        return trait_params or None

    def _parse_parameters(self):
        """
        If traits or resourceTypes contain <<parameter>> in definition
        """
        _resources_params = []
        # Default self._resource_types to empty list to get rid of this
        # if-statement.
        # LR: returns None if none define, so will need the if-statement
        if self.resource_types:
            for r in self.resource_types:
                data = json.dumps(r.data)
                match = find_params(data)
                # Not sure about the += here, I would prefer "append".
                _resources_params.extend(match)

        _traits_params = []
        # Same concern as above.
        # LR: returns None if none define, so will need the if-statement
        if self.traits:
            for t in self.traits:
                data = json.dumps(list(t.keys()))
                match = find_params(data)
                _traits_params.extend(match)

                # Is t.values() guaranteed to be non-empty? If not,
                # the next line will crash.
                data = json.dumps(list(t.values())[0].data)
                match = find_params(data)
                _traits_params.extend(match)

        # Instead of the list(set) combo just make _traits_params and
        # _resource_params a set initially.
        return dict(resource_types=list(set(_resources_params)),
                    traits=list(set(_traits_params)))

    def get_parameters(self):
        """
        Returns <<parameters>> used in traits and/or resource_types.
        """
        return self._parse_parameters()

    @property
    def schemas(self):
        """
        Returns a dict of user-defined schemas that may be applied anywhere
        in the API definition.

        Current explicit supported types are XML, JSON, YAML. Other schema
        definitions may work at your own risk.

        Returns ``None`` if no schema defined.
        """
        return self.raml.get('schemas')

    def __repr__(self):
        return '<APIRoot(raml_file="{0}")>'.format(self.raml_file)


class ResourceStack(object):
    def __init__(self, api, raml_file):
        self.api = api
        self.raml = raml_file

    def yield_resources(self):
        """
        Yields Resource objects for the API defined in the RAML File.
        """
        available_methods = ['get', 'post', 'put', 'delete',
                             'patch', 'head', 'options']
        resource_stack = []

        # Akward code, create a helper method for it.
        for k, v in list(self.raml.items()):
            if k.startswith("/"):
                for method in available_methods:
                    if method in self.raml[k].keys():
                        node = Resource(name=k, data=v, method=method,
                                        api=self.api)
                        resource_stack.append(node)

        # Akward code, create a helper method for it.
        while resource_stack:
            current = resource_stack.pop(0)
            yield current
            if current.data:
                for child_k, child_v in list(current.data.items()):
                    if child_k.startswith("/"):
                        for method in available_methods:
                            if method in current.data[child_k].keys():
                                child = Resource(name=child_k, data=child_v,
                                                 method=method, parent=current,
                                                 api=self.api)
                                resource_stack.append(child)


class Resource(object):
    """
    An API's endpoint (resource) defined in RAML, identified by a leading
    slash, ``/``.
    """
    def __init__(self, name, data, method, api, parent=None):
        self.name = name
        self.data = data
        self.api = api
        self.parent = parent
        self.method = method

    def _get_path_to(self, node):
        # parent_path = self._get_path_to(node,parent, '')
        parent_path = ''
        if node.parent:
            parent_path = self._get_path_to(node.parent)
        return parent_path + node.name

    @property
    def display_name(self):
        """
        Returns the Resource's display name.

        A friendly name used only for display or documentation purposes.

        If ``displayName`` is not specified in RAML, it defaults to ``name``.
        """
        return self.data.get('displayName', self.name)

    @property
    def description(self):
        """
        Returns ``DescriptiveContent`` object with ``raw`` and ``html``
        attributes, or ``None`` if not defined.

        Assumes raw content is written in plain text or Markdown in RAML
        per specification. (Optional)
        """
        return DescriptiveContent(self.data.get('description'))

    @property
    def headers(self):
        """
        Returns a list of Header objects that the endpoint accepts.

        Returns ``None`` if no headers defined.
        """
        _headers = self.data.get(self.method).get('headers', {})
        headers = []
        for k, v in list(_headers.items()):
            headers.append(Header(k, v, self.method))
        return headers or None

    @property
    def path(self):
        """
        Returns string URI path of Resource.

        Not explicitly defined in RAML but inferred based off of
        the Resource ``name``.
        """
        return self._get_path_to(self)

    @property
    def absolute_path(self):
        """
        Return the full API URL for Resource.

        Not explicitly defined in RAML but inferred based off of
        ``path`` and the API root's ``base_uri``.
        """
        return self.api.base_uri + self.path

    def _get_secured_by(self):
        # TODO: put a validator in to check if schemes here are not in
        # list of secured schemes
        # I'd create a helper method for the if-statement below.
        if self.data.get('securedBy'):
            secured_by = self.data.get('securedBy')
        # Can self.method be None? If yes, the next line crashes.
        elif self.data.get(self.method).get('securedBy'):
            secured_by = self.data.get(self.method).get('securedBy')
        else:
            return None

        _secured_by = []
        for secured in secured_by:
            if isinstance(secured, dict):
                scheme = list(secured.keys())[0]
                if 'scopes' in list(secured.values())[0]:
                    scopes = list(secured.values())[0].get('scopes')
            else:
                # What's the expected type here? Can you make sure
                # that "secured" has a valid format?
                scheme = secured
                scopes = None

            _scheme = {}
            for s in self.api.security_schemes:
                if s.name == scheme:
                    _scheme['name'] = s.name
                    _scheme['type'] = s.type
                    _scheme['scheme'] = s
                if scopes:
                    _scheme['scopes'] = scopes

                if _scheme not in _secured_by:
                    _secured_by.append(_scheme)
        return _secured_by

    @property
    def secured_by(self):
        """
        Returns authentication protocol information if Resource is secured
        """
        return self._get_secured_by()

    def _fill_reserved_params(self, string):
        if "<<resourcePathName>>" in string:
            name = self.name[1:]  # assumes all path names start with '/'
            string = string.replace("<<resourcePathName>>", name)
        if "<<resourcePath>>" in string:
            string = string.replace("<<resourcePath>>", self.name)

        # Unclear to me if this is even a valid code path that makes
        # sense.
        # LR: will return string that was passed in if there are no
        # reserved params used (resourcePathName, resourcePath)
        return string

    def _fill_params(self, string, key, value):
        if key in string:
            string = string.replace("<<" + key + ">>", value)
        string = self._fill_reserved_params(string)
        return string

    def _map_resource_string(self, res_type):
        # Can res_type be empty? If yes, next line crashes.
        # LR: No - it's either None or a string, if None, then
        # this function won't even be called
        api_resources = self.api.resource_types

        api_resources_names = [a.name for a in api_resources]
        if res_type not in api_resources_names:
            msg = "'{0}' is not defined in API Root's resourceTypes."
            raise RAMLParserError(msg)

        results = []
        for r in api_resources:
            if r.name == res_type:
                result = dict(name=r.name, usage=r.usage)
                methods = r.methods
                for m in methods:
                    if self.method == m.name:
                        desc = m.data.get('description', r.description.raw)
                    else:
                        # otherwise use the general description
                        desc = r.description.raw
                    result['description'] = self._fill_reserved_params(desc)
                results.append(result)

        return results[0]

    def _map_resource_dict(self, res_type):
        api_resources = self.api.resource_types

        # Can res_type be empty? If yes, next line crashes.
        # LR: No - it's either None or a dict, if None, then
        # this function won't even be called
        _type = list(res_type.keys())[0]
        # Can api_resources be None? If yes, next line crashes.
        api_resources_names = [a.name for a in api_resources]
        if _type not in api_resources_names:
            msg = "'{0}' is not defined in API Root's resourceTypes."
            raise RAMLParserError(msg)

        for r in api_resources:
            if r.name == _type:
                _values = list(res_type.values())[0]
                data = json.dumps(r.data)
                for k, v in list(_values.items()):
                    data = self._fill_params(data, k, v)
                # Can next line throw exceptions that are not caught
                # or documented?
                # LR: How would I test to see this?
                data = json.loads(data)
                result = dict(name=r.name, data=data)
                return result

    def _get_resource_type(self):
        # NOTE: Extremely naive implementation, esp for dicts
        res_type = self.data.get('type')
        if res_type:
            mapped_res_type = {}
            if isinstance(res_type, str):
                mapped_res_type = self._map_resource_string(res_type)

            elif isinstance(res_type, dict):
                if len(res_type.keys()) > 1:
                    msg = "Too many resource types applied to one resource."
                    raise RAMLParserError(msg)
                mapped_res_type = self._map_resource_dict(res_type)

            elif isinstance(res_type, list):
                if len(res_type) > 1:
                    msg = "Too many resource types applied to one resource."
                    raise RAMLParserError(msg)
                mapped_res_type = self._map_resource_string(res_type[0])

            else:
                msg = "Error applying resource type '{0}'' to '{1}'.".format(
                    res_type, self.name)
                raise RAMLParserError(msg)
            return mapped_res_type

    @property
    def resource_type(self):
        """
        Returns a list of resource types assigned to the resource.

        :raises RAMLParserError: Too many resource types applied to one \
        resource.
        :raises RAMLParserError: Resource not defined in the API Root.
        :raises RAMLParserError: If resource type is something other \
        than a ``str`` or ``dict``.
        """
        return self._get_resource_type()

    @property
    def traits(self):
        """
        Returns a list of traits assigned to the Resource.
        """
        endpoint_traits = self.data.get('is', [])
        method_traits = self.data.get(self.method).get('is', [])
        return endpoint_traits + method_traits

    @property
    def scopes(self):
        """Returns a list of OAuth2 scopes assigned to the resource"""
        # Code is awkward, can this be structured better?
        if self.secured_by:
            for item in self.secured_by:
                if 'oauth_2_0' in item.values():
                    if self.data.get('securedBy'):
                        for i in self.data.get('securedBy'):
                            if isinstance(i, dict) and 'oauth_2_0' in i.keys():
                                return i.get('oauth_2_0').get('scopes')
                    elif self.data.get(self.method).get('securedBy'):
                        for i in self.data.get('securedBy'):
                            if isinstance(i, dict) and 'oauth_2_0' in i.keys():
                                return i.get('oauth_2_0').get('scopes')
        else:
            return None

    @property
    def protocols(self):
        """
        Returns a list of supported protocols for the particular resource.

        Overrides the root API's protocols.  Returns ``None`` if not defined.
        """
        return self.data.get(self.method).get('protocols')

    def _get_responses(self, node):
        resps = []
        responses = self.data.get(self.method).get('responses', {})
        # Why are you turning responses.items() into a list? You
        # do this all over the place but I don't know why.
        # LR: this is for py3 compatibility.  py3 .items()s returns a
        # generator but I want an interator.
        for k, v in list(responses.items()):
            if k in HTTP_RESP_CODES:
                resps.append(Response(k, v, self.method))
            else:
                msg = "{0} not a supported HTTP Response code".format(k)
                raise RAMLParserError(msg)

        return resps

    @property
    def responses(self):
        """
        Returns a list of Response objects of a resource.

        :raises RAMLParserError: Unsupported HTTP Response code
        """
        return self._get_responses(self)

    def _get_body(self, node):
        bodies = []
        _bodies = self.data.get(self.method).get('body', {})
        for k, v in list(_bodies.items()):
            bodies.append(Body(k, v))
        return bodies or None

    @property
    def body(self):
        """
        Returns a Body object of a request if defined in RAML, or ``None``
        if not.
        """
        return self._get_body(self)

    def _get_uri_params(self, node, uri_params):
        """Returns a list of URIParameter Objects"""
        # uri_params = self._get_uri_params(node.parent, [])
        # then remove if-statement.
        # LR: then this would fail if ``node.parent`` = None
        if node.parent:
            uri_params = self._get_uri_params(node.parent, [])
        if 'uriParameters' in node.data:
            for k, v in list(node.data['uriParameters'].items()):
                uri_params.append((URIParameter(k, v)))
        # LR: How can I better do this 'if-if-if statement'?
        if self.resource_type:
            if self.resource_type.get('data'):
                if 'uriParameters' in self.resource_type['data'].get(
                        self.method):
                    items = self.resource_type['data'][self.method][
                        'uriParameters'].items()
                    for k, v in list(items):
                        uri_params.append((URIParameter(k, v)))
        return uri_params

    @property
    def uri_params(self):
        """
        Returns a list of ``URIParameter`` objects of a ``Resource``, or
        ``None`` if none are defined.
        """
        return self._get_uri_params(self, []) or None

    def _get_base_uri_params(self, node, base_uri_params):
        """
        Returns a list of ``URIParameter`` objects for the ``base_uri``
        """
        if node.parent:
            base_uri_params = self._get_base_uri_params(node.parent, [])
        if 'baseUriParameters' in node.data:
            for k, v in list(node.data['baseUriParameters'].items()):
                base_uri_params.append((URIParameter(k, v)))
        return base_uri_params

    @property
    def base_uri_params(self):
        """
        Returns a list of Base ``URIParameter`` objects of a Resource.
        """
        return self._get_base_uri_params(self, []) or None

    def _get_query_params(self, node):
        query_params = []
        if 'queryParameters' in node.data[self.method]:
            items = node.data[self.method]['queryParameters'].items()
            for k, v in list(items):
                query_params.append((QueryParameter(k, v)))
        if self.resource_type:
            if self.resource_type.get('data'):
                if 'queryParameters' in self.resource_type['data'][self.method]:
                    items = self.resource_type['data'][self.method][
                        'queryParameters'].items()
                    for k, v in list(items):
                        query_params.append((QueryParameter(k, v)))
        return query_params

    @property
    def query_params(self):
        """
        Returns a list of ``QueryParameter`` objects, or ``None`` if no
        query parameters are defined.
        """
        return self._get_query_params(self) or None

    def _get_form_params(self, node):
        # TODO: abstract away the body/app/json shiz
        form_params = []
        if self.method in ['post', 'delete', 'put', 'patch']:
            if 'body' in node.data.get(self.method):
                form_headers = ['application/x-www-form-urlencoded',
                                'multipart/form-data']
                for header in form_headers:
                    form = node.data.get(self.method).get('body').get(header)
                    if form and form.get('formParameters'):
                        for k, v in list(form['formParameters'].items()):
                            form_params.append((FormParameter(k, v)))
            if self.resource_type:
                if self.resource_type.get('data'):
                    if 'formParameters' in self.resource_type['data'][self.method]:
                        items = self.resource_type['data'][self.method][
                            'formParameters'].items()
                        for k, v in list(items):
                            form_params.append((FormParameter(k, v)))
        return form_params

    @property
    def form_params(self):
        """
        Returns a list of FormParameter objects, or ``None`` if no form
        parameters are defined.
        """
        # TODO: seems like there isn't a test for this if None?
        return self._get_form_params(self)

    @property
    def req_content_types(self):
        """
        Returns a list of ``ContentType`` objects that the Resource supports.
        """
        # TODO: seems like there isn't a test for this if None?
        content_type = []
        if self.method in ["post", "put", "delete", "patch"]:
            if self.data.get(self.method).get('body'):
                # grabs all content types
                content_types = self.data.get(self.method).get('body')
                types = self.data.get(self.method).get('body').keys()
                # TODO: skip www-form-encoded
                for content in types:
                    schema = content_types.get(content).get('schema')
                    example = content_types.get(content).get('example')
                    content_type.append(ContentType(content, schema, example))
        return content_type or None

    def __repr__(self):
        return "<Resource(name='{0}')>".format(self.name)
