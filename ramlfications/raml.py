# ! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function

__all__ = ["RAMLRoot", "Trait", "ResourceType", "Resource", "RAMLParserError"]

import re


from six.moves import BaseHTTPServer as httpserver

from .parameters import (
    FormParameter, URIParameter, QueryParameter,
    Header, Response, Body, SecuritySchemes,
    Documentation, DescriptiveContent
)
from .utils import memoized, fill_reserved_params

HTTP_RESP_CODES = httpserver.BaseHTTPRequestHandler.responses.keys()
AVAILABLE_METHODS = ['get', 'post', 'put', 'delete', 'patch', 'head',
                     'options', 'trace', 'connect']
HTTP_METHODS = [
    "get", "post", "put", "delete", "patch", "options",
    "head", "trace", "connect", "get?", "post?", "put?", "delete?",
    "patch?", "options?", "head?", "trace?", "connect?"
]


class RAMLParserError(Exception):
    pass


class RAMLRoot(object):
    def __init__(self, raml_obj):
        self.raml = raml_obj.data
        self.raml_file = raml_obj.raml_file
        self.__resources = None
        self.__resource_types = None
        self.__traits = None

    @property
    def resources(self):
        """
        Returns a list of ``Resource`` objects.
        """
        return self.__resources

    @resources.setter
    def resources(self, resource_objs):
        self.__resources = resource_objs

    @property
    def resource_types(self):
        return self.__resource_types

    @resource_types.setter
    def resource_types(self, resource_type_objs):
        self.__resource_types = resource_type_objs

    @property
    def traits(self):
        """
        Returns a list of traits, or ``None`` if non are defined.
        """
        return self.__traits

    @traits.setter
    def traits(self, trait_objs):
        self.__traits = trait_objs

    @property
    @memoized
    def title(self):
        """
        Returns the title property defined in the root section of the API.
        """
        return self.raml.get('title')

    @property
    @memoized
    def version(self):
        """
        Returns the API version.
        """
        return self.raml.get('version')

    @property
    @memoized
    def protocols(self):
        """
        Returns the supported protocols of the API.  If not set, then
        grabbed from ``base_uri``.
        """
        protocol = re.findall(r"(https|http)", self.base_uri)
        return self.raml.get('protocols', protocol)

    @property
    @memoized
    def base_uri(self):
        """
        Returns the base URI of API.

        **Note:** optional during development, required after implementation.

        :raises RAMLParserError: if no ``version`` is defined but is\
        referenced in the ``baseUri`` parameter.
        """
        base_uri = self.raml.get('baseUri')
        if base_uri:
            if "{version}" in base_uri:
                try:
                    return base_uri.replace("{version}", self.raml['version'])
                # Double-check KeyError behavior
                except KeyError:
                    # Double-check all files for consistency of
                    # double-ticks vs single-ticks for strings
                    raise RAMLParserError(
                        "No API Version defined even though version is "
                        "referred in the baseUri")

        return base_uri

    @property
    @memoized
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
    @memoized
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
    @memoized
    def media_type(self):
        # TODO: raise an error if not acceptable media type given
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
    @memoized
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
    @memoized
    def security_schemes(self):
        """
        Returns a list of SecurityScheme objects supported by the API,
        or ``None`` if none are defined.

        Valid security schemes are: OAuth 1.0, OAuth 2.0, Basic Authentication,
         Digest Authentication, and API-defined auth with ``x-{other}``.
        """
        return SecuritySchemes(self.raml).security_schemes

    @property
    @memoized
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
        return '<RAMLRoot(raml_file="{0}")>'.format(self.raml_file)


