#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

__all__ = ["RAMLLoader", "LoadRamlFileError"]

import os

import yaml
import six


class LoadRamlFileError(Exception):
    pass


# Better name for a RAML object?
class RAMLDict(object):
    """
    Object representing the loaded RAML file.

    :param str name: name of RAML File
    :param str raml_file: string path to the RAML file location
    :param dict data: data parsed by YAML library
    """
    def __init__(self, name, raml_file, data):
        self.name = name
        self.raml_file = raml_file
        self.data = data

    # Remove this function
    def __repr__(self):
        return '<RAMLDict(name="{0}")>'.format(self.name)


class RAMLLoader(object):
    """
    Extends YAML to load RAML files with ``!include`` tags and preserve
    order.
    """
    def _get_raml_object(self, raml_file):
        if raml_file is None:
            msg = "RAML file can not be 'None'."
            raise LoadRamlFileError(msg)

        if isinstance(raml_file, six.text_type) or isinstance(
                raml_file, str):
            return open(os.path.abspath(raml_file), 'r')
        elif hasattr(raml_file, 'read'):
            return raml_file
        else:
            msg = ("Can not load object '{0}': Not a basestring type or "
                   "file object".format(raml_file))
            raise LoadRamlFileError(msg)

    def _yaml_include(self, loader, node):
        """
        Adds the ability to follow ``!include`` directives within
        RAML Files.
        """
        # Get the path out of the yaml file
        file_name = os.path.join(os.path.dirname(loader.name), node.value)

        with open(file_name) as inputfile:
            return yaml.load(inputfile)

    # Get rid of state in the Loader class and either return a tuple
    # or define a new RamlFile class and return an instance here
    def load(self, raml_file):
        """
        Loads the desired RAML file and returns an instance of ``RAMLDict``.

        :param str raml_file: string path to RAML file
        :param unicode raml_file: unicode string path to RAML file
        :param file raml_file: file-like object of RAML file \
            (must have a ``read`` method)
        :return: An instance of ``RAMLDict``
        :rtype: ``RAMLDict``
        """
        yaml.add_constructor("!include", self._yaml_include)

        try:
            with self._get_raml_object(raml_file) as raml:
                loaded_raml = yaml.load(raml)
                return RAMLDict(raml.name, raml_file, loaded_raml)
        except IOError as e:
            raise LoadRamlFileError(e)

    # Remove this function
    def __repr__(self):
        return '<RAMLLoader(raml_file="{0}")>'.format(self.raml_file)
