#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function

import markdown2 as markdown

HTTP_METHODS = ["get", "post", "put", "delete", "patch", "options", "head"]


class ContentType(object):
    """
    Supported Content Type of a resource (e.g. ``application/json``).

    :param str name: The name of content type
    :param dict schema: Schema definition of content type
    :param str example: Example usage of content type
    """
    def __init__(self, name, schema, example):
        self.name = name
        self.schema = schema
        self.example = example

    def __repr__(self):
        return "<ContentType(name='{0}')>".format(self.name)


class BaseParameter(object):
    """
    Base parameter with properties defined by the RAML spec's
    'Named Parameters' section.

    :param str item: The item name of parameter
    :param dict data: All defined data of the item
    :param str param_type: Type of parameter
    """
    def __init__(self, item, data, param_type):
        self.item = item
        self.data = data
        self.param_type = param_type

    @property
    def name(self):
        """
        RAML key/name of the parameter.
        """
        return self.item

    @property
    def display_name(self):
        """
        Returns the parameter's display name.

        A friendly name used only for display or documentation purposes.

        If ``displayName`` is not specified in RAML, it defaults to ``name``.
        """
        display_name = self.data.get('displayName')
        if not display_name:
            display_name = self.name
        return display_name

    @property
    def type(self):
        """
        Primative type of Parameter.  If ``type`` is not specified in the RAML
        definition, it defaults to ``string``.

        Valid types are:
        * ``string``
        * ``number`` - Floating point numbers allowed (as defined by YAML)
        * ``integer`` - Floating point numbers **not** allowed.
        * ``date`` - Acceptible date representations defined under Date/Time\
        formats in [RFC2616](https://www.ietf.org/rfc/rfc2616.txt)
        * ``boolean``
        * ``file`` - only applicable in FormParameters
        """
        return self.data.get('type')

    @property
    def description_raw(self):
        """
        The description attribute describing the intended use or meaning
        of the parameter.  May be written in Markdown.
        """
        return self.data.get('description')

    @property
    def description_html(self):
        """
        The ``description_raw`` attribute parsed into HTML.
        """
        return markdown.markdown(self.data.get('description', ''))

    @property
    def example(self):
        """
        Returns the example value for the property.
        """
        return self.data.get('example', '')

    @property
    def enum(self):
        """
        Returns the ``enum`` attribute that provides an enumeration of the \
        parameter's valid values. This MUST be an array.  Applicable only
        for parameters of type ``string``.
        """
        return self.data.get('enum')

    @property
    def default(self):
        """
        Returns the default attribute for the property if the property \
        is omitted or its value is not specified.
        """
        return self.data.get('default')

    @property
    def pattern(self):
        """
        Returns the pattern attribute that is a regular expression \
        that parameter of type ``string`` MUST match.
        """
        return self.data.get('pattern')

    @property
    def min_length(self):
        """
        Returns the parameter value's minimum number of characters.
        Applicable only for parameters of type ``string``.
        """
        return self.data.get('minLength')

    @property
    def max_length(self):
        """
        Returns the parameter value's maximum number of characters.
        Applicable only for parameters of type ``string``.
        """
        return self.data.get('maxLength')

    @property
    def minimum(self):
        """
        Returns the parameter's minimum value.
        Applicable only for parameters of type ``integer`` or ``number``.
        """
        return self.data.get('minimum')

    @property
    def maximum(self):
        """
        Returns the parameter's minimum value.
        Applicable only for parameters of type ``integer`` or ``number``.
        """
        return self.data.get('maximum')

    @property
    def repeat(self):
        """
        Returns a boolean if the parameter can be repeated.
        """
        return self.data.get('repeat')

    def __repr__(self):
        return "<{0}Parameter(name='{1}')>".format(self.param_type, self.name)


class JSONFormParameter(object):   # pragma: no cover
    def __init__(self, param, data, example):
        BaseParameter.__init__(self, param, data, "JSON")
        self.example = example

    @property
    def required(self):
        return self.data.get('required')


class URIParameter(BaseParameter):
    """
    URI parameter with properties defined by the RAML spec's
    'Named Parameters' section, e.g. ``/foo/{id}`` where ``id``
    is the name of URI parameter, and ``data`` are the
    defined RAML attributes (e.g. ``required=True``, ``type=string``)

    :param str param: The parameter name
    :param dict data: All defined data of the parameter
    :param bool required: Default is True
    """
    def __init__(self, param, data, required=True):
        BaseParameter.__init__(self, param, data, "URI")
        self.required = required


class QueryParameter(BaseParameter):
    """
    Query parameter with properties defined by the RAML spec's
    'Named Parameters' section, e.g.:

    ``/foo/bar?baz=123``

    where ``baz`` is the Query Parameter name, and ``data`` are the
    defined RAML attributes (e.g. ``required=True``, ``type=string``)

    :param str param: The parameter name
    :param dict data: All defined data of the parameter
    :param bool required: Default is True
    """
    def __init__(self, param, data):
        BaseParameter.__init__(self, param, data, "Query")

    @property
    def required(self):
        """
        Returns a boolean if the the parameter and its value MUST be present.
        Defaults to ``False`` if not defined, except for ``URIParameter``,
        where the default is ``True`` if omitted.
        """
        return self.data.get('required')