class _BaseResourceProperties(object):
    """
    Base class from which Trait and _BaseResource inherit.
    """
    def __init__(self, name, data, api):
        self.name = name
        self.data = data
        self.api = api

    @property
    @memoized
    def headers(self):
        """
        Returns a list of accepted Header objects.

        Returns ``None`` if no headers defined.
        """
        resource_headers = self.data.get('headers', {})
        headers = []
        for k, v in list(resource_headers.items()):
            headers.append(Header(k, v))
        return headers or None

    @property
    @memoized
    def body(self):
        """
        Returns a list of Body objects of a request or
        ``None`` if none defined.
        """
        bodies = []
        resource_body = self.data.get('body', {})
        for k, v in list(resource_body.items()):
            bodies.append(Body(k, v))
        return bodies or None

    @property
    @memoized
    def responses(self):
        """
        Returns a list of ``Response`` objects of a Trait, or ``None``
        if none are defined.

        :raises RAMLParserError: Unsupported HTTP Response code
        """
        resps = []
        resource_responses = self.data.get('responses', {})
        for k, v in list(resource_responses.items()):
            if int(k) in HTTP_RESP_CODES:
                resps.append(Response(k, v, self.method))
            else:
                msg = "{0} not a supported HTTP Response code".format(k)
                raise RAMLParserError(msg)

        return resps or None

    @property
    @memoized
    def uri_params(self):
        """
        Returns a list of ``URIParameter`` objects of a Trait, or
        ``None`` if none are defined.
        """
        uri_params = []
        for k, v in list(self.data.get('uriParameters', {}).items()):
            uri_params.append((URIParameter(k, v)))

        return uri_params or None

    @property
    @memoized
    def base_uri_params(self):
        """
        Returns a list of ``URIParameter`` objects of a Trait for
        ``base_uri``, or ``None`` if none are defined.
        """
        base_uri_params = []
        for k, v in list(self.data.get('baseUriParameters', {}).items()):
            base_uri_params.append((URIParameter(k, v)))
        return base_uri_params or None

    @property
    @memoized
    def query_params(self):
        """
        Returns a list of ``QueryParameter`` objects of a Trait,
        or ``None`` if no query parameters are defined.
        """
        resource_params = self.data.get('queryParameters', {})

        query_params = []
        for k, v in list(resource_params.items()):
            query_params.append((QueryParameter(k, v)))
        return query_params or None

    @property
    @memoized
    def form_params(self):
        """
        Returns a list of FormParameter objects, or ``None`` if no form
        parameters are defined.
        """
        form_params = []
        for k, v in list(self.data.get('formParameters', {}).items()):
            form_params.append((FormParameter(k, v)))
        return form_params or None

    @property
    @memoized
    def req_mime_types(self):
        """
        Returns a list of strings referring to MIME types that the
        Trait supports, or ``None`` if none defined.
        """
        mime_types = self.data.get('body', {}).keys()

        return mime_types or None

    @property
    @memoized
    def description(self):
        """
        Returns ``DescriptiveContent`` object with ``raw`` and ``html``
        attributes, or ``None`` if not defined.

        Assumes raw content is written in plain text or Markdown in RAML
        per specification. (Optional)
        """
        resource_desc = self.data.get('description')
        if resource_desc:
            return DescriptiveContent(resource_desc)
        return None


class Trait(_BaseResourceProperties):
    """
    Method-level properties to apply to a Resource or ResourceType.
    """
    @property
    @memoized
    def usage(self):
        """
        Returns a string detailing how to use this trait.
        """
        return self.data.get('usage')

    def __repr__(self):
        return "<Trait(name='{0}')>".format(self.name)


