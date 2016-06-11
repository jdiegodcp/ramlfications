# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB

from __future__ import absolute_import, division, print_function

import attr
import copy
import re

from six import MAXSIZE, iteritems, string_types, integer_types

from ramlfications.errors import UnknownDataTypeError, DataTypeValidationError
from ramlfications.utils.common import OrderedDict
from ramlfications.utils.parser import convert_camel_case

from .root import BaseContent


__type_registry = {}


def type_class(name):
    def decorator(klass):
        __type_registry[name] = klass
        return klass
    return decorator


# In order to simplify the code, we match 1:1 the raml type definition to the
# attrs object representation
def create_type(name, raml_def):
    # spec:
    # string is default type when nothing else defined
    typeexpr = raml_def.get('type', 'string')

    if typeexpr not in __type_registry:
        # we start simple, type expressions are for another commit
        raise UnknownDataTypeError(
            "{0} type expression is not supported or not defined".format(
                typeexpr))

    klass = __type_registry[typeexpr]
    # we try here to be very near the raml to avoid lots of boilerplate code to
    # convert raml spec into our internal object format
    # remaining conversion is handle via the 'convert=' parameters of the attrs
    # library

    raml_def = dict([
        (convert_camel_case(k), v) for k, v in iteritems(raml_def)
    ])
    return klass(name=name, **raml_def)


@attr.s
class BaseDataType(object):
    """
    Base class for all raml data types.

    :param string name: name of the type
    :param Content description: description for the type.
        This is a markdown Content with on the fly conversion to html using
        description.html
    :type string base type for this type
    """
    name        = attr.ib()
    description = attr.ib(default="", repr=False, convert=BaseContent)
    type        = attr.ib(default="string", repr=False)

    def validate(self, validated_objet, position_hint=None):
        """Basic default validator which does not check anything
        :param <any> validated_objet: object to be validated with the
            type definition
        :param string position_hint: position of the object in a
            more global validation. Used for proper error message
        """
        pass


###
#   helpers for ObjectType
###
@attr.s
class Property(object):
    """
    helper class for holding additional checks for object properties

    :param bool required: is this property mandatory
    :param <any> default: default value for this property
    :param <BaseDataType> data_type: type definition of the property
    """
    required        = attr.ib(default=False, repr=False)
    default         = attr.ib(default=None, repr=False)
    data_type       = attr.ib(default=None)


def create_property(property_def):
    # we remove the attributes for the property in order to keep
    # only attributes needed for the type definition
    type_def = copy.copy(property_def)
    return Property(default=type_def.pop('default', None),
                    required=type_def.pop('required', False),
                    data_type=create_type(None, type_def))


def parse_properties(properties):
    # @todo: should parse k for syntax sugar
    return OrderedDict([
        (k, create_property(v))
        for k, v in iteritems(properties)])


@type_class("object")
@attr.s
class ObjectType(BaseDataType):
    """
    Type class for object types

    :param string properties: dictionary of Properties
    """
    properties           = attr.ib(repr=False, default=None,
                                   convert=parse_properties)
    # to be implemented
    min_properties        = attr.ib(repr=False, default=0)
    max_properties        = attr.ib(repr=False, default=MAXSIZE)
    additional_properties = attr.ib(repr=False, default=None)
    pattern_properties    = attr.ib(repr=False, default=None)
    discriminator        = attr.ib(repr=False, default=None)
    discriminator_value   = attr.ib(repr=False, default=None)

    def validate(self, o, position_hint=None):
        if not isinstance(o, dict):
            raise DataTypeValidationError(
                position_hint, o,
                "requires a dictionary")
        if position_hint is None:
            position_hint = ['object']

        for k, p in iteritems(self.properties):
            if p.required and k not in o:
                raise DataTypeValidationError(
                    position_hint + [k], None,
                    "should be specified")
            v = o.get(k, p.default)
            p.data_type.validate(v, position_hint + [k])


@attr.s
class ScalarType(BaseDataType):
    """
    Type class for scalar types

    :param dictionary facets: optional facet description
    :param list enum: optional list of values that this scalar can take
    """
    facets   = attr.ib(repr=False, default=None)
    enum     = attr.ib(repr=False, default=None)

    def validate(self, s, position_hint):
        super(ScalarType, self).validate(s, position_hint)
        if self.enum is not None:
            if s not in self.enum:
                raise DataTypeValidationError(
                    position_hint, s,
                    "should be one of " + ", ".join(
                        [repr(x) for x in self.enum]))


