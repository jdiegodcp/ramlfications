# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB

from __future__ import absolute_import, division, print_function

import attr

from .base import BaseNode, BaseContent
from ramlfications.validate import *  # NOQA


@attr.s
class SecuritySchemeNode(BaseNode):
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
    type          = attr.ib(repr=False)
    described_by  = attr.ib(repr=False)
    settings      = attr.ib(repr=False, validator=defined_sec_scheme_settings)
    config        = attr.ib(repr=False)

    @property
    def description(self):
        if self.desc:
            return BaseContent(self.desc)
        return None