class _BaseResource(_BaseResourceProperties):
    """
    Base class from which Resource and ResourceType inherit.  Based off
    of _BaseResourceProperties
    """
    def __init__(self, name, data, method, api):
        _BaseResourceProperties.__init__(self, name, data, api)
        self.method = method
        self._traits = None
        self._security_schemes = None

    @property
    @memoized
    def is_(self):
        """
        Returns a list of strings denoting traits assign to Resource or
        Resource Type, or ``None`` if not defined.

        Use ``resource.traits`` to get the actual ``Trait`` object.
        """
        try:
            method_traits = self.data.get(self.method, {}).get('is', [])
        except AttributeError:
            # self.method could exist, but return None
            method_traits = []

        resource_traits = self.data.get('is', [])
        return method_traits + resource_traits or None

    @property
    def traits(self):
        """
        Returns a list of ``Trait`` objects assigned to the Resource or
        ResourceType, if any.

        Use ``resource.is_`` to get a simple list of strings denoting the
        names of applicable traits.
        """
        return self._traits

    @traits.setter
    def traits(self, trait_objects):
        self._traits = trait_objects

    @property
    @memoized
    def secured_by(self):
        try:
            method_secured = self.data.get(self.method, {}).get('securedBy')
        except AttributeError:
            # self.method could exist, but return None
            method_secured = []
        resource_secured = self.data.get('securedBy')
        return method_secured or resource_secured or None

    @property
    def security_schemes(self):
        """
        Returns a list of ``SecurityScheme`` objects assigned to the Resource
        or ResourceType, or ``None`` if none assigned.

        Use ``resource.secured_by`` to get a simple list of strings denoting
        the names of applicable security schemes.
        """
        return self._security_schemes

    @security_schemes.setter
    def security_schemes(self, security_objs):
        self._security_schemes = security_objs

    @property
    @memoized
    def protocols(self):
        """
        Returns a list of supported protocols for the particular Resource or
        ResourceType.

        Overrides the root API's protocols.  Returns ``None`` if not defined.
        """
        try:
            method_protocols = self.data.get(self.method).get('protocols')
            if method_protocols:
                return method_protocols
        except AttributeError:
            # self.method could exist, but return None
            pass

        resource_protocols = self.data.get('protocols')
        if resource_protocols:
            return resource_protocols
        return None

    #####
    # Following properties extend those from _BaseResourceProperies
    #####

    @property
    @memoized
    def headers(self):
        """
        Returns a list of accepted Header objects for Resource or
        ResourceTypes, or  ``None`` if no headers defined.
        """
        try:
            method_headers = self.data.get(self.method, {}).get('headers', {})
        except AttributeError:
            # self.method could exist, but return None
            pass

        headers = super(_BaseResource, self).headers or []

        for k, v in list(method_headers.items()):
            headers.append(Header(k, v, self.method))
        return headers or None

    @property
    @memoized
    def body(self):
        """
        Returns a list of Body objects of a request for Resource or
        ResourceTypes, or ``None`` if none defined.
        """
        bodies = super(_BaseResource, self).body or []
        try:
            method_body = self.data.get(self.method, {}).get('body', {})
            for k, v in list(method_body.items()):
                bodies.append(Body(k, v))
        except AttributeError:
            # self.method could exist, but return None
            pass

        return bodies or None

    @property
    @memoized
    def responses(self):
        """
        Returns a list of Response objects of a Resource or ResourceType,
        or ``None`` if none defined.

        :raises RAMLParserError: Unsupported HTTP Response code
        """
        resps = super(_BaseResource, self).responses or []
        try:
            method_responses = self.data.get(self.method, {}).get(
                'responses', {})

            for k, v in list(method_responses.items()):
                if int(k) in HTTP_RESP_CODES:
                    resps.append(Response(k, v, self.method))
                else:
                    msg = "{0} not a supported HTTP Response code".format(k)
                    raise RAMLParserError(msg)
        except AttributeError:
            # self.method could exist, but return None
            pass

        return resps

    @property
    @memoized
    def uri_params(self):
        """
        Returns a list of ``URIParameter`` objects of a Resource or
        ResourceType, or ``None`` if none are defined.
        """
        uri_params = super(_BaseResource, self).uri_params or []
        try:
            method_params = self.data.get(self.method, {}).get(
                'uriParameters', {})
            for k, v in list(method_params.items()):
                uri_params.append((URIParameter(k, v)))
        except AttributeError:
            # self.method could exist, but return None
            pass

        return uri_params or None

    @property
    @memoized
    def base_uri_params(self):
        """
        Returns a list of base ``URIParameter`` objects of a Resource or
        ResourceType, or ``None`` if none are defined.
        """
        base_params = super(_BaseResource, self).base_uri_params or []
        try:
            method_params = self.data.get(self.method, {}).get(
                'baseUriParameters', {})
            for k, v in list(method_params.items()):
                base_params.append((URIParameter(k, v)))
        except AttributeError:
            # self.method could exist, but return None
            pass

        return base_params or None

    @property
    @memoized
    def query_params(self):
        """
        Returns a list of ``QueryParameter`` objects of a Resource or
        ResourceType, or ``None`` if no query parameters are defined.
        """
        query_params = super(_BaseResource, self).query_params or []
        try:
            method_params = self.data.get(self.method, {}).get(
                'queryParameters', {})
            for k, v in list(method_params.items()):
                query_params.append(QueryParameter(k, v))
        except AttributeError:
            # self.method could exist, but return None
            pass

        return query_params or None

    @property
    @memoized
    def form_params(self):
        """
        Returns a list of FormParameter objects of a Resource or
        ResourceType, or ``None`` if no form parameters are defined.
        """

        form_params = super(_BaseResource, self).form_params or []

        method_params = {}
        url_form = {}
        multipart = {}

        if self.method in ['post', 'delete', 'put', 'patch']:
            try:
                method_params = self.data.get(self.method, {}).get(
                    'formParameters', {})
                # TODO: will these show up outside of a method?
                url_form = self.data.get(self.method, {}).get('body').get(
                    'application/x-www-form-urlencoded', {}).get(
                    'formParameters', {})
                multipart = self.data.get(self.method, {}).get('body').get(
                    'multipart/form-data', {}).get('formParameters', {})
                items = dict(method_params.items() +
                             url_form.items() +
                             multipart.items())
                for k, v in list(items.items()):
                    form_params.append((FormParameter(k, v)))
            except AttributeError:
                # self.method could exist, but return None
                pass

        return form_params or None

    @property
    @memoized
    def req_mime_types(self):
        """
        Returns a list of strings referring to MIME types that the
        Resource or ResourceType supports, or ``None`` if none defined.
        """
        method_mime = []
        if self.method in ["post", "put", "delete", "patch"]:
            try:
                method_mime = self.data.get(self.method, {}).get(
                    'body', {}).keys()
            except AttributeError:
                # self.method could exist, but return None
                method_mime = []

        mime_types = self.data.get('body', {}).keys() + method_mime

        return mime_types or None

    @property
    @memoized
    def description(self):
        """
        Returns ``DescriptiveContent`` object with ``raw`` and ``html``
        attributes, or ``None`` if not defined.

        Assumes raw content is written in plain text or Markdown in RAML
        per specification.
        """
        try:
            method_desc = self.data.get(self.method, {}).get('description')
            if method_desc:
                return DescriptiveContent(method_desc)
        except AttributeError:
            # self.method could exist, but return None
            pass

        return super(_BaseResource, self).description


