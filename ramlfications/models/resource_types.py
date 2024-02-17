# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB

from __future__ import absolute_import, division, print_function

import attr

from .base import BaseNode
from ramlfications.validate import *  # NOQA


@attr.s
class ResourceTypeNode(BaseNode):
    """
    RAML Resource Type object

    :param str name: Name of resource type
    :param str type: Name of inherited :py:class:`ResourceTypeNode` object,
        or ``None``.
    :param str method: Supported method. If ends in ``?``, parameters will \
        only be applied to assigned resource if resource implements this \
        method. Else, resource must implement the method.
    :param str usage: Usage of resource type, or ``None``
    :param bool optional: Inherited if resource defines method.
    :param list is: List of assigned trait names, or ``None``
    :param list traits: List of assigned :py:class:`TraitNode` objects, \
        or ``None``
    :param str secured_by: List of ``str`` s or ``dict`` s of assigned \
        security scheme, or ``None``. If a ``str``, the name of the security \
        scheme.  If a ``dict``, the key is the name of the scheme, the values \
        are the parameters assigned (e.g. relevant OAuth 2 scopes).
    :param list security_schemes: A list of assigned \
        :py:class:`parameters.SecurityScheme` objects, or ``None``.
    :param str display_name: User-friendly name of resource; \
        defaults to ``name``

    """
    name             = attr.ib()
    # TODO: abstract validator in BaseNode
    # raw              = attr.ib(repr=False, validator=defined_resource_type)
    type             = attr.ib(repr=False, validator=assigned_res_type)
    method           = attr.ib(repr=False)
    usage            = attr.ib(repr=False)
    optional         = attr.ib(repr=False)
    is_              = attr.ib(repr=False, validator=assigned_traits)
    traits           = attr.ib(repr=False)
    secured_by       = attr.ib(repr=False)
    security_schemes = attr.ib(repr=False)
    display_name     = attr.ib(repr=False)
