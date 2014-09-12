#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
try:
    from collections import OrderedDict
except ImportError:
    # python 2.6
    from ordereddict import OrderedDict

import os

import yaml

from .parameters import (ContentType, FormParameter, URIParameter,
                         QueryParameter)


class RAMLParserError(Exception):
    pass


HTTP_METHODS = ["get", "post", "put", "delete", "patch", "options", "head"]


class EndpointOrder(object):
    """Parses endpoint order to set order for RAML nodes"""
    def __init__(self, yaml_file):
        self.yaml = yaml_file

    @property
    def order(self):
        """
        Returns the desired visual order of endpoints defined in a
        YAML file
        """
        class OrderedLoader(yaml.SafeLoader):
            pass

        def construct_mapping(loader, node):
            loader.flatten_mapping(node)
            return OrderedDict(loader.construct_pairs(node))
        OrderedLoader.add_constructor(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            construct_mapping)

        try:
            return yaml.load(file(self.yaml), OrderedLoader)
        except IOError as e:
            raise RAMLParserError(e)

    @property
    def groupings(self):
        """Returns groupings of endpoints defined in endpoint-order.yaml"""
        return self.order.keys()


class APIRoot(object):

    def __init__(self, raml_file):
        yaml.add_constructor("!include", self.__yaml_include)
        self.raml = self.__raml(raml_file)

    def __yaml_include(self, loader, node):
        # Get the path out of the yaml file
        file_name = os.path.join(os.path.dirname(loader.name), node.value)

        with open(file_name) as inputfile:
            return yaml.load(inputfile)

    def __raml(self, raml_file):
        try:
            return yaml.load(open(raml_file))
        except IOError as e:
            raise RAMLParserError(e)

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
        return self.raml['title'] or None

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
            docs = []
            for doc in documentation:
                doc = Documentation(doc.get('title'), doc.get('content'))
                docs.append(doc)
            return docs
        return None

    @property
    def security_schemes(self):
        return SecuritySchemes(self.raml).security_schemes

    def _parse_trait_query_params(self, trait):
        pass

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


class ResourceType(object):
    def __init__(self, name, data):
        self.name = name
        self.data = data

    @property
    def usage(self):
        return self.data.get('usage')

    @property
    def description(self):
        return self.data.get('description')

    @property
    def type(self):
        return self.data.get('type')

    @property
    def methods(self):
        methods = []
        for m in HTTP_METHODS:
            if self.data.get(m):
                rec = ResourceTypeMethod(m, self.data.get(m))
                methods.append(rec)
            elif self.data.get(m + "?"):
                rec = ResourceTypeMethod(m + "?", self.data.get(m + "?"))
                methods.append(rec)
        return methods


class ResourceTypeMethod(object):
    def __init__(self, name, data):
        self.name = name
        self.data = data

    @property
    def optional(self):
        return "?" in self.name


class Documentation(object):
    # TODO: parse markdown content
    def __init__(self, title, content):
        self.title = title
        self.content = content


class SecuritySchemes(object):
    def __init__(self, raml_file):
        self.raml = raml_file

    def _get_security_schemes(self):
        defined_schemes = self.raml.get('securitySchemes')
        if defined_schemes:
            schemes = []
            for scheme in defined_schemes:
                for k, v in list(scheme.items()):
                    schemes.append(SecurityScheme(k, v))
            return schemes
        else:
            return None

    @property
    def security_schemes(self):
        return self._get_security_schemes()


class SecurityScheme(object):
    def __init__(self, name, data):
        self.name = name
        self.data = data

    @property
    def type(self):
        return self.data.get('type')

    @property
    def described_by(self):
        # TODO: return a Headers, Response object
        return self.data.get('describedBy')

    @property
    def description(self):
        return self.data.get('description')

    def _get_oauth_scheme(self, scheme):
        return {'oauth_2_0': Oauth2Scheme,
                'oauth_1_0': Oauth1Scheme}[scheme]

    @property
    def settings(self):
        schemes = ['oauth_2_0', 'oauth_1_0']
        if self.name in schemes:
            return self._get_oauth_scheme(self.name)(self.data.get('settings'))


class Oauth2Scheme(object):
    def __init__(self, settings):
        self.settings = settings

    @property
    def scopes(self):
        return self.settings.get('scopes')  # list of strings

    @property
    def authorization_uri(self):
        return self.settings.get('authorizationUri')  # string

    @property
    def access_token_uri(self):
        return self.settings.get('accessTokenUri')  # string

    @property
    def authorization_grants(self):
        return self.settings.get('authorizationGrants')  # list of strings


class Oauth1Scheme(object):
    def __init__(self, settings):
        self.settings = settings

    @property
    def request_token_uri(self):
        return self.settings.get('requestTokenUri')

    @property
    def authorization_uri(self):
        return self.settings.get('authorizationUri')

    @property
    def token_credentials_uri(self):
        return self.settings.get('tokenCredentialsUri')


class Headers(object):
    def __init__(self):
        pass


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
        return self.data.get('displayName', '')

    @property
    def description(self):
        return self.data.get(self.method).get('description')

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
        if isinstance(secured_by, list):
            _secured_by = []
            for secured in secured_by:
                if isinstance(secured, dict):
                    _secured_by.append(secured.keys()[0])
                else:
                    _secured_by.append(secured)
            return _secured_by
        return secured_by

    @property
    def secured_by(self):
        return self._get_secured_by()

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
            else:
                return None
            for item in secured_by:
                if isinstance(item, dict) and 'oauth_2_0' in item.keys():
                    return item.get('oauth_2_0').get('scopes')
        return None

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
                form_header = 'x-www-form-urlencoded'
                # TODO: check that this works with other HTTP verbs
                # such as DELETE, PATCH, etc
                form = node.data.get(self.method).get('body').get(form_header)
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
