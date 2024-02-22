# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB
# from __future__ import absolute_import, division, print_function

import os

PAR_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(PAR_DIR, 'data')
RAML_08 = os.path.join(DATA_DIR, 'raml_08')
RAML_10 = os.path.join(DATA_DIR, 'raml_10')
VALIDATE_08 = os.path.join(RAML_08, 'validate')
FIXTURES = os.path.join(PAR_DIR + '/data/fixtures/')
UPDATE = os.path.join(PAR_DIR + '/data/update/')
JSONREF = os.path.join(PAR_DIR + '/data/jsonref/')

# examples from github.com/raml-org/raml-examples
RAML_ORG_EXAMPLES = os.path.join(DATA_DIR, 'ramlorgexamples')


DATA_TYPE_OBJECT_ATTRS = [
    'additional_properties', 'annotation', 'config', 'default',
    'description', 'discriminator', 'discriminator_value',
    'display_name', 'errors', 'example', 'examples', 'facets',
    'max_properties', 'min_properties', 'name', 'properties',
    'raml_version', 'raw', 'root', 'schema', 'type', 'usage', 'xml'
]


class AssertNotSetError(Exception):
    pass


# Helper function to iterate over all properties that should not be
# set on an object
def assert_not_set(obj, properties):
    for p in properties:
        if getattr(obj, p):
            msg = ("Attribute '{0}' is set in object '{1}' when should "
                   "not be.".format(p, obj))
            raise AssertNotSetError(msg)


def assert_not_set_raises(obj, properties):
    for p in properties:
        try:
            getattr(obj, p)
            msg = ("Attribute '{0}' is set in object '{1}' when it "
                   "should not be.".format(p, obj))
            raise AssertNotSetError(msg)
        # this check _should_ throw an attr error
        except AttributeError:
            continue


def assert_set_none(obj, properties):
    for p in properties:
        assert not getattr(obj, p)
