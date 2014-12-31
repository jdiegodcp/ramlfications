#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function

import markdown2 as markdown

HTTP_METHODS = [
    "get", "post", "put", "delete", "patch", "options",
    "head", "trace", "connect"
]


# TODO: is this object really needed?
class ContentType(object):
    """
    Supported Content Type of a resource (e.g. ``application/json``).

    :param str name: The name of content type
    :param dict schema: Schema definition of content type
    :param str example: Example usage of content type
    """
    def __init__(self, name, schema, example):
        # Input validation would be nice here.
        # LR: Will do, but will add it to validate.py
        self.name = name
        self.schema = schema
        self.example = example

    def __repr__(self):
        return "<ContentType(name='{0}')>".format(self.name)


# NOTE: this is a class for extensibility, e.g. adding RTF support or whatevs
class Content(object):
    """
    Returns documentable content from the RAML file (e.g. Documentation
    content, description) in either raw or parsed form.
    """
    def __init__(self, data):
        """
        :param str data: The raw/marked up content
        """
        self.data = data

    @property
    def raw(self):
        """
        Helper method to return raw Markdown/plain text written in RAML file.
        """
        return self.data

    @property
    def html(self):
        """
        Returns text parsed from Markdown into HTML.
        """
        try:
            return markdown.markdown(self.data)
        except TypeError:
            return None

    def __repr__(self):
        return self.raw


class String(object):
    """
    Primative String type
    """
    def __init__(self, name, data):
        """
        :param str name: Name of parameter
        :param dict data: Data associated with parameter
        """
        self.name = name
        self.data = data

    @property
    def enum(self):
        """
        Returns the ``enum`` attribute, if any, that provides an \
        enumeration of the :py:class:`.String` parameter's valid values.

        :returns: enum
        :rtype: ``list`` of ``str`` s, or ``None``
        """
        return self.data.get('enum')

    @property
    def pattern(self):
        """
        Returns the pattern attribute, if any, that is a regular expression
        that the :py:class:.`String` parameter MUST match.

        :returns: regex pattern
        :rtype: ``str``, or ``None``
        """
        return self.data.get('pattern')

    @property
    def min_length(self):
        """
        Returns the minimum number of characters of the :py:class:`.String` \
        parameter as defined in the API specification.

        :returns: Minimum number of allowed characters
        :rtype: ``int``, or ``None``
        """
        return self.data.get('min_length')

    @property
    def max_length(self):
        """
        Returns the maximum number of characters of the :py:class:`.String` \
        parameter as defined in the API specification.

        :returns: Maximum number of allowed characters
        :rtype: ``int``, or ``None``
        """
        return self.data.get('maxLength')

    def __repr__(self):
        return "<String(name='{0}')>".format(self.name)


class IntegerNumber(object):
    """
    Primative Integer or Number Parameter Type
    """
    def __init__(self, name, data):
        """
        :param str name: Name of parameter
        :param dict data: Data associated with parameter
        """
        self.name = name
        self.data = data

    @property
    def minimum(self):
        """
        Returns the minimum value of the :py:class:`.IntegerNumber` \
        parameter as defined in the API specification.

        :returns: Minimum value
        :rtype: ``int``, ``float``, or ``None``
        """
        return self.data.get('minimum')

    @property
    def maximum(self):
        """
        Returns the maximum value of the :py:class:`.IntegerNumber` \
        parameter as defined in the API specification.

        :returns: Maximum value
        :rtype: ``int``, ``float``, or ``None``
        """
        return self.data.get('maximum')

    def __repr__(self):
        return "<IntegerNumber(name='{0}')>".format(self.name)


class Boolean(object):
    """
    Primative Boolean Parameter Type
    """
    def __init__(self, name, data):
        """
        :param str name: Name of parameter
        :param dict data: Data associated with parameter
        """
        self.name = name
        self.data = data

    @property
    def repeat(self):
        """
        Returns if the parameter can be repeated.

        :rtype: boolean; ``False`` if not defined
        """
        return self.data.get('repeat', False)

    def __repr__(self):
        return "<Boolean(name='{0}')>".format(self.name)


class Date(object):
    """
    Primative Date Parameter Type
    """
    def __init__(self, name, data):
        """
        :param str name: Name of parameter
        :param dict data: Data associated with parameter
        """
        self.name = name
        self.data = data

    @property
    def repeat(self):
        """
        Returns if the parameter can be repeated.

        :rtype: boolean; ``False`` if not defined
        """
        return self.data.get('repeat', False)

    def __repr__(self):
        return "<Date(name='{0}')>".format(self.name)


