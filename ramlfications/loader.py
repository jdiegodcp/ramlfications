#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

__all__ = ["RAMLLoader", "LoadRamlFileError"]

import os

import yaml


class LoadRamlFileError(Exception):
    pass


class RAMLLoader(object):
    def __init__(self, raml_file):
        self.raml_file = raml_file

    def _get_abs_path(self):
        if self.raml_file is None:
            msg = "RAML file can not be 'None'."
            raise LoadRamlFileError(msg)
        return os.path.abspath(self.raml_file)

    def _yaml_include(self, loader, node):
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
    def load(self):
        yaml.add_constructor("!include", self._yaml_include)

        try:
            raml = self._get_abs_path()
            with open(raml) as r:
                return yaml.load(r)
        except IOError as e:
            raise LoadRamlFileError(e)

    def __repr__(self):
        return '<RAMLLoader(raml_file="{0}")>'.format(self.raml_file)


def load(raml_file):
    return RAMLLoader(raml_file).load()
