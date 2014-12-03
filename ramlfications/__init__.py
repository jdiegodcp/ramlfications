#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function

__author__ = 'Lynn Root'
__version__ = '0.1.0'
__license__ = 'Apache 2.0'


from ramlfications.loader import *  # NOQA
from ramlfications.parser import *  # NOQA
from ramlfications.validate import *  # NOQA


def parse(raml_file):
    loader = RAMLLoader(raml_file)
    return APIRoot(loader)


def load(raml_file):
    loader = RAMLLoader(raml_file)
    return loader.load()


def validate(raml_file, production=True):
    return validate_raml(raml_file, production)
