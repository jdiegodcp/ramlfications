# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB

from __future__ import absolute_import, division, print_function

import attr

from six import iterkeys

from ramlfications.validate import *  # NOQA


RAML_ROOT_LOOKUP = {}


def collectramlroots(kls):
    def klass():
        if kls.raml_version not in list(iterkeys(RAML_ROOT_LOOKUP)):
            RAML_ROOT_LOOKUP[kls.raml_version] = kls
    klass()
    return kls


@attr.s
class BaseRootNode(object):
    """
    API Root Node

    This is the base node for api raml, or fragments

    :param dict raw: dict of loaded RAML data
    :param str raml_version: RAML spec version
    """
    raw              = attr.ib(repr=False)
    raml_version     = attr.ib(repr=False)


@attr.s
class RootNodeAPIBase(BaseRootNode):
    """
    API Root Node base for API files

    :param str version: API version
    :param str base_uri: API's base URI
    :param list base_uri_params: parameters for base URI, or ``None``. \
        The order of ``base_uri_params`` will follow the order \
        defined in the :py:obj:`.RootNodeAPI08.base_uri`.
    :param list uri_params: URI parameters that can apply to all resources, \
        or ``None``. The order of ``uri_params`` will follow the order \
        defined in the :py:obj:`.RootNodeAPI08.base_uri`.
    :param list protocols: API-supported protocols, defaults to protocol \
        in ``base_uri``
    :param str title: API Title
    :param list docs: list of :py:class:`parameters.Documentation` objects, \
        or ``None``
    :param list schemas: list of dictionaries, or ``None``
    :param str media_type: default accepted request/response media type, \
        or ``None``
    :param list resource_types: list of :py:class:`ResourceTypeNode`, \
        or ``None``
    :param list traits: list of :py:class:`TraitNode`, or ``None``
    :param list security_schemes: list of \
        :py:class:`parameters.SecurityScheme` objects, or ``None``
    :param list resources: list of :py:class:`ResourceNode` objects, \
        or ``None``
    :param raml_obj: loaded :py:class:`raml.RAMLDict` object
    """
    version          = attr.ib(repr=False, validator=root_version)
    base_uri         = attr.ib(repr=False, validator=root_base_uri)
    base_uri_params  = attr.ib(repr=False,
                               validator=root_base_uri_params)
    uri_params       = attr.ib(repr=False, validator=root_uri_params)
    protocols        = attr.ib(repr=False, validator=root_protocols)
    title            = attr.ib(validator=root_title)
    documentation    = attr.ib(repr=False, validator=root_docs)
    schemas          = attr.ib(repr=False, validator=root_schemas)
    media_type       = attr.ib(repr=False, validator=root_media_type)
    secured_by       = attr.ib(repr=False, validator=root_secured_by)
    resource_types   = attr.ib(repr=False, init=False)
    traits           = attr.ib(repr=False, init=False)
    security_schemes = attr.ib(repr=False, init=False)
    resources        = attr.ib(repr=False, init=False,
                               validator=root_resources)
    raml_obj         = attr.ib(repr=False)
    config           = attr.ib(repr=False,
                               validator=attr.validators.instance_of(dict))
    errors           = attr.ib(repr=False)


@collectramlroots
@attr.s
class RootNodeAPI08(RootNodeAPIBase):
    """
    API Root Node for 0.8 raml files
    """
    raml_version = "0.8"


@collectramlroots
@attr.s
class RootNodeAPI10(RootNodeAPIBase):
    """
    API Root Node for 1.0 raml files
    """
    types            = attr.ib(repr=False, init=False)
    raml_version = "1.0"
