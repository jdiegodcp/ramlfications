#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

import os

import yaml


class RAMLLoaderError(Exception):
    pass


class RAMLLoader(object):
    def __init__(self, raml_file):
        yaml.add_constructor("!include", self.__yaml_include)
        self.raml = self.__raml(raml_file)

    def __yaml_include(self, loader, node):
        # Get the path out of the yaml file
        file_name = os.path.join(os.path.dirname(loader.name), node.value)

        with open(file_name) as inputfile:
            return yaml.load(inputfile)

    def __raml(self, raml_file):
        try:
            return yaml.load(open(raml_file))
        except IOError as e:
            raise RAMLLoaderError(e)