###
#   helpers for StringType
###
def maybe_create_re(pattern):
    if pattern is not None:
        return re.compile(pattern)
    return None


@type_class("string")
@attr.s
class StringType(ScalarType):
    """
    Type class for string types

    :param regex pattern: optional regular expression the string must match
    :param min_length: optional minimum length of the string
    :param max_length: optional maximum length of the string
    """
    pattern      = attr.ib(repr=False, default=None,
                           convert=maybe_create_re)
    min_length   = attr.ib(repr=False, default=0)
    max_length   = attr.ib(repr=False, default=MAXSIZE)

    def validate(self, s, position_hint):
        super(StringType, self).validate(s, position_hint)
        if not isinstance(s, string_types):
            raise DataTypeValidationError(
                "requires a string, but got {0}".format(s))

        if self.pattern is not None:
            if not self.pattern.match(s):
                raise DataTypeValidationError(
                    position_hint, s,
                    "requires a string matching pattern {0}"
                    .format(self.pattern.pattern))

        if len(s) < self.min_length:
            raise DataTypeValidationError(
                position_hint, s,
                "requires a string with length greater than {0}"
                .format(self.min_length))

        if len(s) > self.max_length:
            raise DataTypeValidationError(
                position_hint, s,
                "requires a string with length smaller than {0}"
                .format(self.max_length))


@type_class("number")
@attr.s
class NumberType(ScalarType):
    """
    Type class for number types (JSON number)

    :param number minimum: (Optional, applicable only for parameters\
        of type number or integer) The minimum attribute specifies the\
        parameter's minimum value.
    :param number maximum: (Optional, applicable only for parameters\
        of type number or integer) The maximum attribute specifies the\
        parameter's maximum value.
    :param string format: StringType one of: int32, int64, int, long, \
        float, double, int16, int8
    :param number multiple_of: A numeric instance is valid against\
        "multiple_of" if the result of the division of the instance\
        by this keyword's value is an integer.
    """
    format       = attr.ib(repr=False, default="double")
    minimum      = attr.ib(repr=False, default=None)
    maximum      = attr.ib(repr=False, default=None)
    multiple_of  = attr.ib(repr=False, default=None)

    def validate(self, s, position_hint):
        super(NumberType, self).validate(s, position_hint)

        if not isinstance(s, integer_types + (float,)):
            raise DataTypeValidationError(
                position_hint, s,
                "requires a number")
        if self.format.startswith("int"):
            if not isinstance(s, integer_types):
                raise DataTypeValidationError(
                    position_hint, s,
                    "requires an integer")
            numbits = int(self.format[3:])
            if s & (1 << numbits) - 1  != s:
                raise DataTypeValidationError(
                    position_hint, s,
                    "does not fit in {0}".format(self.format))

        if self.minimum is not None:
            if self.minimum > s:
                raise DataTypeValidationError(
                    position_hint, s,
                    "requires to be minimum {0}".format(self.minimum))

        if self.maximum is not None:
            if self.maximum < s:
                raise DataTypeValidationError(
                    position_hint, s,
                    "requires to be maximum {0}".format(self.maximum))

        if self.multiple_of is not None:
            if not isinstance(s, integer_types):
                raise DataTypeValidationError(
                    position_hint, s,
                    "requires a integer for multiple_of")

            if (s % self.multiple_of) != 0:
                raise DataTypeValidationError(
                    position_hint, s,
                    "requires to be multiple of {0}".format(self.multiple_of))


@type_class("integer")
@attr.s
class IntegerType(NumberType):
    """
    Type class for integer types

    """
    def validate(self, s, position_hint):
        if not isinstance(s, integer_types):
            raise DataTypeValidationError(
                position_hint, s,
                "requires an integer")
        super(IntegerType, self).validate(s, position_hint)


@type_class("boolean")
@attr.s
class BooleanType(ScalarType):
    """
    Type class for boolean types

    """
    def validate(self, s, position_hint):
        if not isinstance(s, bool):
            raise DataTypeValidationError(
                position_hint, s,
                "requires a boolean")
        super(BooleanType, self).validate(s, position_hint)
