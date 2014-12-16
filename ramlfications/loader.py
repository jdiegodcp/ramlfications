#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

__all__ = ["RAMLLoader", "LoadRamlFileError"]

import os

import yaml
import six


class LoadRamlFileError(Exception):
    pass


class RAMLLoader(object):
    """
    Loads the desired RAML file and returns a Python dictionary.

    Accepts either:
    - string of the file
    - unicode string of the file
    - Python file object with a ``read`` method returning either
      ``str`` or ``unicode``
    """
    def __init__(self, raml_file):
        self.raml_file = raml_file
        self.name = None

    def _get_raml_object(self):
        if self.raml_file is None:
            msg = "RAML file can not be 'None'."
            raise LoadRamlFileError(msg)

        if isinstance(self.raml_file, six.text_type) or isinstance(
                self.raml_file, str):
            return open(os.path.abspath(self.raml_file), 'r')
        elif hasattr(self.raml_file, 'read'):
            return self.raml_file
        else:
            msg = ("Can not load object '{0}': Not a basestring type or "
                   "file object".format(self.raml_file))
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

    def load(self):
        yaml.add_constructor("!include", self._yaml_include)

        try:
            with self._get_raml_object() as raml:
                loaded_raml = yaml.load(raml)
                self.name = raml.name
                return loaded_raml
        except IOError as e:
            raise LoadRamlFileError(e)

    def __repr__(self):
        return '<RAMLLoader(raml_file="{0}")>'.format(self.raml_file)