class File(object):
    """File Parameter Type"""
    def __init__(self, name, data):
        """
        :param str name: Name of parameter
        :param dict data: Data associated with parameter
        """
        self.name = name
        self.data = data

    @property
    def repeat(self):
        """
        Returns if the parameter can be repeated.

        :rtype: boolean; ``False`` if not defined
        """
        return self.data.get('repeat', False)

    def __repr__(self):
        return "<File(name='{0}')>".format(self.name)


class BaseParameter(object):
    """
    Base parameter from which all objects that contain "Named Parameters"
    per `RAML Spec <http://raml.org/spec.html#named-parameters>`_ can \
    inherit.
    """
    def __init__(self, name, data, param_type):
        """
        :param str name: The item name of parameter
        :param dict data: All defined data of the item
        :param str param_type: Type of parameter
        """
        self.name = name
        self.data = data
        self.param_type = param_type

    @property
    def display_name(self):
        """
        Returns the parameter's display name used for display or \
        documentation purposes.

        If ``displayName`` is not specified in RAML, it defaults to \
        :py:obj:`.name`.

        :rtype: ``str``
        """
        return self.data.get('displayName', self.name)

    def _map_type(self, item_type):
        return {
            'string': String,
            'integer': IntegerNumber,
            'number': IntegerNumber,
            'boolean': Boolean,
            'date': Date,
            'file': File
        }[item_type]

    @property
    def type(self):
        """
        Primative type of Parameter.  If ``type`` is not specified in the RAML
        definition, it defaults to :py:class:`.String`.

        Valid types are:

            * ``string``
            * ``number`` - Floating point numbers allowed (as defined by YAML)
            * ``integer`` - Floating point numbers **not** allowed.
            * ``date`` - Acceptible date representations defined under Date/\
                Time formats in \
                `RFC2616 <https://www.ietf.org/rfc/rfc2616.txt>`_
            * ``boolean``
            * ``file`` - only applicable in FormParameters

        :returns: Appropriate primative parameter object
        """
        item_type = self.data.get('type', 'string')
        return self._map_type(item_type)(self.name, self.data)

    @property
    def description(self):
        """
        Returns :py:class:`.Content` object with ``raw`` and \
        ``html`` attributes, or ``None`` if not defined.

        :rtype: :py:class:`.Content`
        """
        return Content(self.data.get('description'))

    @property
    def example(self):
        """
        :returns: example value for the property if set, or ``None``
        :rtype: appropriate primative type, e.g. ``str``, ``int``, ``bool``
        """
        return self.data.get('example')

    @property
    def default(self):
        """
        :returns: default value for the property if set, or ``None``
        :rtype: appropriate primative type, e.g. ``str``, ``int``, ``bool``
        """
        return self.data.get('default')

    def __repr__(self):
        return "<{0}Parameter(name='{1}')>".format(self.param_type, self.name)


class URIParameter(BaseParameter):
    """
    URI parameter with properties defined by the RAML spec's
    `Named Parameters <http://raml.org/spec.html#named-parameters>`_ section, \
    e.g. ``/foo/{id}`` where ``id`` is the name of URI parameter, and \
    ``data`` contains the defined RAML attributes.
    """
    def __init__(self, name, data, required=True):
        """
        :param str name: The parameter name
        :param dict data: All defined data of the parameter
        :param bool required: Default is True
        """
        BaseParameter.__init__(self, name, data, "URI")
        self.required = required


class QueryParameter(BaseParameter):
    """
    Query parameter with properties defined by the RAML spec's
    `Named Parameters <http://raml.org/spec.html#named-parameters>`_ \
    section, e.g.:

        ``/foo/bar?baz=123``

    where ``baz`` is the Query Parameter name, and ``data`` \
    contains the defined RAML attributes.
    """
    def __init__(self, name, data):
        """
        :param str name: The parameter name
        :param dict data: All defined data of the parameter
        :param bool required: Default is True
        """
        BaseParameter.__init__(self, name, data, "Query")

    @property
    def required(self):
        """
        :returns: if the the parameter and its value MUST be present
        :rtype: ``bool``, defaults to ``False`` if not defined
        """
        return self.data.get('required', False)


