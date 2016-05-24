# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB

from __future__ import absolute_import, division, print_function

import attr

from .base import BaseNode


@attr.s
class TraitNode(BaseNode):
    """
    RAML Trait object

    :param str name: Name of trait
    :param str usage: Usage of trait
    """
    name  = attr.ib()
    # TODO: abstract validator in BaseNode
    # raw   = attr.ib(repr=False, validator=defined_trait)
    usage = attr.ib(repr=False)
