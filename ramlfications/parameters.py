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
        # Input validation would be nice here.
        # LR: Will do, but will add it to validate.py

        # Also: Hide private variables with an underscore like:
        # self._name = name
        # LR: Not sure if want this private, though
        self.name = name
        self.schema = schema
        self.example = example

    def __repr__(self):
        return "<ContentType(name='{0}')>".format(self.name)


# NOTE: this is a class for extensibility, e.g. adding RTF support or whatevs
class DescriptiveContent(object):
    """
    Returns documentable content from the RAML file (e.g. Documentation
    content, description) in either raw or parsed form.

    :param str data: The raw/marked up content.
    """
    def __init__(self, data):
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
        Returns parsed Markdown into HTML.
        """
        try:
            return markdown.markdown(self.data)
        except TypeError:
            return None


class String(object):
    """String parameter type"""
    def __init__(self, name, data):
        self.name = name
        self.data = data

    @property
    def enum(self):
        """
        Returns the ``enum`` attribute that provides an enumeration of the
        parameter's valid values. This MUST be an array.  Applicable only
        for parameters of type ``string``.  Returns ``None`` if not set.
        (Optional)
        """
        return self.data.get('enum')

    @property
    def pattern(self):
        """
        Returns the pattern attribute that is a regular expression
        that parameter of type ``string`` MUST match.
        Returns ``None`` if not set.
        """
        return self.data.get('pattern')

    @property
    def min_length(self):
        """
        Returns the parameter value's minimum number of characters.
        Applicable only for parameters of type ``string``.
        Returns ``None`` if not set.
        """
        return self.data.get('min_length')

    @property
    def max_length(self):
        """
        Returns the parameter value's maximum number of characters.
        Applicable only for parameters of type ``string``.
        Returns ``None`` if not set.
        """
        return self.data.get('maxLength')

    def __repr__(self):
        return "<String(name='{0}')>".format(self.name)


class IntegerNumber(object):
    """Integer or Number Parameter Type"""
    def __init__(self, name, data):
        self.name = name
        self.data = data

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

    def __repr__(self):
        return "<IntegerType(name='{0}')>".format(self.name)


class Boolean(object):
    """Boolean Parameter Type"""
    def __init__(self, name, data):
        self.name = name
        self.data = data

    @property
    def repeat(self):
        """
        Returns a boolean if the parameter can be repeated.
        """
        return self.data.get('repeat')

    def __repr__(self):
        return "<Boolean(name='{0}')>".format(self.name)


class Date(object):
    pass


class File(object):
    pass


class BaseParameter(object):
    """
    Base parameter with properties defined by the RAML spec's
    'Named Parameters' section.

    :param str name: The item name of parameter
    :param dict data: All defined data of the item
    :param str param_type: Type of parameter
    """
    def __init__(self, name, data, param_type):
        # Input validation would be nice here.
        # LR: Will do, but will add it to validate.py
        self.name = name
        self.data = data
        self.param_type = param_type

    @property
    def display_name(self):
        """
        Returns the parameter's display name.  (Optional)

        A friendly name used only for display or documentation purposes.

        If ``displayName`` is not specified in RAML, it defaults to ``name``.
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
        definition, it defaults to ``string``.  (Optional)

        Valid types are:
        * ``string``
        * ``number`` - Floating point numbers allowed (as defined by YAML)
        * ``integer`` - Floating point numbers **not** allowed.
        * ``date`` - Acceptible date representations defined under Date/Time\
        formats in [RFC2616](https://www.ietf.org/rfc/rfc2616.txt)
        * ``boolean``
        * ``file`` - only applicable in FormParameters
        """
        # TODO: Add test if 'type' isn't set in RAML
        item_type = self.data.get('type', 'string')
        return self._map_type(item_type)(self.name, self.data)

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
    def example(self):
        """
        Returns the example value for the property.  Returns ``None`` if
        not set.  (Optional)
        """
        return self.data.get('example')

    @property
    def default(self):
        """
        Returns the default attribute for the property if the property
        is omitted or its value is not specified.  Returns ``None`` if not
        defined. (Optional)
        """
        return self.data.get('default')

    def __repr__(self):
        return "<{0}Parameter(name='{1}')>".format(self.param_type, self.name)


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
        # Same concerns as in the class above. Will not mention it again
        # below.
        # LR: this does inherit BaseParameter, this is the new preferred way to
        # call super() on classes that is compatible with py2 and py3
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
        # Exists in a whole lot of classes defined here. Maybe define a class
        # RequiredParameter and inherit from that.
        # LR: No, because Header,  doesn't have 'required'
        return self.data.get('required', True)


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
        return self.data.get('required', True)


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


# From now on please consider:
# - Use undersores for private variables
# - Document if return types can be None, but even better return empty
#   strings everywhere. I won't repeat that. (LR: Will do)
# LR: Not sure which should be private - I think it's useful to have all of
# the below public
class Body(object):
    def __init__(self, name, data):
        self.name = name
        self.data = data

    @property
    def mime_type(self):
        return self.name

    @property
    def schema(self):
        """
        Body schema definition.  Returns ``None`` if not set.

        Can **NOT** be set if ``mime_type`` is
        ``application/x-www-form-urlencoded`` or ``multipart/form-data``.
        (Optional)
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
        Example of Body.  Returns ``None`` if not set. (Optional)
        """
        return self.data.get("example")

    def __repr__(self):
        return "<Body(name='{0}')>".format(self.name)


class Response(object):
    def __init__(self, code, data, method):
        self.code = code
        self.data = data
        self.method = method

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
        return [
            Header(k, v, self.method) for k, v in self.data.get(
                'headers', {}).items()
        ]

    @property
    def body(self):
        return self.data.get('body', '')

    @property
    def resp_content_types(self):
        content_type = []
        if self.data.get('body'):
            # grabs all content types
            # Can content_types be None?
            # LR: not valid raml if body does not have keys that are
            # content types
            content_types = self.data.get('body')
            # types = content_types.keys()
            # Can types be None?
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
    def description(self):
        """
        Returns ``DescriptiveContent`` object with ``raw`` and ``html``
        attributes, or ``None`` if not defined.

        Assumes raw content is written in plain text or Markdown in RAML
        per specification. (Optional)
        """
        return DescriptiveContent(self.data.get('description'))

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
        # Further up you always define methods "required", now we have
        # one "optional". This seems weird unless there's a good reason.
        # Would having a "required" method here be better than
        # "optional".
        # LR: this is according to the RAML spec where "?" denotes optional
        return "?" in self.name

    def __repr__(self):
        return "<ResourceTypeMethod(name='{0}')>".format(self.name)


class Documentation(object):
    """
    Returns Documentation defined in API Root.
    """
    def __init__(self, title, content):
        self.title = title
        self.content = DescriptiveContent(content)

    def __repr__(self):
        return "<Documentation(title='{0}')>".format(self.title)


class SecuritySchemes(object):
    def __init__(self, raml_file):
        self.raml = raml_file

    def _get_security_schemes(self):
        defined_schemes = self.raml.get('securitySchemes')
        if defined_schemes:
            schemes = []
            for s in defined_schemes:
                schemes.extend(
                    [SecurityScheme(k, v) for k, v in list(s.items())]
                )
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
        return self._get_described_by()

    @property
    def description(self):
        """
        Returns ``DescriptiveContent`` object with ``raw`` and ``html``
        attributes, or ``None`` if not defined.

        Assumes raw content is written in plain text or Markdown in RAML
        per specification. (Optional)
        """
        return DescriptiveContent(self.data.get('description'))

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
