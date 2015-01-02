# ! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function

__all__ = ["RAMLRoot", "Trait", "ResourceType", "Resource", "RAMLParserError"]

from six.moves import BaseHTTPServer as httpserver


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
        self.__version = None
        self.__base_uri = None
        self.__base_uri_params = None
        self.__uri_params = None
        self.__protocols = None
        self.__title = None
        self.__docs = None
        self.__schemas = None
        self.__resources = None
        self.__resource_types = None
        self.__traits = None
        self.__media_type = None
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
        return self.__title

    @title.setter
    def title(self, title):
        self.__title = title

    @property
    def version(self):
        """
        The API's version.

        :returns: API Version
        :rtype: string
        """
        return self.__version

    @version.setter
    def version(self, version):
        self.__version = version

    @property
    def protocols(self):
        """
        Supported protocols of the API.  If not set, then inferred from \
        :py:obj:`.base_uri`.

        :returns: supported protocols (`HTTP`, `HTTPS`)
        :rtype: string
        """
        return self.__protocols

    @protocols.setter
    def protocols(self, protos):
        self.__protocols = protos

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
        return self.__base_uri

    @base_uri.setter
    def base_uri(self, base_uri):
        self.__base_uri = base_uri

    @property
    def uri_params(self):
        """
        URI Parameters available for the baseUri and all resources/endpoints.

        :rtype: ``list`` of :py:class:`.parameters.URIParameter` objects, \
            or ``None``.
        :raises RAMLParserError: if :py:obj:`.version` is defined \
            (:py:obj:`.version` can only be used in \
             :py:obj:`.base_uri_parameters`).
        """
        return self.__uri_params

    @uri_params.setter
    def uri_params(self, uri_params):
        self.__uri_params = uri_params

    @property
    def base_uri_params(self):
        """
        Returns URI Parameters for meant specifically for :py:obj:`.base_uri`.

        :rtype: ``list`` of :py:class:`.parameters.URIParameter` objects, \
            or ``None``.
        """
        return self.__base_uri_params

    @base_uri_params.setter
    def base_uri_params(self, base_uri_params):
        self.__base_uri_params = base_uri_params

    @property
    def media_type(self):
        """
        Returns the default supported MIME Media Type of the API.  \
        Returns ``None`` if no media types are defined.

        Valid media types:

            * ``text/yaml``, ``text/x-yaml``, ``application/yaml``, \
                ``application/x-yaml``
            * Any defined by the \
                `IANA <http://www.iana.org/assignments/media-types>`_
            * A custom type that follows the regex: \
                ``application\/[A-Za-z.-0-1]*+?(json|xml)``

        :rtype: string
        """
        return self.__media_type

    @media_type.setter
    def media_type(self, media_type):
        self.__media_type = media_type

    @property
    def documentation(self):
        """
        API documentation

        :rtype: ``list`` of :py:class:`.parameters.Documentation` objects, \
            or ``None``.
        :raises RAMLParserError: if can not parse documentation.
        """
        return self.__docs

    @documentation.setter
    def documentation(self, docs):
        self.__docs = docs

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
        return self.__schemas

    @schemas.setter
    def schemas(self, schemas):
        self.__schemas = schemas

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
        self._headers = None
        self._body = None
        self._responses = None
        self._uri_params = None
        self._base_uri_params = None
        self._query_params = None
        self._form_params = None
        self._media_types = None
        self._description = None

    @property
    def headers(self):
        """
        Accepted headers for the Resource or Resource Type.

        :rtype: ``list`` of :py:class:`.parameters.Header` objects, \
            or ``None``.
        """
        return self._headers

    @headers.setter
    def headers(self, header_objs):
        self._headers = header_objs

    @property
    def body(self):
        """
        Accepted body for the Resource or Resource Type.

        :rtype: ``list`` of :py:class:`.parameters.Body` objects, or ``None``.
        """
        return self._body

    @body.setter
    def body(self, body_objs):
        self._body = body_objs

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
        return self._responses

    @responses.setter
    def responses(self, resp_objs):
        self._responses = resp_objs

    @property
    def uri_params(self):
        """
        Accepted URI parameters for the Resource or Resource Type.

        :rtype: ``list`` of :py:class:`.parameters.URIParameter` objects, \
            or ``None``.
        """
        return self._uri_params

    @uri_params.setter
    def uri_params(self, uri_objs):
        self._uri_params = uri_objs

    @property
    def base_uri_params(self):
        """
        Accepted base URI parameters for the Resource or Resource Type.

        :rtype: ``list`` of :py:class:`.parameters.URIParameter` objects, \
            or ``None``.
        """
        return self._base_uri_params

    @base_uri_params.setter
    def base_uri_params(self, base_uri_objs):
        self._base_uri_params = base_uri_objs

    @property
    def query_params(self):
        """
        Accepted query parameters for the Resource or Resource Type.

        :rtype: ``list`` of :py:class:`.parameters.QueryParameter` objects, \
            or ``None``.
        """
        return self._query_params

    @query_params.setter
    def query_params(self, query_objs):
        self._query_params = query_objs

    @property
    def form_params(self):
        """
        Accepted form parameters for the Resource or Resource Type.

        :rtype: ``list`` of :py:class:`.parameters.FormParameter` objects, \
            or ``None``.
        """
        return self._form_params

    @form_params.setter
    def form_params(self, form_objs):
        self._form_params = form_objs

    @property
    def media_types(self):
        return self._media_types

    @media_types.setter
    def media_types(self, media_types):
        self._media_types = media_types

    @property
    def description(self):
        """
        Defined description of the Resource or Resource Type.

        :rtype: ``list`` of :py:class:`.parameters.Content` objects, \
            or ``None``
        """
        return self._description

    @description.setter
    def description(self, desc_obj):
        self._description = desc_obj


