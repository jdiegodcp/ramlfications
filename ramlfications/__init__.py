#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function

__author__ = 'Lynn Root'
__version__ = '0.1.0'
__license__ = 'Apache 2.0'


from ramlfications.loader import load
from ramlfications.parser import parse
from ramlfications.validate import validate

__all__ = [
    'load',
    'parse',
    'validate'
]
