# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB

from __future__ import absolute_import, division, print_function


from ramlfications.validate import *  # NOQA

from .base import BaseContent


####
# Attributes found in the root of RAML file(s)
####

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
        return BaseContent(self._title)

    @property
    def content(self):
        return BaseContent(self._content)

    def __repr__(self):  # NOCOV
        return "Documentation(title='{0}')".format(self.title)
