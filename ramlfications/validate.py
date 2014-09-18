#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB


VALID_RAML_VERSIONS = ["0.8"]


class ValidateRAMLError(Exception):
    pass


class ValidateRAML(object):
    def __init__(self, raml_file):
        self.raml = raml_file

    def validate_raml_header(self):
        with open(self.raml, 'r') as r:
            raml_header = r.readline().split('\n')[0]
            raml_def, version = raml_header.split()
            if raml_def != "#%RAML":
                msg = "Not a valid RAML header: {0}.".format(raml_def)
                raise ValidateRAMLError(msg)
            if version not in VALID_RAML_VERSIONS:
                msg = "Not a valid version of RAML: {0}.".format(version)
                raise ValidateRAMLError(msg)

            return raml_def, version
