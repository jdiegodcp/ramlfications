# ! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function

__all__ = ["RAMLRoot", "Trait", "ResourceType", "Resource", "RAMLParserError"]

import re


from six.moves import BaseHTTPServer as httpserver

from .parameters import (
    FormParameter, URIParameter, QueryParameter,
    Header, Response, Body,
    Documentation, Content
)
from .utils import fill_reserved_params

HTTP_RESP_CODES = httpserver.BaseHTTPRequestHandler.responses.keys()
AVAILABLE_METHODS = ['get', 'post', 'put', 'delete', 'patch', 'head',
                     'options', 'trace', 'connect']


class RAMLParserError(Exception):
    pass


class RAMLRoot(object):
    """
    Parsed RAML object.
    """
    def __init__(self, raml_obj):
        """
        :param loader.RAMLDict raml_obj: Loaded RAML file
        """
        self.raml = raml_obj.data
        self.raml_file = raml_obj.raml_file
        self.__resources = None
        self.__resource_types = None
        self.__traits = None
        self.__security_schemes = None

    @property
    def resources(self):
        """
        Resources (endpoints) that the API supports.

        :return: resources
        :rtype: ``list`` of :py:class:`Resource` objects
        """
        return self.__resources

    @resources.setter
    def resources(self, resource_objs):
        self.__resources = resource_objs

    @property
    def resource_types(self):
        """
        Resource Types that the API has defined, if any.

        :return: resource types
        :rtype: ``list`` of :py:class:`.ResourceType`, or ``None``
        """
        return self.__resource_types

    @resource_types.setter
    def resource_types(self, resource_type_objs):
        self.__resource_types = resource_type_objs

    @property
    def traits(self):
        """
        API-supported traits, if any.

        :returns: Traits
        :rtype: ``list`` of :py:class:`.Trait` objects, or ``None``
        """
        return self.__traits

    @traits.setter
    def traits(self, trait_objs):
        self.__traits = trait_objs

    @property
    def security_schemes(self):
        """
        Security schemes that the API supports, if any.

        :rtype: ``list`` of :py:class:`.parameters.SecurityScheme` objects, \
        or ``None``.
        """
        return self.__security_schemes

    @security_schemes.setter
    def security_schemes(self, sec_objs):
        self.__security_schemes = sec_objs

    @property
    def title(self):
        """
        Title element defined in the root section of the RAML API definition.

        :returns: API Title
        :rtype: string
        """
        return self.raml.get('title')

    @property
    def version(self):
        """
        The API's version.

        :returns: API Version
        :rtype: string
        """
        return self.raml.get('version')

    @property
    def protocols(self):
        """
        Supported protocols of the API.  If not set, then inferred from \
        :py:obj:`.base_uri`.

        :returns: supported protocols (`HTTP`, `HTTPS`)
        :rtype: string
        """
        protocol = re.findall(r"(https|http)", self.base_uri)
        return self.raml.get('protocols', protocol)

    @property
    def base_uri(self):
        """
        Returns the base URI of API.

        .. note::
            ``base_uri`` is optional during development, required after \
            implementation.

        :raises RAMLParserError: if no ``version`` is defined but is \
            referenced in the :py:obj:`.base_uri` parameter.
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
    def uri_parameters(self):
        """
        URI Parameters available for the baseUri and all resources/endpoints.

        :rtype: ``list`` of :py:class:`.parameters.URIParameter` objects, \
            or ``None``.
        :raises RAMLParserError: if :py:obj:`.version` is defined \
            (:py:obj:`.version` can only be used in \
             :py:obj:`.base_uri_parameters`).
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
        Returns URI Parameters for meant specifically for :py:obj:`.base_uri`.

        :rtype: ``list`` of :py:class:`.parameters.URIParameter` objects, \
            or ``None``.
        """
        base_uri_params = self.raml.get('baseUriParameters', {})
        uri_params = []
        for k, v in list(base_uri_params.items()):
            uri_params.append((URIParameter(k, v)))
        return uri_params or None

    @property
    def media_type(self):
        # TODO: raise an error if not acceptable media type given
        """
        Returns the supported Media Type of the API.  Returns ``None``
        if no media types are defined.

        Valid media types:

            * ``text/yaml``, ``text/x-yaml``, ``application/yaml``, \
                ``application/x-yaml``
            * Any defined by the \
                `IANA <http://www.iana.org/assignments/media-types>`_
            * A custom type that follows the regex: \
                ``application\/[A-Za-z.-0-1]*+?(json|xml)``

        :rtype: string
        """
        return self.raml.get('mediaType')

    @property
    def documentation(self):
        """
        API documentation

        :rtype: ``list`` of :py:class:`.parameters.Documentation` objects, \
            or ``None``.
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
    def schemas(self):
        """
        Returns a dictionary of user-defined schemas that may be applied \
        anywhere in the API definition.

        .. note::
            Current explicit supported types are XML, JSON, YAML. Other \
            schema definitions may work at your own risk.

        :rtype: ``dict``
        """
        return self.raml.get('schemas')

    def __repr__(self):
        return '<RAMLRoot(raml_file="{0}")>'.format(self.raml_file)


