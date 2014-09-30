#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
try:
    from collections import OrderedDict
except ImportError:  # pragma: no cover
    # python 2.6
    from ordereddict import OrderedDict

import re

from .loader import RAMLLoader
from .parameters import (ContentType, FormParameter, URIParameter,
                         QueryParameter, Header, Response, ResourceType,
                         Documentation, SecuritySchemes)


class RAMLParserError(Exception):
    pass


HTTP_RESP_CODES = [100, 101, 102,
                   200, 201, 202, 203, 204, 205, 206, 207, 208, 226,
                   300, 301, 302, 303, 304, 305, 306, 307, 308,
                   400, 401, 402, 403, 404, 405, 406, 407, 408, 409,
                   410, 411, 412, 413, 414, 415, 416, 417, 418, 420,
                   422, 423, 424, 425, 426, 428, 429, 431, 444, 449,
                   450, 499,
                   500, 501, 502, 503, 504, 505, 509, 510, 511, 598,
                   599]


class APIRoot(object):
    def __init__(self, raml_file):
        self.raml = RAMLLoader(raml_file).raml

    @property
    def nodes(self):
        nodes_stack = NodeStack(self.raml).yield_nodes()
        nodes = OrderedDict()
        for node in nodes_stack:
            key_name = node.method + "-" + node.display_name
            nodes[key_name] = node
        return nodes

    @property
    def title(self):
        return self.raml.get('title')

    @property
    def protocols(self):
        return self.raml.get('protocols')

    @property
    def base_uri(self):
        base_uri = self.raml.get('baseUri')
        if base_uri:
            if "{version}" in base_uri:
                try:
                    return base_uri.replace("{version}", self.raml['version'])
                except KeyError:
                    raise RAMLParserError("No API Version defined even though "
                                          "version is referred in the baseUri")
            else:
                return base_uri
        return None

    @property
    def uri_parameters(self):
        uri_params = self.raml.get('uriParameters')
        if uri_params:
            params = []
            for k, v in list(uri_params.items()):
                if k == 'version':
                    raise RAMLParserError("'version' can only be defined "
                                          "in baseUriParameters")
                params.append((URIParameter(k, v)))
            return params
        return None

    @property
    def base_uri_parameters(self):
        base_uri_params = self.raml.get('baseUriParameters')
        if base_uri_params:
            uri_params = []
            for k, v in list(base_uri_params.items()):
                uri_params.append((URIParameter(k, v)))
            return uri_params
        return None

    @property
    def media_type(self):
        return self.raml.get('mediaType')

    @property
    def resource_types(self):
        resource_types = self.raml.get('resourceTypes')
        if resource_types:
            resources = []
            for resource in resource_types:
                resources.append(ResourceType(list(resource.keys())[0],
                                              list(resource.values())[0]))
            return resources
        return None

    @property
    def documentation(self):
        documentation = self.raml.get('documentation')
        if documentation:
            if not isinstance(documentation, list):
                msg = "Error parsing documentation"
                raise RAMLParserError(msg)
            docs = []
            for doc in documentation:
                doc = Documentation(doc.get('title'), doc.get('content'))
                docs.append(doc)
            return docs
        return None

    @property
    def security_schemes(self):
        return SecuritySchemes(self.raml).security_schemes

    @property
    def traits(self):
        traits = self.raml.get('traits')
        trait_params = []
        for trait in traits:
            for key, value in list(trait.items()):
                items = value.get('queryParameters')
                for k, v in list(items.items()):
                    trait_params.append({key: QueryParameter(k, v)})
        return trait_params

    def __find_params(self, string):
        # TODO: ignoring humanizers for now
        match = re.findall(r"(<<.*?>>)", string)
        match = [m[2:-2] for m in match]  # clean <<>> first
        ret = []
        for m in match:
            if "!singularlize" or "!pluralize" in m:  # clean out humanizers
                param = m.split(" | ")[0]
                param = "<<{0}>>".format(param)  # then put back <<>>
                if param not in ret:
                    ret.append(param)
            else:
                if m not in ret:
                    param = "<<{0}>>".format(m)
                    ret.append(param)

        return ret

    def __parse_parameters(self):
        """If traits or resourceTypes contain <<parameter>> in definition"""
        _resources_params = []
        if self.resource_types:
            for r in self.resource_types:
                data = json.dumps(r.data)
                match = self.__find_params(data)
                _resources_params += match

        _traits_params = []
        if self.traits:
            for t in self.traits:
                data = json.dumps(t.keys())
                match = self.__find_params(data)
                _traits_params += match

                data = json.dumps(t.values()[0].data)
                match = self.__find_params(data)
                _traits_params += match

        return dict(resource_types=list(set(_resources_params)),
                    traits=list(set(_traits_params)))

    def get_parameters(self):
        return self.__parse_parameters()

    @property
    def schemas(self):
        return self.raml.get('schemas')