class FormParameter(BaseParameter):
    """
    Form parameter with properties defined by the RAML spec's
    'Named Parameters' section, e.g.:

    ``curl -X POST https://api.com/foo/bar -d baz=123``

    where ``baz`` is the Form Parameter name, and ``data`` are the
    defined RAML attributes (e.g. ``required=True``, ``type=string``).

    :param str param: The parameter name
    :param dict data: All defined data of the parameter
    """
    def __init__(self, param, data):
        BaseParameter.__init__(self, param, data, "Form")

    @property
    def required(self):
        """
        Returns a boolean if the the parameter and its value MUST be present.
        Defaults to ``False`` if not defined, except for ``URIParameter``,
        where the default is ``True`` if omitted.
        """
        return self.data.get('required')


class Header(BaseParameter):
    """
    Header with properties defined by the RAML spec's
    'Named Parameters' section, e.g.:

    ``curl -H 'X-Some-Header: foobar' ...``

    where ``X-Some-Header`` is the Header name, and ``data`` are the
    defined RAML attributes (e.g. ``required=True``, ``type=string``).

    :param str param: The parameter name
    :param dict data: All defined data of the parameter
    """
    def __init__(self, name, data, method):
        BaseParameter.__init__(self, name, data, "Header")
        self.method = method


class Body(object):
    def __init__(self, name, data):
        self.name = name
        self.data = data

    @property
    def mime_type(self):
        return self.name

    @property
    def schema(self):
        return self.data.get("schema")

    @property
    def example(self):
        return self.data.get("example")

    def __repr__(self):
        return "<Body(name='{0}')>".format(self.name)


class Response(object):
    def __init__(self, code, data, method):
        self.code = code
        self.data = data
        self.method = method

    @property
    def description_raw(self):
        return self.data.get('description')

    @property
    def description_html(self):
        return markdown.markdown(self.data.get('description', ''))

    @property
    def headers(self):
        _headers = self.data.get('headers')
        headers = []
        if _headers:
            for k, v in list(_headers.items()):
                headers.append(Header(k, v, self.method))
        return headers

    @property
    def body(self):
        return self.data.get('body')

    @property
    def resp_content_types(self):
        content_type = []
        if self.data.get('body'):
            # grabs all content types
            content_types = self.data.get('body')
            types = self.data.get('body').keys()
            for content in types:
                schema = content_types.get(content).get('schema')
                example = content_types.get(content).get('example')
                content_type.append(ContentType(content, schema, example))
        return content_type

    def __repr__(self):
        return "<Response(code='{0}')>".format(self.code)


class ResourceType(object):
    def __init__(self, name, data):
        self.name = name
        self.data = data

    @property
    def usage(self):
        return self.data.get('usage')

    @property
    def description_raw(self):
        return self.data.get('description')

    @property
    def description_html(self):
        return markdown.markdown(self.data.get('description', ''))

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

    def __repr__(self):
        return "<ResourceType(name='{0}')>".format(self.name)


class ResourceTypeMethod(object):
    def __init__(self, name, data):
        self.name = name
        self.data = data

    @property
    def optional(self):
        return "?" in self.name

    def __repr__(self):
        return "<ResourceTypeMethod(name='{0}')>".format(self.name)


class Documentation(object):
    """
    Returns Documentation defined in API Root.
    """
    def __init__(self, title, content):
        self.title = title
        self.content_raw = content or ''
        self.content_html = markdown.markdown(self.content_raw)

    def __repr__(self):
        return "<Documentation(title='{0}')>".format(self.title)


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

    def _get_described_by(self):
        _described_by = self.data.get('describedBy')

        if _described_by:
            described_by = {}

            _headers = _described_by.get('headers')
            _responses = _described_by.get('responses')
            _q_params = _described_by.get('queryParameters')
            _u_params = _described_by.get('uriParameters')
            _f_params = _described_by.get('formParameters')

            if _headers:
                head = []
                for k, v in list(_headers.items()):
                    head.append(Header(k, v, method=None))
                described_by['headers'] = head

            if _responses:
                resp = []
                for k, v in list(_responses.items()):
                    resp.append(Response(k, v, method=None))
                described_by['responses'] = resp

            if _q_params:
                q = []
                for k, v in list(_q_params.items()):
                    q.append(QueryParameter(k, v))
                described_by['query_parameters'] = q

            if _u_params:
                u = []
                for k, v in list(_u_params.items()):
                    u.append(URIParameter(k, v))
                described_by['uri_parameters'] = u

            if _f_params:
                f = []
                for k, v in list(_f_params.items()):
                    f.append(FormParameter(k, v))
                described_by['form_parameters'] = f

            return described_by
        return None

    @property
    def described_by(self):
        return self._get_described_by()

    @property
    def description_raw(self):
        return self.data.get('description')

    @property
    def description_html(self):
        return markdown.markdown(self.data.get('description', ''))

    def _get_oauth_scheme(self, scheme):
        return {'oauth_2_0': Oauth2Scheme,
                'oauth_1_0': Oauth1Scheme}[scheme]

    @property
    def settings(self):
        schemes = ['oauth_2_0', 'oauth_1_0']
        if self.name in schemes:
            return self._get_oauth_scheme(self.name)(self.data.get('settings'))

    def __repr__(self):
        return "<Security Scheme(name='{0}')>".format(self.name)


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
