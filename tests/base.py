#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

import unittest


class BaseTestCase(unittest.TestCase):
    maxDiff = None

    def assertItemInList(self, item, items):
        self.assertTrue(item in items)

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