class NodeStack(object):
    def __init__(self, raml_file):
        self.raml = raml_file

    def yield_nodes(self):
        available_methods = ['get', 'post', 'put', 'delete',
                             'patch', 'head', 'options']
        node_stack = []

        for k, v in list(self.raml.items()):
            if k.startswith("/"):
                for method in available_methods:
                    if method in self.raml[k].keys():
                        node = Node(name=k, data=v, method=method)
                        node_stack.append(node)
        while node_stack:
            current = node_stack.pop(0)
            yield current
            if current.data:
                for child_k, child_v in list(current.data.items()):
                    if child_k.startswith("/"):
                        for method in available_methods:
                            if method in current.data[child_k].keys():
                                child = Node(child_k, child_v, method, current)
                                node_stack.append(child)


class Node(object):
    def __init__(self, name, data, method, parent=None):
        self.name = name
        self.data = data
        self.parent = parent
        self.method = method

    def _get_path_to(self, node):
        parent_path = ''
        if node.parent:
            parent_path = self._get_path_to(node.parent)
        return parent_path + node.name

    @property
    def display_name(self):
        display_name = self.data.get('displayName')
        if not display_name:
            display_name = self.name
        return display_name

    @property
    def description(self):
        return self.data.get(self.method).get('description')

    @property
    def headers(self):
        _headers = self.data.get(self.method).get('headers')
        headers = []
        if _headers:
            for k, v in list(_headers.items()):
                headers.append(Header(k, v, self.method))
        return headers

    @property
    def path(self):
        """Returns string URI path of Node"""
        return self._get_path_to(self)

    def _get_secured_by(self):
        # TODO: put a validator in to check if schemes here are not in
        # list of secured schemes
        if self.data.get('securedBy'):
            secured_by = self.data.get('securedBy')
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
        return self._get_secured_by()

    @property
    def resource_type(self):
        return self.data.get('type', '')

    @property
    def traits(self):
        endpoint_traits = self.data.get('is', [])
        method_traits = self.data.get(self.method).get('is', [])
        return endpoint_traits + method_traits

    @property
    def scopes(self):
        if self.secured_by and 'oauth_2_0' in self.secured_by:
            if self.data.get('securedBy'):
                secured_by = self.data.get('securedBy')
            elif self.data.get(self.method).get('securedBy'):
                secured_by = self.data.get(self.method).get('securedBy')

            for item in secured_by:
                if isinstance(item, dict) and 'oauth_2_0' in item.keys():
                    return item.get('oauth_2_0').get('scopes')
        return None

    @property
    def protocols(self):
        """Returns a list of supported protocols"""
        return self.data.get(self.method).get('protocols', [])

    def _get_responses(self, node):
        resps = []
        responses = self.data.get(self.method).get('responses')
        if responses:
            for k, v in list(responses.items()):
                if k not in HTTP_RESP_CODES:
                    msg = "{0} not a supported HTTP Response code".format(k)
                    raise RAMLParserError(msg)
                else:
                    resps.append(Response(k, v, self.method))

        return resps

    @property
    def responses(self):
        """Returns responses of a given method"""
        return self._get_responses(self)

    def _get_uri_params(self, node):
        """Returns a list of URIParameter Objects"""
        uri_params = []
        if node.parent:
            uri_params = self._get_uri_params(node.parent)
        if 'uriParameters' in node.data:
            for k, v in list(node.data['uriParameters'].items()):
                uri_params.append((URIParameter(k, v)))
        return uri_params

    @property
    def uri_params(self):
        """Returns URI parameters of Node"""
        return self._get_uri_params(self)

    def _get_base_uri_params(self, node):
        """Returns a list of (base) URIParameter objects"""
        base_uri_params = []
        if node.parent:
            base_uri_params = self._get_base_uri_params(node.parent)
        if 'baseUriParameters' in node.data:
            for k, v in list(node.data['baseUriParameters'].items()):
                base_uri_params.append((URIParameter(k, v)))
        return base_uri_params

    @property
    def base_uri_params(self):
        """Returns Base URI params of a Node"""
        return self._get_base_uri_params(self)

    def _get_query_params(self, node):
        """Returns a list of QueryParameter objects"""
        query_params = []
        if 'queryParameters' in node.data[self.method]:
            items = node.data[self.method]['queryParameters'].items()
            for k, v in list(items):
                query_params.append((QueryParameter(k, v)))
        return query_params

    @property
    def query_params(self):
        """Returns query parameters of Node"""
        return self._get_query_params(self)

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
        return form_params

    @property
    def form_params(self):
        """Returns a list of FormParameter objects"""
        return self._get_form_params(self)

    @property
    def req_content_types(self):
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
        return content_type
