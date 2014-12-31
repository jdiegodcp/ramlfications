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
    """
    Module helper function to parse a RAML File.  First loads the RAML file
    with :py:class:`.loader.RAMLLoader` then parses with 
    :py:func:`.parser.parse_raml` to return a :py:class:`.raml.RAMLRoot`
    object.

    :param str raml_file: String path to RAML file
    :return: parsed API
    :rtype: RAMLRoot
    :raises LoadRamlFileError: If error occurred trying to load the RAML file
        (see :py:class:`.loader.RAMLLoader`)
    :raises RAMLParserError: If error occurred during parsing of RAML file
        (see :py:class:`.raml.RAMLRoot`)
    """
    loader = RAMLLoader().load(raml_file)
    return parse_raml(loader)


def load(raml_file):
    """
    Module helper function to load a RAML File using :py:class:`.loader.RAMLLoader`.

    :param str raml_file: String path to RAML file
    :return: loaded RAML file
    :rtype: RAMLDict
    :raises LoadRamlFileError: If error occurred trying to load the RAML file
        (see :py:class:`.loader.RAMLLoader`)
    """
    return RAMLLoader().load(raml_file)


def validate(raml_file, production=True):
    """
    Module helper function to validate a RAML File.  First loads the RAML file
    with :py:class:`.loader.RAMLLoader` then validates with :py:func:`.validate.validate_raml`.

    :param str raml_file: String path to RAML file
    :param bool production: If the RAML file is meant to be production-ready
    :return: No return value if successful
    :raises LoadRamlFileError: If error occurred trying to load the RAML file
        (see :py:class:`.loader.RAMLLoader`)
    :raises InvalidRamlFileError: If error occurred trying to validate the RAML
        file (see :py:mod:`.validate`)

    """
    return validate_raml(raml_file, production)
