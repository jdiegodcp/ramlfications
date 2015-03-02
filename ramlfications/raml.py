# ! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function

import attr
from six.moves import BaseHTTPServer as httpserver

from .validate import *  # NOQA

__all__ = ["RootNode", "ResourceNode"]

HTTP_RESP_CODES = httpserver.BaseHTTPRequestHandler.responses.keys()
AVAILABLE_METHODS = ['get', 'post', 'put', 'delete', 'patch', 'head',
                     'options', 'trace', 'connect']


class RAMLParserError(Exception):
    pass


@attr.s
class RootNode(object):
    """
    API Root Node
    """
    raml_file        = attr.ib(validator=root_raml_file)
    raw              = attr.ib(repr=False)
    version          = attr.ib(repr=False, validator=root_version)
    base_uri         = attr.ib(repr=False, validator=root_base_uri)
    base_uri_params  = attr.ib(repr=False,
                               validator=root_base_uri_params)
    uri_params       = attr.ib(repr=False, validator=root_uri_params)
    protocols        = attr.ib(repr=False, validator=root_protocols)
    title            = attr.ib(repr=False, validator=root_title)
    docs             = attr.ib(repr=False, validator=root_docs)
    schemas          = attr.ib(repr=False, validator=root_schemas)
    media_type       = attr.ib(repr=False, validator=root_media_type)
    resource_types   = attr.ib(repr=False, init=False)
    traits           = attr.ib(repr=False, init=False)
    security_schemes = attr.ib(repr=False, init=False)
    resources        = attr.ib(repr=False, init=False,
                               validator=root_resources)
    raml_obj         = attr.ib(repr=False)


@attr.s
class BaseNode(object):
    raw             = attr.ib(repr=False)
    root            = attr.ib(repr=False)
    headers         = attr.ib(repr=False)
    body            = attr.ib(repr=False)
    responses       = attr.ib(repr=False)
    uri_params      = attr.ib(repr=False)
    base_uri_params = attr.ib(repr=False)
    query_params    = attr.ib(repr=False)
    form_params     = attr.ib(repr=False)
    media_type      = attr.ib(repr=False)
    description     = attr.ib(repr=False)
    protocols       = attr.ib(repr=False)


@attr.s
class TraitNode(BaseNode):
    name = attr.ib()
    usage = attr.ib(repr=False)


@attr.s
class ResourceTypeNode(BaseNode):
    name             = attr.ib()
    type             = attr.ib(repr=False, validator=assigned_res_type)
    method           = attr.ib(repr=False)
    usage            = attr.ib(repr=False)
    optional         = attr.ib(repr=False)
    is_              = attr.ib(repr=False, validator=assigned_traits)
    traits           = attr.ib(repr=False)
    secured_by       = attr.ib(repr=False)
    security_schemes = attr.ib(repr=False)
    display_name     = attr.ib(repr=False)


@attr.s
class ResourceNode(BaseNode):
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
