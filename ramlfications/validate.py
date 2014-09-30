#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB


from .parser import APIRoot


VALID_RAML_VERSIONS = ["0.8"]


class RAMLValidationError(Exception):
    pass


class ValidateRAML(object):
    def __init__(self, raml_file):
        self.raml_file = raml_file
        self.api = APIRoot(raml_file)

    def raml_header(self):
        with open(self.raml_file, 'r') as r:
            raml_header = r.readline().split('\n')[0]
            raml_def, version = raml_header.split()
            if raml_def != "#%RAML":
                msg = "Not a valid RAML header: {0}.".format(raml_def)
                raise RAMLValidationError(msg)
            if version not in VALID_RAML_VERSIONS:
                msg = "Not a valid version of RAML: {0}.".format(version)
                raise RAMLValidationError(msg)

            return raml_def, version
