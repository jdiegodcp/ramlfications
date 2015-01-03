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


def fill_reserved_params(resource, string):
    """
    Replaces parameters that are reserved according to the RAML spec.

    :param Resource resource: Resource object to grab relevant information.
    :param str string: string to modify
    :returns: Modified string with the relevant replaced information.
    """
    if "<<resourcePathName>>" in string:
        string = string.replace("<<resourcePathName>>", resource.name[1:])
    if "<<resourcePath>>" in string:
        string = string.replace("<<resourcePath>>", resource.path)

    return string
