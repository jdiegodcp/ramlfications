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


class BaseRAMLParserError(BaseRAMLError):
    pass


class InvalidRootNodeError(BaseRAMLParserError):
    pass


class InvalidResourceNodeError(BaseRAMLParserError):
    pass


class InvalidParameterError(BaseRAMLParserError):
    def __init__(self, message, parameter):
        super(InvalidParameterError, self).__init__(message)
        self.parameter = parameter


class InvalidSecuritySchemeError(BaseRAMLParserError):
    pass


#####
# Loader Exceptions
#####

class LoadRAMLError(BaseRAMLError):
    pass


#####
# Update MIME Media Type Exception
#####

class MediaTypeError(BaseRAMLError):
    pass


class InvalidVersionError(BaseRAMLError):
    pass


class UnknownDataTypeError(BaseRAMLError):
    pass


class DataTypeValidationError(BaseRAMLError):
    """A common validator type for data type validation errors

    :param list position_hint: path in the validated object where the
        error happens. can be None.
    :param <any> value: value of the object which had a problem:
        repl of this object will be present in the message
    :param <any> message: message to provide to the user
    """
    def __init__(self, position_hint, value, message):
        self.position_hint = position_hint
        self.value = value
        if position_hint is None:
            position_hint = []
        super(DataTypeValidationError, self).__init__(
            "{0}: {1}, but got: {2}".format(
                ".".join(position_hint), message, value
            ))
