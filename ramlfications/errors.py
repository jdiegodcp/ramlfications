# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function


#####
# Validation Exceptions
#####


class InvalidRAMLError(Exception):
    def __init__(self, errors):
        super(InvalidRAMLError, self).__init__(
            "Validation errors were found.")
        self.errors = errors

    def __str__(self):
        output = "\n"
        for e in self.errors:
            output += "\t{0}: {1}\n".format(e.__class__.__name__, e)
        # Strip last newline
        return output[:-1]


class BaseRAMLError(Exception):
    pass


class InvalidRootNodeError(BaseRAMLError):
    pass


class InvalidResourceNodeError(BaseRAMLError):
    pass


class InvalidParameterError(BaseRAMLError):
    def __init__(self, message, parameter):
        super(InvalidParameterError, self).__init__(message)
        self.parameter = parameter


class InvalidSecuritySchemeError(BaseRAMLError):
    pass


#####
# Loader Exceptions
#####

class LoadRAMLError(Exception):
    pass


#####
# Update MIME Media Type Exception
#####

class MediaTypeError(Exception):
    pass


class InvalidVersionError(Exception):
    pass
