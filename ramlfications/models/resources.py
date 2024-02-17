# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB

from __future__ import absolute_import, division, print_function

import attr

from .base import BaseNode
from ramlfications.validate import *  # NOQA


@attr.s
class ResourceNode(BaseNode):
    """
    Supported API-endpoint (“resource”)

    :param str name: Resource name
    :param ResourceNode parent: parent node object if any, or ``None``
    :param str method: HTTP method for resource, or ``None``
    :param str display_name: User-friendly name of resource; \
        defaults to ``name``
    :param str path: relative path of resource
    :param str absolute_uri: Absolute URI of resource: \
        :py:class:`RootNodeAPI08`'s ``base_uri`` + ``path``
    :param list is: A list of ``str`` s or ``dict`` s of resource-assigned \
        traits, or ``None``
    :param list traits: A list of assigned :py:class:`TraitNode` objects, \
        or ``None``
    :param str type: The name of the assigned resource type, or ``None``
    :param ResourceTypeNode resource_type: The assigned \
        :py:class:`ResourceTypeNode` object
    :param list secured_by: A list of ``str`` s or ``dict`` s of resource-\
        assigned security schemes, or ``None``. If a ``str``, the name of the \
        security scheme.  If a ``dict``, the key is the name of the scheme, \
        the values are the parameters assigned (e.g. relevant OAuth 2 scopes).
    :param list security_schemes: A list of assigned \
        :py:class:`parameters.SecurityScheme` objects, or ``None``.
    """
    name             = attr.ib(repr=False)
    parent           = attr.ib(repr=False)
    method           = attr.ib()
    display_name     = attr.ib(repr=False)
    path             = attr.ib()
    absolute_uri     = attr.ib(repr=False)
    is_              = attr.ib(repr=False, validator=assigned_traits)
    traits           = attr.ib(repr=False)
    type             = attr.ib(repr=False, validator=assigned_res_type)
    resource_type    = attr.ib(repr=False)
    secured_by       = attr.ib(repr=False)
    security_schemes = attr.ib(repr=False)