class _BaseResourceProperties(object):
    """
    Base class from which Trait and _BaseResource inherit.
    """
    def __init__(self, name, data, api):
        """
        :param str name: Name of Trait
        :param dict data: Data associated with Trait
        :param RAMLRoot api: API with which the Trait is associated
        """
        self.name = name
        self.data = data
        self.api = api

    @property
    def headers(self):
        """
        Accepted headers for trait.

        :rtype: ``list`` of :py:class:`.parameters.Header` objects, \
            or ``None``.
        """
        resource_headers = self.data.get('headers', {})
        headers = []
        for k, v in list(resource_headers.items()):
            headers.append(Header(k, v))
        return headers or None

    @property
    def body(self):
        """
        Accepted body for trait.

        :rtype: ``list`` of :py:class:`.parameters.Body` objects, or ``None``.
        """
        bodies = []
        resource_body = self.data.get('body', {})
        for k, v in list(resource_body.items()):
            bodies.append(Body(k, v))
        return bodies or None

    @property
    def responses(self):
        """
        Accepted responses for trait.

        .. note::
             Currently only supports HTTP/1.1-defined responses.

        :rtype: ``list`` of :py:class:`.parameters.Response` objects, \
            or ``None``.
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
    def uri_params(self):
        """
        Accepted URI parameters for trait.

        :rtype: ``list`` of :py:class:`.parameters.URIParameter` objects, \
            or ``None``.
        """
        uri_params = []
        for k, v in list(self.data.get('uriParameters', {}).items()):
            uri_params.append((URIParameter(k, v)))

        return uri_params or None

    @property
    def base_uri_params(self):
        """
        Accepted base URI parameters for trait.

        :rtype: ``list`` of :py:class:`.parameters.URIParameter` objects, \
            or ``None``.
        """
        base_uri_params = []
        for k, v in list(self.data.get('baseUriParameters', {}).items()):
            base_uri_params.append((URIParameter(k, v)))
        return base_uri_params or None

    @property
    def query_params(self):
        """
        Accepted query parameters for trait.

        :rtype: ``list`` of :py:class:`.parameters.QueryParameter` objects, \
            or ``None``.
        """
        resource_params = self.data.get('queryParameters', {})

        query_params = []
        for k, v in list(resource_params.items()):
            query_params.append((QueryParameter(k, v)))
        return query_params or None

    @property
    def form_params(self):
        """
        Accepted form parameters for trait.

        :rtype: ``list`` of :py:class:`.parameters.FormParameter` objects, \
            or ``None``.
        """
        form_params = []
        for k, v in list(self.data.get('formParameters', {}).items()):
            form_params.append((FormParameter(k, v)))
        return form_params or None

    @property
    def req_mime_types(self):
        """
        Supported MIME media types for trait.

        :rtype: ``list`` of ``str`` s or ``None``.
        """
        mime_types = self.data.get('body', {}).keys()

        return mime_types or None

    @property
    def description(self):
        """
        Description of trait.

        .. note::
            Assumes raw content is written in plain text or Markdown in RAML \
            per specification.

        :rtype: ``list`` of :py:class:`.parameters.Content` objects, \
        or ``None``.
        """
        resource_desc = self.data.get('description')
        if resource_desc:
            return Content(resource_desc)
        return None


class Trait(_BaseResourceProperties):
    """
    Method-level properties to apply to a Resource or ResourceType.
    """
    @property
    def usage(self):
        """
        Returns a string detailing how to use this trait.

        :rtype: ``string``
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
        """
        :param str name: Name of Resource Type
        :param dict data: Data associated with Resource Type
        :param str method: HTTP Method associated with Resource Type
        :param RAMLRoot api: API with which the Resource Type is associated
        :param str type: Another ResourceType from which it inherits, if any
        """
        _BaseResourceProperties.__init__(self, name, data, api)
        self.method = method
        self._traits = None
        self._security_schemes = None

    @property
    def is_(self):
        """
        Trait(s) assigned to particular :py:class:`Resource` or \
            :py:class:`ResourceType` object

        Use ``resource.traits`` or ``resource_type.traits`` to access actual \
        :py:class:`.Trait` object(s), if any.

        :rtype: ``list`` of ``str`` s referring to Trait names, or ``None``.
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
        :py:class:`.Trait` objects assigned to particular resource or \
            resource type.

        Use ``resource.is_`` or ``resource_type.is_`` to get a simple list of \
        strings denoting the names of applicable traits.

        :rtype: ``list`` of :py:class:`.Trait` objects, or ``None``
        """
        return self._traits

    @traits.setter
    def traits(self, trait_objects):
        self._traits = trait_objects

    @property
    def secured_by(self):
        """
        Security Scheme(s) assigned to particular :py:class:`Resource` or
        :py:class:`ResourceType` object.

        Use ``resource.security_schemes`` or \
        ``resource_type.security_schemes`` to access actual \
        :py:class:`.parameters.SecurityScheme` object(s), if any.

        :rtype: ``list`` of ``str`` s referring to Security Scheme names, \
            or ``None``.
        """
        try:
            if self.data.get(self.method, {}).get('securedBy'):
                return self.data.get(self.method, {}).get('securedBy')
        except AttributeError:
            # self.method could exist, but return None
            pass

        if self.data.get('securedBy'):
            return self.data.get('securedBy')

        if hasattr(self, 'parent'):
            if self.parent and self.parent.secured_by:
                return self.parent.secured_by
        return None

    @property
    def security_schemes(self):
        """
        Returns a list of ``SecurityScheme`` objects assigned to the Resource \
        or ResourceType, or ``None`` if none assigned.

        Use ``resource.secured_by`` to get a simple list of strings denoting \
        the names of applicable security schemes.

        :rtype: ``list`` of :py:class:`.parameters.SecurityScheme` objects, \
            or ``None.
        """
        return self._security_schemes

    @security_schemes.setter
    def security_schemes(self, security_objs):
        self._security_schemes = security_objs

    @property
    def protocols(self):
        """
        Returns a list of supported protocols for the particular Resource or
        ResourceType.

        Overrides the root API's protocols if defined.

        :rtype: ``list`` of ``str`` s
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
        else:
            return self.api.protocols

    #####
    # Following properties extend those from _BaseResourceProperies
    #####

    @property
    def headers(self):
        """
        Accepted headers for the Resource or Resource Type.

        :rtype: ``list`` of :py:class:`.parameters.Header` objects, \
            or ``None``.
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
    def body(self):
        """
        Accepted body for the Resource or Resource Type.

        :rtype: ``list`` of :py:class:`.parameters.Body` objects, or ``None``.
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
    def responses(self):
        """
        Accepted responses for the Resource or Resource Type.

        .. note::
            Currently only supports HTTP/1.1-defined responses

        :rtype: ``list`` of :py:class:`.parameters.Response` objects, \
            or ``None``.
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
    def uri_params(self):
        """
        Accepted URI parameters for the Resource or Resource Type.

        :rtype: ``list`` of :py:class:`.parameters.URIParameter` objects, \
            or ``None``.
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
    def base_uri_params(self):
        """
        Accepted base URI parameters for the Resource or Resource Type.

        :rtype: ``list`` of :py:class:`.parameters.URIParameter` objects, \
            or ``None``.
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
    def query_params(self):
        """
        Accepted query parameters for the Resource or Resource Type.

        :rtype: ``list`` of :py:class:`.parameters.QueryParameter` objects, \
            or ``None``.
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
    def form_params(self):
        """
        Accepted form parameters for the Resource or Resource Type.

        :rtype: ``list`` of :py:class:`.parameters.FormParameter` objects, \
            or ``None``.
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
    def req_mime_types(self):
        """
        Accepted MIME media types for the Resource or Resource Type.

        :rtype: ``list`` of ``str`` s, or ``None``.
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

        return mime_types or self.api.media_type

    @property
    def description(self):
        """
        Defined description of the Resource or Resource Type.

        :rtype: ``list`` of :py:class:`.parameters.Content` objects, \
            or ``None``
        """
        try:
            method_desc = self.data.get(self.method, {}).get('description')
            if method_desc:
                return Content(method_desc)
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
    def headers(self):
        """
        Accepted headers for the Resource Type.

        :rtype: ``list`` of :py:class:`.parameters.Header` objects, \
            or ``None``.
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
    def body(self):
        """
        Accepted body for the Resource Type.

        :rtype: ``list`` of :py:class:`.parameters.Body` objects, or ``None``.
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
    def responses(self):
        """
        Accepted responses for the Resource Type.

        .. note::
            Currently only supports HTTP/1.1-defined responses

        :rtype: ``list`` of :py:class:`.parameters.Response` objects, \
            or ``None``.
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
    def uri_params(self):
        """
        Accepted URI parameters for the Resource Type.

        :rtype: ``list`` of :py:class:`.parameters.Body` objects, or ``None``.
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
    def base_uri_params(self):
        """
        Accepted base URI parameters for the Resource Type.

        :rtype: ``list`` of :py:class:`.parameters.Body` objects, or ``None``.
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
    def query_params(self):
        """
        Accepted query parameters for the Resource Type.

        :rtype: ``list`` of :py:class:`.parameters.QueryParameter` objects, \
            or ``None``.
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
    def form_params(self):
        """
        Accepted form parameters for the Resource Type.

        :rtype: ``list`` of :py:class:`.parameters.FormParameter` objects, \
            or ``None``.
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
    def req_mime_types(self):
        """
        Accepted MIME media types for the Resource Type.

        :rtype: ``list`` of ``str`` s, or ``None``.
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
    def description(self):
        """
        Description of Resource Type.

        :rtype: ``list`` of :py:class:`.parameters.Content` objects, \
            or ``None``.
        """
        try:
            opt_method_desc = self.data.get(self.orig_method, {}).get(
                'description')
            if opt_method_desc:
                return Content(opt_method_desc)
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
        """
        :param str name: Name of Resource
        :param dict data: Data associated with Resource
        :param str method: HTTP method associated with Resource
        :param RAMLRoot api: API with which the Resource is associated
        :param Resource parent: Parent of Resource, if any
        """
        _BaseResource.__init__(self, name, data, method, api)
        self.parent = parent
        self._resource_type = None

    @property
    def display_name(self):
        """
        The friendly name used only for display or documentation purposes.

        If ``displayName`` is not specified in RAML, it defaults to ``name``.

        :rtype: ``str``
        """
        return self.data.get('displayName', self.name)

    def _get_path_to(self, node):
        parent_path = ''
        if node.parent:
            parent_path = self._get_path_to(node.parent)
        return parent_path + node.name

    @property
    def path(self):
        """
        Returns a string of the URI path of Resource relative to \
        :py:class:`RAMLRoot.base_uri`.

        .. note::
            Not explicitly defined in RAML but inferred based off of \
            the Resource ``name`` and its ``parent`` if any.

        :rtype: ``str``
        """
        return self._get_path_to(self)

    @property
    def absolute_uri(self):
        """
        Returns a string of the absolute URI path of Resource.

        .. note::
            Not explicitly defined in RAML but inferred based off of \
            :py:obj:`.path` and :py:class:`.RAMLRoot.base_uri`.

        :rtype: ``str``
        """
        return self.api.base_uri + self.path

    @property
    def resource_type(self):
        """
        Returns a list of ResourceType objects assigned to the Resource.

        Use ``resource.type`` to get the string name representation of the
        ResourceType applied.

        :rtype: ``list`` of :py:class:`.ResourceType` objects
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
    def type(self):
        """
        Returns a string of the ``type`` associated with the corresponding
        ResourceTypes, or a dictionary where the (single) key is the name
        of the mapped ResourceType, and the values are the parameters
        associated with it.

        Use ``resource.resource_type`` to get the actual ResourceType object.

        :rtype: ``str``, ``dict``, or ``None``
        """
        resource_type = self.data.get('type')
        if not resource_type and self.parent:
            return self.parent.type
        return resource_type

    @property
    def protocols(self):
        """
        Returns a list of supported protocols for the particular ResourceType.

        Overrides the root API's protocols.  Defaults to the API's definition \
        if Resource-level protocol(s) is not defined.

        :rtype: ``list`` of ``str`` s
        """
        protocols = super(Resource, self).protocols
        if protocols:
            return protocols

        if self.resource_type:
            return self.resource_type.protocols
        return self.api.protocols

    @property
    def headers(self):
        """
        Accepted headers for the Resource.

        :rtype: ``list`` of :py:class:`.parameters.Header` objects, \
            or ``None``.
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
    def responses(self):
        """
        Accepted response for the Resource.

        .. note::
            Currently only supports HTTP/1.1-defined responses

        :rtype: ``list`` of :py:class:`.parameters.Response` objects, \
            or ``None``.
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
    def body(self):
        """
        Accepted body for the Resource.

        :rtype: ``list`` of :py:class:`.parameters.Body` objects, or ``None``.
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
    def query_params(self):
        """
        Accepted query parameters for the Resource.

        :rtype: ``list`` of :py:class:`.parameters.QueryParameter` objects, \
            or ``None``.
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
    def uri_params(self):
        """
        Accepted URI parameters for the Resource.

        :rtype: ``list`` of :py:class:`.parameters.URIParameter` objects, \
            or ``None``.
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
    def base_uri_params(self):
        """
        Accepted base URI parameters for the Resource.

        :rtype: ``list`` of :py:class:`.parameters.URIParameter` objects, \
            or ``None``.
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
    def form_params(self):
        """
        Accepted form parameters for the Resource.

        :rtype: ``list`` of :py:class:`.parameters.FormParameter` objects, \
            or ``None``.
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
    # def traits(self):
    #     traits = []
    #     if self.resource_type:
    #         traits.extend(self.resource_type.traits or [])
    #     if self.parent:
    #         traits.extend(self.parent.traits or [])
    #     _traits = super(Resource, self).traits or []
    #     return traits + _traits or None

    @property
    def description(self):
        """
        Description of the Resource.

        :rtype: ``list`` of :py:class:`.parameters.Content` objects, \
        or ``None``.
        """
        if super(Resource, self).description is not None:
            return super(Resource, self).description
        elif self.resource_type and self.resource_type.description:
            desc = fill_reserved_params(self,
                                        self.resource_type.description.raw)
            return Content(desc)
        elif self.parent:
            return self.parent.description
        return None

    def __repr__(self):
        return "<Resource(method='{0}', path='{1}')>".format(
            self.method.upper(), self.path)
