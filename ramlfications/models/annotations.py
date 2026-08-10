# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB


import attr

from .base import BaseContent


@attr.s
class AnnotationType(object):
    """
    A RAML 1.0 ``annotationTypes`` declaration.

    :param str name: name of the annotation type
    :param dict raw: raw declaration data
    :param str type: declared value type (a data type name or expression)
    :param data_type: resolved data type object for the value type
    :param list allowed_targets: locations this annotation may target
    """
    name            = attr.ib()
    raw             = attr.ib(repr=False, cmp=False)
    type            = attr.ib(repr=False, default="string")
    data_type       = attr.ib(repr=False, default=None)
    display_name    = attr.ib(repr=False, default=None)
    description     = attr.ib(repr=False, converter=BaseContent, default="")
    allowed_targets = attr.ib(repr=False, default=None)
    errors          = attr.ib(repr=False, cmp=False, default=None)
    config          = attr.ib(repr=False, cmp=False, default=None)


@attr.s
class Annotation(object):
    """
    An annotation applied to a node: ``(name): value``.

    :param str name: annotation name (without parentheses)
    :param value: the applied value
    :param AnnotationType annotation_type: the declared annotation type, \
        or ``None`` if the annotation is not declared
    """
    name            = attr.ib()
    value           = attr.ib(repr=False)
    annotation_type = attr.ib(repr=False, default=None)
