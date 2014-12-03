#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

import os
import unittest
import sys

PAR_DIR = os.path.abspath(os.path.dirname(__file__))
EXAMPLES = os.path.join(PAR_DIR + '/data/examples/')
VALIDATE = os.path.join(PAR_DIR + '/data/validate/')


class BaseTestCase(unittest.TestCase):
    maxDiff = None

    # This helper function might already exist in unnittest.
    def assertItemInList(self, item, items):
        self.assertTrue(item in items)

    # Is this even properly aligned? Is this code ever executed?
    # Allow for py3.x compatability
    if not hasattr(unittest.TestCase, 'assertIsInstance'):
        def assertIsInstance(self, item, object):
            self.assertTrue(isinstance(item, object))

    # Allow for py2.6 compatability
    if not hasattr(unittest.TestCase, 'assertDictEqual'):
        # assertEqual uses for dicts
        def assertDictEqual(self, d1, d2, msg=None):
            for k, v1 in d1.iteritems():
                self.assertTrue(k in d2)
                v2 = d2[k]
                self.assertEqual(v1, v2, msg)
            return True

    if not hasattr(unittest.TestCase, 'assertIsNotNone'):
        def assertIsNotNone(self, value, *args):
            self.assertNotEqual(value, None, *args)

    if not hasattr(unittest.TestCase, 'assertListEqual'):
        def assertListEqual(self, list1, list2):
            self.assertEqual(len(list1), len(list2))
            self.assertEqual(sorted(list1), sorted(list2))

    if not hasattr(unittest.TestCase, 'assertIsNone'):
        def assertIsNone(self, item):
            self.assertEqual(item, None)

    # py2.6 assertRaises compatibility
    def assert_raises(self, exception, function, **kw):
        if sys.version_info[:2] == (2, 6):
            try:
                function(**kw)
            except exception as e:
                return e.message
            except Exception as ee:
                return ee.message
            else:
                self.fail("No exception thrown")
        else:
            with self.assertRaises(exception) as e:
                function(**kw)
            return e.exception
