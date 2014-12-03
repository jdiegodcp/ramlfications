#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

__all__ = ["RAMLLoader", "LoadRamlFileError"]

import os

import yaml


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

        if isinstance(self.raml_file, str):
            return file(os.path.abspath(self.raml_file), 'r')
        elif isinstance(self.raml_file, unicode):
            return file(os.path.abspath(self.raml_file), 'r')
        elif isinstance(self.raml_file, file):
            return self.raml_file

    def _yaml_include(self, loader, node):
        """
        Adds the ability to follow ``!include`` directives within
        RAML Files.
        """
        # Get the path out of the yaml file
        file_name = os.path.join(os.path.dirname(loader.name), node.value)

        with open(file_name) as inputfile:
            return yaml.load(inputfile)

    # Instead of having a load function it would probably be more
    # Pythonic if you could implement the __ functions to make RAML
    # files work with "with" like:
    #
    # with RAMLLoader(filename) as f:
    #   print f
    # LR: Nah. YAML & JSON loaders don't work like that. It's always called
    # like yaml.load(fileobject) or json.dumps(filename).
    def load(self):
        yaml.add_constructor("!include", self._yaml_include)

        try:
            raml = self._get_raml_object()
            self.name = raml.name
            return yaml.load(raml)
        except IOError as e:
            raise LoadRamlFileError(e)
        else:
            raml.close()

    def __repr__(self):
        return '<RAMLLoader(raml_file="{0}")>'.format(self.raml_file)
