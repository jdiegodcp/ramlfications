#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

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