class Trait(_BaseResourceProperties):
    """
    Method-level properties to apply to a Resource or ResourceType.
    """
    def __init__(self, name, data, api):
        _BaseResourceProperties.__init__(self, name, data, api)
        self._usage = None

    @property
    def usage(self):
        """
        Returns a string detailing how to use this trait.

        :rtype: ``string``
        """
        return self._usage

    @usage.setter
    def usage(self, usage):
        self._usage = usage

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
        self._protocols = None

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
        return self._protocols

    @protocols.setter
    def protocols(self, protocols):
        self._protocols = protocols


class ResourceType(_BaseResource):
    """
    Resource-level properties to apply to a Resource.
    """
    def __init__(self, name, data, method, api, type=None):
        _BaseResource.__init__(self, name, data, method, api)
        self.orig_method = method
        self.method = self._clean_method(method)
        self.type = type
        self._usage = None

    def _clean_method(self, method):
        if method.endswith("?"):
            return method[:-1]
        return method

    @property
    def usage(self):
        """
        Returns a string detailing how to use this ResourceType.
        """
        return self._usage

    @usage.setter
    def usage(self, usage):
        self._usage = usage

    @property
    def optional(self):
        """
        Returns ``True`` if ``?`` in method, denoting that the method \
        definition is optional when applied to a :py:class:`.Resource`.
        """
        return "?" in self.orig_method

    def __repr__(self):
        return "<ResourceType(method='{0}', name='{1}')>".format(
            self.method.upper(), self.name)


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
        self._display_name = None
        self._resource_type = None
        self._type = None

    @property
    def display_name(self):
        """
        The friendly name used only for display or documentation purposes.

        If ``displayName`` is not specified in RAML, it defaults to ``name``.

        :rtype: ``str``
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        self._display_name = display_name

    def __get_path(self, node):
        parent_path = ''
        if node.parent:
            parent_path = self.__get_path(node.parent)
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
        return self.__get_path(self)

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
        return self._type

    @type.setter
    def type(self, type):
        self._type = type

    def __repr__(self):
        return "<Resource(method='{0}', path='{1}')>".format(
            self.method.upper(), self.path)
