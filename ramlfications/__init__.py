# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function

__author__ = "Lynn Root"
__version__ = "0.1.0a1"
__license__ = "Apache 2.0"


from ramlfications.config import setup_config
from ramlfications.parser import parse_raml

from ramlfications._helpers import load_file, load_string


def load(raml_file):
    """
    Module helper function to load a RAML File using \
    :py:class:`.loader.RAMLLoader`.

    :param str raml_file: String path to RAML file
    :return: loaded RAML
    :rtype: dict
    :raises LoadRAMLError: If error occurred trying to load the RAML file
    """
    return load_file(raml_file)


def loads(raml_string):
    """
    Module helper function to load a RAML File using \
    :py:class:`.loader.RAMLLoader`.

    :param str raml_string: String of RAML data
    :return: loaded RAML
    :rtype: dict
    :raises LoadRAMLError: If error occurred trying to load the RAML file
    """
    return load_string(raml_string)


def parse(raml, config_file=None):
    """
    Module helper function to parse a RAML File.  First loads the RAML file
    with :py:class:`.loader.RAMLLoader` then parses with
    :py:func:`.parser.parse_raml` to return a :py:class:`.raml.RAMLRoot`
    object.

    :param raml: Either string path to the RAML file, a file object, or \
        a string representation of RAML.
    :param str config_file:  String path to desired config file, if any.
    :return: parsed API
    :rtype: RAMLRoot
    :raises LoadRAMLError: If error occurred trying to load the RAML file
        (see :py:class:`.loader.RAMLLoader`)
    :raises RAMLParserError: If error occurred during parsing of RAML file
        (see :py:class:`.raml.RAMLRoot`)
    :raises InvalidRamlFileError: RAML file is invalid according to RAML \
        `specification <http://raml.org/spec.html>`_.
    """
    loader = load(raml)
    config = setup_config(config_file)
    return parse_raml(loader, config)


def validate(raml, config_file=None):
    """
    Module helper function to validate a RAML File.  First loads \
    the RAML file \
    with :py:class:`.loader.RAMLLoader` then validates with \
    :py:func:`.validate.validate_raml`.

    :param str raml: Either string path to the RAML file, a file object, \or
        a string representation of RAML.
    :param str config_file:  String path to desired config file, if any.
    :return: No return value if successful
    :raises LoadRAMLError: If error occurred trying to load the RAML file
        (see :py:class:`.loader.RAMLLoader`)
    :raises InvalidRamlFileError: If error occurred trying to validate the RAML
        file (see :py:mod:`.validate`)

    """
    loader = load(raml)
    config = setup_config(config_file)
    config["validate"] = True
    parse_raml(loader, config)
