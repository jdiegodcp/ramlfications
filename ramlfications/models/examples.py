# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import attr


@attr.s
class Example(object):
    """
    Single example.

    Used starting with RAML 1.0.

    """
    value        = attr.ib(repr=False)
    name         = attr.ib(default=None)
    description  = attr.ib(default=None, repr=False)
    display_name = attr.ib(default=None, repr=False)

    # Not sure when validation of examples should get done; leave for now.
    strict       = attr.ib(default=True, repr=False)

    # TODO: this will need to support annotations.