class ResourceType(_BaseResource):
    """
    Resource-level properties to apply to a Resource.
    """
    def __init__(self, name, data, method, api, type=None):
        _BaseResource.__init__(self, name, data, method, api)
        self.orig_method = method
        self.method = self._clean_method(method)
        self.type = type

    def _clean_method(self, method):
        if method.endswith("?"):
            return method[:-1]
        return method

    @property
    @memoized
    def usage(self):
        """
        Returns a string detailing how to use this ResourceType.
        """
        return self.data.get('usage')

    @property
    def optional(self):
        """
        Returns ``True`` if ``?`` in method, denoting that it is optional.
        """
        return "?" in self.orig_method

    def __repr__(self):
        return "<ResourceType(method='{0}', name='{1}')>".format(
            self.method.upper(), self.name)

    #####
    # Following properties extend those from _BaseResourceProperies
    #####
    @property
    @memoized
    def protocols(self):
        """
        Returns a list of supported protocols for the particular ResourceType.

        Overrides the root API's protocols.  Returns ``None`` if not defined.
        """
        try:
            opt_method_protocols = self.data.get(self.orig_method).get(
                'protocols')
            if opt_method_protocols:
                return opt_method_protocols
        except AttributeError:
            # self.method could exist, but return None
            pass

        protocols = super(ResourceType, self).protocols
        return protocols or None

    @property
    @memoized
    def headers(self):
        """
        Returns a list of accepted Header objects for ResourceType,
        or  ``None`` if no headers defined.
        """
        try:
            opt_method_headers = self.data.get(self.orig_method, {}).get(
                'headers', {})
        except AttributeError:
            # self.method could exist, but return None
            opt_method_headers = {}

        headers = super(ResourceType, self).headers or []
        for k, v in list(opt_method_headers.items()):
            headers.append(Header(k, v, self.method))
        return headers or None

    @property
    @memoized
    def body(self):
        """
        Returns a list of Body objects of a request for ResourceType,
        or ``None`` if none defined.
        """
        bodies = super(ResourceType, self).body or []
        try:
            opt_method_body = self.data.get(self.orig_method, {}).get(
                'body', {})
            for k, v in list(opt_method_body.items()):
                bodies.append(Body(k, v))

        except AttributeError:
             # self.method could exist, but return None
            pass

        return bodies or None

    @property
    @memoized
    def responses(self):
        """
        Returns a list of Response objects of a ResourceType, or ``None``
        if none are defined.

        :raises RAMLParserError: Unsupported HTTP Response code
        """
        resps = super(ResourceType, self).responses or []
        try:
            opt_method_resps = self.data.get(self.orig_method, {}).get(
                'responses', {})

            for k, v in list(opt_method_resps.items()):
                if int(k) in HTTP_RESP_CODES:
                    resps.append(Response(k, v, self.method))
                else:
                    msg = "{0} not a supported HTTP Response code".format(k)
                    raise RAMLParserError(msg)
        except AttributeError:
            # self.method could exist, but return None
            pass

        return resps

    @property
    @memoized
    def uri_params(self):
        """
        Returns a list of ``URIParameter`` objects of a ResourceType, or
        ``None`` if none are defined.
        """
        uri_params = super(ResourceType, self).uri_params or []
        try:
            orig_method_params = self.data.get(self.orig_method, {}).get(
                'uriParameters', {})
            for k, v in list(orig_method_params.items()):
                uri_params.append((URIParameter(k, v)))
        except AttributeError:
            # self.method could exist, but return None
            pass

        return uri_params or None

    @property
    @memoized
    def base_uri_params(self):
        """
        Returns a list of base ``URIParameter`` objects of a ResourceType,
        or ``None`` if none are defined.
        """
        base_params = super(ResourceType, self).base_uri_params or []
        try:
            opt_method_params = self.data.get(self.orig_method, {}).get(
                'baseUriParameters', {})
            for k, v in list(opt_method_params.items()):
                base_params.append((URIParameter(k, v)))
        except AttributeError:
            # self.method could exist, but return None
            pass

        return base_params or None

    @property
    @memoized
    def query_params(self):
        """
        Returns a list of ``QueryParameter`` objects of a ResourceType,
        or ``None`` if no query parameters are defined.
        """
        query_params = super(ResourceType, self).query_params or []
        try:
            opt_method_params = self.data.get(self.orig_method, {}).get(
                'queryParameters', {})
            for k, v in list(opt_method_params.items()):
                query_params.append(QueryParameter(k, v))
        except AttributeError:
            # self.method could exist, but return None
            pass
        return query_params or None

    @property
    @memoized
    def form_params(self):
        """
        Returns a list of FormParameter objects of a ResourceType,
        or ``None`` if no form parameters are defined.
        """
        form_params = super(ResourceType, self).form_params or []

        method_params = {}
        url_form = {}
        multipart = {}

        if self.orig_method in ['post?', 'delete?', 'put?', 'patch?']:
            try:
                method_params = self.data.get(self.orig_method, {}).get(
                    'formParameters', {})
                # TODO: will these show up outside of a method?
                url_form = self.data.get(self.orig_method, {}).get('body').get(
                    'application/x-www-form-urlencoded', {}).get(
                    'formParameters', {})
                multipart = self.data.get(self.orig_method, {}).get(
                    'body').get('multipart/form-data', {}).get(
                    'formParameters', {})

                items = dict(method_params.items() +
                             url_form.items() +
                             multipart.items())

                for k, v in list(items.items()):
                    form_params.append((FormParameter(k, v)))

            except AttributeError:
                # self.method could exist, but return None
                pass

        return form_params or None

    @property
    @memoized
    def req_mime_types(self):
        """
        Returns a list of strings referring to MIME types that the
        ResourceType supports, or ``None`` if none defined.
        """
        mime_types = super(ResourceType, self).req_mime_types or []
        opt_method_mime = []
        try:
            if self.orig_method in ["post?", "put?", "delete?", "patch?"]:
                opt_method_mime = self.data.get(self.orig_method, {}).get(
                    'body', {}).keys()
        except AttributeError:
            # self.method could exist, but return None
            pass

        return mime_types + opt_method_mime or None

    @property
    @memoized
    def description(self):
        """
        Returns ``DescriptiveContent`` object with ``raw`` and ``html``
        attributes, or ``None`` if not defined.

        Assumes raw content is written in plain text or Markdown in RAML
        per specification.
        """
        try:
            opt_method_desc = self.data.get(self.orig_method, {}).get(
                'description')
            if opt_method_desc:
                return DescriptiveContent(opt_method_desc)
        except AttributeError:
            # self.method could exist, but return None
            pass
        return super(ResourceType, self).description