class FormParameter(BaseParameter):
    """
    Form parameter with properties defined by the RAML spec's \
    `Named Parameters <http://raml.org/spec.html#named-parameters>`_ \
    section, e.g.:

        ``curl -X POST https://api.com/foo/bar -d baz=123``

    where ``baz`` is the Form Parameter name, and ``data`` contains the \
    defined RAML attributes.
    """
    def __init__(self, name, data):
        """
        :param str name: The parameter name
        :param dict data: All defined data of the parameter
        """
        BaseParameter.__init__(self, name, data, "Form")

    @property
    def required(self):
        """
        :returns: if the the parameter and its value MUST be present
        :rtype: ``bool``, defaults to ``False`` if not defined
        """
        return self.data.get('required', False)


class Header(BaseParameter):
    """
    Header with properties defined by the RAML spec's
    `Named Parameters <http://raml.org/spec.html#named-parameters>`_ \
    section, e.g.:

        ``curl -H 'X-Some-Header: foobar' ...``

    where ``X-Some-Header`` is the Header name, and ``data`` contains the
    defined RAML attributes.
    """
    def __init__(self, name, data, method=None):
        """
        :param str name: The parameter name
        :param dict data: All defined data of the parameter
        :param str method: Supported HTTP method
        """
        BaseParameter.__init__(self, name, data, "Header")
        self.method = method


class Body(object):
    """
    Body of a request or a :py:class:`.Response` with properties defined by \
    the `RAML Spec <http://raml.org/spec.html#body>`_
    """
    def __init__(self, mime_type, data):
        """
        :param str name: Accepted MIME media types for the Body of the \
            request/response.
        :param dict data: All defined data of the parameter
        """
        self.mime_type = mime_type
        self.data = data

    @property
    def schema(self):
        """
        :returns: schema definition of :py:class:`.Body` object
        :rtype: ``str`` representation of schema

        .. note::
            Schema can not be set if ``mime_type`` is \
            ``application/x-www-form-urlencoded`` or ``multipart/form-data``.
        """
        schema = self.data.get("schema")
        if self.mime_type in ["application/x-www-form-urlencoded",
                              "multipart/form-data"]:
            # TODO: this needs to raise a validation error
            schema = None
        return schema

    @property
    def example(self):
        """
        :returns: Example of Body
        :rtype: ``str`` representation of example
        """
        return self.data.get("example")

    def __repr__(self):
        return "<Body(name='{0}')>".format(self.name)


class Response(object):
    """
    Expected response with properties defined by \
    the `RAML Spec <http://raml.org/spec.html#responses>`_
    """
    def __init__(self, code, data, method):
        """
        :param int code: Valid HTTP response code
        :param dict data: Data defining the response
        :param str method: Valid HTTP method
        """
        self.code = code
        self.data = data
        self.method = method

    @property
    def description(self):
        """
        Returns :py:class:`.Content` object with ``raw`` and \
        ``html`` attributes, or ``None`` if not defined.

        :rtype: :py:class:`.Content`
        """
        return Content(self.data.get('description'))

    @property
    def headers(self):
        """
        :returns: supported :py:class:`.Header` objects to be expected in \
            the API's response
        :rtype: ``list`` of :py:class:`.Header` objects, or ``None``
        """
        return [
            Header(k, v, self.method) for k, v in self.data.get(
                'headers', {}).items()
        ] or None

    @property
    def body(self):
        """
        :returns: supported :py:class:`.Body` objects to be expected in \
            the API's response
        :rtype: ``list`` of :py:class:`.Body` objects, or ``None``
        """
        name = self.data.get('body').keys()[0]
        data = self.data.get('body').values()[0]
        return Body(name, data) or None

    def __repr__(self):
        return "<Response(code='{0}')>".format(self.code)


class Documentation(object):
    """
    Returns Documentation defined in API Root.
    """
    def __init__(self, title, content):
        """
        :param str title: Title of documentation
        :param str content: Documentation content in raw text
        """
        self.title = title
        self.__content = content

    @property
    def content(self):
        """
        :returns: Content of documentation
        :rtype: :py:class:`.Content` object
        """
        return Content(self.__content)

    def __repr__(self):
        return "<Documentation(title='{0}')>".format(self.title)


