#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

import os

import yaml


class RAMLLoaderError(Exception):
    pass


class RAMLLoader(object):
    def __init__(self, raml_file):
        self.raml_file = os.path.abspath(raml_file)

    def _yaml_include(self, loader, node):
        # Get the path out of the yaml file
        file_name = os.path.join(os.path.dirname(loader.name), node.value)

        with open(file_name) as inputfile:
            return yaml.load(inputfile)

    def load(self):
        yaml.add_constructor("!include", self._yaml_include)

        try:
            return yaml.load(open(self.raml_file))
        except IOError as e:
            raise RAMLLoaderError(e)

    def __repr__(self):
        return '<RAMLLoader(raml_file="{0}")>'.format(self.raml_file)


def load(raml_file):
    return RAMLLoader(raml_file).load()