class Resource(_BaseResource):
    """
    An object representing an endpoint defined in RAML, identified by a leading
    slash, ``/``.
    """
    def __init__(self, name, data, method, api, parent=None):
        _BaseResource.__init__(self, name, data, method, api)
        self.parent = parent
        self._resource_type = None

    @property
    @memoized
    def display_name(self):
        """
        Returns the Resource's display name.

        A friendly name used only for display or documentation purposes.

        If ``displayName`` is not specified in RAML, it defaults to ``name``.
        """
        return self.data.get('displayName', self.name)

    def _get_path_to(self, node):
        parent_path = ''
        if node.parent:
            parent_path = self._get_path_to(node.parent)
        return parent_path + node.name

    @property
    @memoized
    def path(self):
        """
        Returns a string of the URI path of Resource relative to
        ``api.base_uri``.

        Not explicitly defined in RAML but inferred based off of
        the Resource ``name``.
        """
        return self._get_path_to(self)

    @property
    @memoized
    def absolute_uri(self):
        """
        Returns a string of the absolute URI path of Resource.

        Not explicitly defined in RAML but inferred based off of
        ``path`` and the API root's ``base_uri``.
        """
        return self.api.base_uri + self.path

    @property
    def resource_type(self):
        """
        Returns a list of ResourceType objects assigned to the Resource.

        Use ``resource.type`` to get the string name representation of the
        ResourceType applied.

        :raises RAMLParserError: Too many resource types applied to one
            resource.
        :raises RAMLParserError: Resource not defined in the API Root.
        :raises RAMLParserError: If resource type is something other
            than a ``str`` or ``dict``.
        """
        return self._resource_type

    @resource_type.setter
    def resource_type(self, resource_type_objs):
        self._resource_type = resource_type_objs

    @property
    @memoized
    def type(self):
        """
        Returns a string of the ``type`` associated with the corresponding
        ResourceTypes, or a dictionary where the (single) key is the name
        of the mapped ResourceType, and the values are the parameters
        associated with it.

        Use ``resource.resource_type`` to get the actual ResourceType object.
        """
        resource_type = self.data.get('type')
        if not resource_type and self.parent:
            return self.parent.type
        return resource_type

    @property
    @memoized
    def protocols(self):
        """
        Returns a list of supported protocols for the particular ResourceType.

        Overrides the root API's protocols.  Returns ``None`` if not defined.
        """
        protocols = super(Resource, self).protocols
        if protocols:
            return protocols

        if self.resource_type:
            return self.resource_type.protocols

        return None

    @property
    @memoized
    def headers(self):
        """
        Returns a list of accepted Header objects for Resource,
        or  ``None`` if no headers defined.
        """
        # TODO: does resource inherit headers from its parent?
        headers = []
        if self.resource_type:
            headers.extend(self.resource_type.headers or [])
        if self.traits:
            for t in self.traits:
                headers.extend(t.headers or [])
        _headers = super(Resource, self).headers or []
        return headers + _headers or None

    @property
    @memoized
    def responses(self):
        """
        Returns a list of Response objects of a Resource, or ``None``
        if none are defined.

        :raises RAMLParserError: Unsupported HTTP Response code
        """
        # TODO: does resource inherit responses from its parent?
        resp = []
        if self.resource_type:
            resp.extend(self.resource_type.responses or [])
        if self.traits:
            for t in self.traits:
                resp.extend(t.responses or [])
        _resp = super(Resource, self).responses or []
        return resp + _resp or None

    @property
    @memoized
    def body(self):
        """
        Returns a list of Body objects of a request for Resource,
        or ``None`` if none defined.
        """
        # TODO: does resource inherit body from its parent?
        body = []
        if self.resource_type:
            body.extend(self.resource_type.body or [])
        if self.traits:
            for t in self.traits:
                body.extend(t.body or [])
        _body = super(Resource, self).body or []
        return body + _body or None

    @property
    @memoized
    def query_params(self):
        """
        Returns a list of ``QueryParameter`` objects of a Resource,
        or ``None`` if no query parameters are defined.
        """
        params = []
        if self.resource_type:
            params.extend(self.resource_type.query_params or [])
        if self.traits:
            for t in self.traits:
                params.extend(t.query_params or [])
        _params = super(Resource, self).query_params or []
        return params + _params or None

    @property
    @memoized
    def uri_params(self):
        """
        Returns a list of ``URIParameter`` objects of a Resource, or
        ``None`` if none are defined.
        """
        params = []
        if self.resource_type:
            params.extend(self.resource_type.uri_params or [])
        if self.traits:
            for t in self.traits:
                params.extend(t.uri_params or [])
        if self.parent:
            params.extend(self.parent.uri_params or [])
        _params = super(Resource, self).uri_params or []
        return params + _params or None

    @property
    @memoized
    def base_uri_params(self):
        """
        Returns a list of base ``URIParameter`` objects of a Resource,
        or ``None`` if none are defined.
        """
        params = []
        if self.resource_type:
            params.extend(self.resource_type.base_uri_params or [])
        if self.traits:
            for t in self.traits:
                params.extend(t.base_uri_params or [])
        if self.parent:
            params.extend(self.parent.base_uri_params or [])
        _params = super(Resource, self).base_uri_params or []
        return params + _params or None

    @property
    @memoized
    def form_params(self):
        """
        Returns a list of FormParameter objects of a Resource,
        or ``None`` if no form parameters are defined.
        """
        params = []
        if self.resource_type:
            params.extend(self.resource_type.form_params or [])
        if self.traits:
            for t in self.traits:
                params.extend(t.form_params or [])
        _params = super(Resource, self).form_params or []
        return params + _params or None

    # @property
    # @memoized
    # def traits(self):
    #     traits = []
    #     if self.resource_type:
    #         traits.extend(self.resource_type.traits or [])
    #     if self.parent:
    #         traits.extend(self.parent.traits or [])
    #     _traits = super(Resource, self).traits or []
    #     return traits + _traits or None

    @property
    @memoized
    def description(self):
        """
        Returns ``DescriptiveContent`` object with ``raw`` and ``html``
        attributes, or ``None`` if not defined.

        Assumes raw content is written in plain text or Markdown in RAML
        per specification.
        """
        if super(Resource, self).description is not None:
            return super(Resource, self).description
        elif self.resource_type and self.resource_type.description:
            desc = fill_reserved_params(self,
                                        self.resource_type.description.raw)
            return DescriptiveContent(desc)
        elif self.parent:
            return self.parent.description
        return None

    def __repr__(self):
        return "<Resource(method='{0}', path='{1}')>".format(
            self.method.upper(), self.path)
