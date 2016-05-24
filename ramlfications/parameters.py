# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function


import attr
import markdown2 as md

from .validate import *  # NOQA


NAMED_PARAMS = [
    "desc", "type", "enum", "pattern", "minimum", "maximum", "example",
    "default", "required", "repeat", "display_name", "max_length",
    "min_length"
]


class Content(object):
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
        return self.data

    @property
    def html(self):
        """
        Returns parsed Markdown into HTML
        """
        return md.markdown(self.data)

    def __repr__(self):
        return self.raw


class Documentation(object):
    """
    User documentation for the API.

    :param str title: Title of documentation.
    :param str content: Content of documentation.
    """
    def __init__(self, _title, _content):
        self._title = _title
        self._content = _content

    @property
    def title(self):
        return Content(self._title)

    @property
    def content(self):
        return Content(self._content)

    def __repr__(self):  # NOCOV
        return "Documentation(title='{0}')".format(self.title)


@attr.s
class SecurityScheme(object):
    """
    Security scheme definition.

    :param str name: Name of security scheme
    :param dict raw: All defined data of item
    :param str type: Type of authentication
    :param dict described_by: :py:class:`.Header` s, :py:class:`.Response` s, \
        :py:class:`.QueryParameter` s, etc that is needed/can be expected \
        when using security scheme.
    :param str description: Description of security scheme
    :param dict settings: Security schema-specific information
    """
    name          = attr.ib()
    raw           = attr.ib(repr=False, init=True,
                            validator=attr.validators.instance_of(dict))
    type          = attr.ib(repr=False)
    described_by  = attr.ib(repr=False)
    desc          = attr.ib(repr=False)
    settings      = attr.ib(repr=False, validator=defined_sec_scheme_settings)
    config        = attr.ib(repr=False)
    errors        = attr.ib(repr=False)

    @property
    def description(self):
        if self.desc:
            return Content(self.desc)
        return None