class SecurityScheme(object):
    """
    An endpoint's supported security scheme(s), if any, defined by its \
    type (OAuth 2.0, OAuth 1.0, etc).
    """
    def __init__(self, name, data):
        """
        :param str name: Name of scheme (e.g. ``oauth_2_0``, ``oauth_1_0``)
        :param dict data: Data associated security scheme assignment
        """
        self.name = name
        self.data = data

    @property
    def type(self):
        """
        Returns string representation of particular scheme.  Use
        :py:obj:`.scheme` to access the type's object.

        :returns: type of authentication.
        :rtype: ``str`` representation of particular scheme
        """
        return self.data.get('type')

    def _convert_items(self, items, obj, **kw):
        return [obj(k, v, **kw) for k, v in list(items.items())]

    def _get_described_by(self):
        _d = self.data.get('describedBy')

        if _d:
            return {
                'headers': self._convert_items(
                    _d.get('headers', {}), Header, method=None
                ),
                'responses': self._convert_items(
                    _d.get('responses', {}), Response, method=None
                ),
                'query_parameters': self._convert_items(
                    _d.get('queryParameters', {}), QueryParameter
                ),
                'uri_parameters': self._convert_items(
                    _d.get('uriParameters', {}), URIParameter
                ),
                'form_parameters': self._convert_items(
                    _d.get('formParameters', {}), FormParameter
                )
            }

        return None

    @property
    def described_by(self):
        """
        If security scheme is custom, or has extended properties.

        :returns: ``describedBy`` information of the authentication scheme
        :rtype: ``dict`` mapping ``headers``, ``responses``, and parameters
            to respective objects, or ``None``.
        """
        return self._get_described_by()

    def _get_scheme(self, scheme):
        return {'oauth_2_0': Oauth2Scheme,
                'oauth_1_0': Oauth1Scheme}[scheme]

    @property
    def scheme(self):
        if self.name in ['oauth_2_0', 'oauth_1_0']:
            return self.__get_scheme(self.name)(self.data.get('settings'))
        elif self.name.startswith("x-"):
            c = CustomAuthScheme(self.name, self.data.get('settings'))
            for k, v in list(self.data.get('settings').items()):
                setattr(c, k, v)
            return c

    @property
    def description(self):
        """
        Returns :py:class:`.Content` object with ``raw`` and \
        ``html`` attributes, or ``None`` if not defined.

        :rtype: :py:class:`.Content`
        """
        return Content(self.data.get('description'))

    @property
    def settings(self):
        """
        Schema-specific information for either OAuth 2.0, OAuth 1.0, \
        or a API-defined authentication method denoted by ``x-{name}``.

        :rtype: ``dict``, or ``None``
        """
        schemes = ['oauth_2_0', 'oauth_1_0']
        if self.name in schemes:
            return self.data.get('settings')
        elif self.name.startswith("x-"):
            return self.data.get('settings')
        return None

    def __repr__(self):
        return "<SecurityScheme(name='{0}')>".format(self.name)


class Oauth2Scheme(object):
    """
    OAuth 2 Authentication protocol scheme
    """
    def __init__(self, settings):
        self.settings = settings
        self.__scopes = settings.get('scopes')

    @property
    def scopes(self):
        """
        Returns a list of strings of available scopes
        """
        return self.__scopes

    @scopes.setter
    def scopes(self, scope_list):
        self.__scopes = scope_list

    @property
    def authorization_uri(self):
        """
        Returns a string of the authorization URI
        """
        return self.settings.get('authorizationUri')  # string

    @property
    def access_token_uri(self):
        """
        Returns a string of the access token URI
        """
        return self.settings.get('accessTokenUri')  # string

    @property
    def authorization_grants(self):
        """
        Returns a list of strings of authorization grants
        """
        return self.settings.get('authorizationGrants')  # list of strings


class Oauth1Scheme(object):
    """
    OAuth 1 Authentication protocol scheme
    """
    def __init__(self, settings):
        self.settings = settings

    @property
    def request_token_uri(self):
        """
        Returns a string of the Request Token URI
        """
        return self.settings.get('requestTokenUri')

    @property
    def authorization_uri(self):
        """
        Returns a string of the Authorization URI
        """
        return self.settings.get('authorizationUri')

    @property
    def token_credentials_uri(self):
        """
        Returns a string of the Token Credentials URI
        """
        return self.settings.get('tokenCredentialsUri')


class CustomAuthScheme(object):
    """
    Custom Authentication scheme
    """
    def __init__(self, name, settings):
        """
        :param str name: Name of auth scheme
        :param dict settings: Settings associated with auth scheme
        """
        self.name = name
        self.settings = settings
