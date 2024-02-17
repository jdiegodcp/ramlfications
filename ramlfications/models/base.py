# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB

from __future__ import absolute_import, division, print_function

import attr
import markdown2 as md


from ramlfications.validate import *  # NOQA


#####
# common base objects
#####

class BaseContent(object):
    """
    Returns documentable content from the RAML file (e.g. Documentation
    content, description) in either raw or parsed form.
    :param str data: The raw/marked up content data.
    """
    def __init__(self, data):
        self.data = data

    @property
    def raw(self):
        """
        Return raw Markdown/plain text written in the RAML file
        """
        if self.data:
            return self.data
        return ""

    @property
    def html(self):
        """
        Returns parsed Markdown into HTML
        """
        if self.data:
            return md.markdown(self.data)

    def __repr__(self):
        return self.raw


#####
# base object for RAML nodes (e.g. resources, data types, etc)
#####
@attr.s
class BaseNode(object):
    """
    :param RootNodeAPI08 root: Back reference to the node's API root
    :param list headers: List of node's :py:class:`parameters.Header` \
        objects, or ``None``
    :param list body: List of node's :py:class:`parameters.Body` objects, \
        or ``None``
    :param list responses: List of node's :py:class:`parameters.Response`\
        objects, or ``None``
    :param list uri_params: List of node's :py:class:`parameters.URIParameter`\
        objects, or ``None``. The order of ``uri_params`` will follow the \
        order defined in the \
        :py:obj:`.ResourceNode.absolute_uri`.
    :param list base_uri_params: List of node's base \
        :py:obj:`parameters.URIParameter` objects, or ``None``. The order of \
        ``base_uri_params`` will follow the order defined in the \
        :py:attribute:`.ResourceNode.absolute_uri`.
    :param list query_params: List of node's \
        :py:obj:`parameters.QueryParameter` objects, or ``None``
    :param list form_params: List of node's \
        :py:class:`parameters.FormParameter` objects, or ``None``
    :param str media_type: Supported request MIME media type. Defaults to \
        :py:class:`RootNodeAPI08`'s ``media_type``.
    :param str description: Description of node.
    :param list protocols: List of ``str`` 's of supported protocols. \
        Defaults to :py:class:`RootNodeAPI08`'s ``protocols``.
    """
    root            = attr.ib(repr=False)
    raw             = attr.ib(repr=False)  # TODO: abstract validator
    headers         = attr.ib(repr=False)
    body            = attr.ib(repr=False)
    responses       = attr.ib(repr=False)
    uri_params      = attr.ib(repr=False)
    base_uri_params = attr.ib(repr=False)
    query_params    = attr.ib(repr=False)
    form_params     = attr.ib(repr=False)
    media_type      = attr.ib(repr=False)
    desc            = attr.ib(repr=False)
    protocols       = attr.ib(repr=False)
    errors          = attr.ib(repr=False)

    @property
    def description(self):
        return BaseContent(self.desc)


#####
# base objects for .parameters.py
#####

@attr.s
class BaseNamedParameter(object):
    """
    Base parameter with properties defined by the RAML spec's \
    'Named Parameters' section.
    :param str name: The name of parameter.
    :param default: Default value for property, or ``None``. Type of \
        ``default`` will match that of ``type``.
    :param str desc: Parameter description, or ``None``.
    :param str display_name: User-friendly name for display or \
        documentation purposes.  If ``displayName`` is not specified \
        in RAML file, defaults to ``name``.
    :param list enum: Array of valid parameter values, or ``None``.  \
        Only applies when primative ``type`` is ``string``.
    :param example: Example value for property, or ``None``. \
        For RAML 0.8, the type of ``example`` will match that of ``type``. \
        For RAML 1.0, ``example`` will be an ``Example`` object with a \
        ``value`` attribute whose type matches that of ``type``.
    :param examples: List of ``Example`` objects (RAML 1.0 only).
    :param int max_length: Parameter value's maximum number of \
        characters, or ``None``. Only applies when primative ``type`` \
        is ``string``.
    :param int maximum: Parmeter's maximum value, or ``None``.  Only \
        applies when primative ``type`` is ``integer`` or ``number``.
    :param int min_length: Parameter value's minimum number of \
        characters, or ``None``. Only applies when primative ``type`` \
        is ``string``.
    :param int minimum: Parameter's minimum value, or ``None``.  Only \
        applies when primative ``type`` is ``integer`` or ``number``.
    :param str pattern: A regular expression that parameter of type \
        ``string`` must match, or ``None`` if not set.
    :param bool repeat: If parameter can be repeated.  Defaults to ``False``.
    :param bool required: If parameter is required.
    :param str type: Primative type of parameter. Defaults to ``string`` if \
        not set.
    """
    name         = attr.ib()
    default      = attr.ib(repr=False)
    desc         = attr.ib(repr=False)
    display_name = attr.ib(repr=False)
    example      = attr.ib(repr=False)
    max_length   = attr.ib(repr=False, validator=string_type_parameter)
    maximum      = attr.ib(repr=False, validator=integer_number_type_parameter)
    min_length   = attr.ib(repr=False, validator=string_type_parameter)
    minimum      = attr.ib(repr=False, validator=integer_number_type_parameter)
    enum         = attr.ib(repr=False, default=None,
                           validator=string_type_parameter)
    pattern      = attr.ib(repr=False, default=None,
                           validator=string_type_parameter)


@attr.s
class BaseParameterAttrs(object):
    """
    Attributes useful for params

    :param dict raw: All defined data of the item
    :param dict config: API's configuration specific to the \
        ``ramlfications`` library.
    :param list errors: List of RAML validation errors.
    """
    raw    = attr.ib(repr=False, cmp=False,
                     validator=attr.validators.instance_of(dict))
    config = attr.ib(repr=False, cmp=False,
                     validator=attr.validators.instance_of(dict))
    errors = attr.ib(repr=False)


@attr.s
class BaseParameter(BaseParameterAttrs, BaseNamedParameter):
    """
    Base parameter with named params plus additional attributes.
    Extends :py:class:`.BaseNamedParameter` with raw dict data from \
    the RAML file, configuration, validation errors, and adds \
    ``description`` property with ``BaseNamedParameter.desc`` parsed \
    into available markup.
    :param dict raw: All defined data of the item
    :param dict config: API's configuration specific to the \
        ``ramlfications`` library.
    :param list errors: List of RAML validation errors.
    """

    @property
    def description(self):
        if self.desc:
            return BaseContent(self.desc)
        return None


@attr.s
class BaseParameterRaml08(object):
    """TODO: writeme"""
    repeat = attr.ib(repr=False)


@attr.s
class BaseParameterRaml10(object):
    """TODO: writeme"""
    examples = attr.ib(repr=False)
