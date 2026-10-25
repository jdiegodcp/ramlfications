# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB


import attr

from .base import BaseNode
from ramlfications.validate import defined_trait


@attr.s
class TraitNode(BaseNode):
    """
    RAML Trait object

    :param str name: Name of trait
    :param str usage: Usage of trait
    """
    name  = attr.ib()
    # redefines BaseNode.raw to attach the validator
    raw   = attr.ib(repr=False, validator=defined_trait)
    usage = attr.ib(repr=False)
