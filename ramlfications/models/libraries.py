# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB


import attr


@attr.s
class Library(object):
    """
    A RAML 1.0 library brought in through a ``uses`` declaration.

    Members are addressable from the using document via the dotted
    ``LibName.member`` notation; the parsed member objects are exposed
    here under those dotted names.

    :param str name: alias the library was assigned in ``uses``
    :param dict raw: loaded raw data of the library file
    :param str usage: the library's ``usage`` description, or ``None``
    :param list uses: nested :py:class:`.Library` objects this library \
        itself uses, or ``None``
    :param list types: parsed data types declared by the library
    :param list annotation_types: parsed annotation types declared \
        by the library
    :param list traits: parsed traits declared by the library
    :param list resource_types: parsed resource types declared \
        by the library
    :param list security_schemes: parsed security schemes declared \
        by the library
    :param str prefix: fully-qualified dotted prefix of this library \
        as seen from the root document (e.g. ``common.base.``)
    """
    name             = attr.ib()
    raw              = attr.ib(repr=False, cmp=False)
    usage            = attr.ib(repr=False, default=None)
    uses             = attr.ib(repr=False, default=None)
    types            = attr.ib(repr=False, default=None)
    annotation_types = attr.ib(repr=False, default=None)
    traits           = attr.ib(repr=False, default=None)
    resource_types   = attr.ib(repr=False, default=None)
    security_schemes = attr.ib(repr=False, default=None)
    prefix           = attr.ib(repr=False, cmp=False, default="")
    errors           = attr.ib(repr=False, cmp=False, default=None)
    config           = attr.ib(repr=False, cmp=False, default=None)
