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
    with ``loader.RAMLLoader`` then parses with ``parser.APIRoot``.

    :param str raml_file: String path to RAML file
    :return: parsed API
    :rtype: APIRoot object
    :raises LoadRamlFileError: If error occurred trying to load the RAML file
        (see ``loader.RAMLLoader``)
    :raises RAMLParserError: If error occurred during parsing of RAML file
        (see ``parser.APIRoot``)
    """
    loader = RAMLLoader().load(raml_file)
    return APIRoot(loader)


def load(raml_file):
    """
    Module helper function to load a RAML File using ``loader.RAMLLoader``.

    :param str raml_file: String path to RAML file
    :return: loaded RAML file
    :rtype: dict
    :raises LoadRamlFileError: If error occurred trying to load the RAML file
        (see ``loader.RAMLLoader``)
    """
    return RAMLLoader().load(raml_file)


def validate(raml_file, production=True):
    """
    Module helper function to validate a RAML File.  First loads the RAML file
    with ``loader.RAMLLoader`` then validates with ``validate.validate_raml``.

    :param str raml_file: String path to RAML file
    :param bool production: If the RAML file is meant to be production-ready
    :return: No return value if successful
    :raises LoadRamlFileError: If error occurred trying to load the RAML file
        (see ``loader.RAMLLoader``)
    :raises InvalidRamlFileError: If error occurred trying to validate the RAML
        file (see ``validate``)

    """
    return validate_raml(raml_file, production)
