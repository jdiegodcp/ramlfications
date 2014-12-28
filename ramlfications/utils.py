#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

import collections
import functools
import re


def find_params(string):
    """
    Parses out the parameter name from ``<<parameterName>>`` that is
    used in Resource Types and Traits.
    """
    # TODO: ignoring humanizers for now
    match = re.findall(r"<<(.*?)>>", string)
    ret = set()
    for m in match:
        param = "<<{0}>>".format(m.split("|")[0].strip())
        ret.add(param)
    return list(ret)


def fill_reserved_params(resource, string):
    if "<<resourcePathName>>" in string:
        string = string.replace("<<resourcePathName>>", resource.name[1:])
    if "<<resourcePath>>" in string:
        string = string.replace("<<resourcePath>>", resource.path)

    return string


class memoized(object):
    """
    Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    """

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)
