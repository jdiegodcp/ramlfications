# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB
from __future__ import absolute_import, division, print_function

import os

PAR_DIR = os.path.abspath(os.path.dirname(__file__))
EXAMPLES = os.path.join(PAR_DIR + '/data/examples/')
VALIDATE = os.path.join(PAR_DIR + '/data/validate/')
FIXTURES = os.path.join(PAR_DIR + '/data/fixtures/')
UPDATE = os.path.join(PAR_DIR + '/data/update/')
JSONREF = os.path.join(PAR_DIR + '/data/jsonref/')

V020EXAMPLES = os.path.join(PAR_DIR + '/data/v020examples/')


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
