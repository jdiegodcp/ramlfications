# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function

import re

from ramlfications import parameter_tags


# To find `<< parameters >>` and `<< parameters | !foo`
PATTERN = r'(<<\s*)(?P<pname>{0}\b[^\s|]*)(\s*\|?\s*(?P<tag>!\S*))?(\s*>>)'


#####
# `<< parameter >>` substituion & parameter function tags
#####
def __replace_str_attr(param, new_value, current_str):
    """
    Replaces ``<<parameters>>`` with their assigned value, processed with \
    any function tags, e.g. ``!pluralize``.
    """
    p = re.compile(PATTERN.format(param))
    ret = re.findall(p, current_str)
    if not ret:
        return current_str
    for item in ret:
        to_replace = "".join(item[0:3]) + item[-1]
        tag_func = item[3]
        if tag_func:
            tag_func = tag_func.strip("!")
            tag_func = tag_func.strip()
            func = getattr(parameter_tags, tag_func)
            if func:
                new_value = func(new_value)
        current_str = current_str.replace(to_replace, str(new_value), 1)

    return current_str


def _substitute_parameters(obj, name, value, params):
    """
    Iterates over the named parameters of a parameter.py object to fill \
    any ``<<parameters>>`` and associated tag functions, e.g. ``!pluralize``
    """
    for s in params:
        current_value = getattr(obj, s)
        if current_value:
            if isinstance(current_value, str):
                new_value = __replace_str_attr(name, value, current_value)
                setattr(obj, s, new_value)


def __set_type_properties(named_params, obj, param):
    for n in named_params:
        attr = getattr(obj, n, None)
        if attr is None:
            attr = getattr(param, n, None)
            setattr(obj, n, attr)


def __param_filter(param, obj, attr, default=None):
    p_value = getattr(param, attr, default)
    o_value = getattr(obj, attr)
    return p_value == o_value


def _inherit_type_properties(obj, params, named_params):
    for param in params:
        set_type = True
        if type(obj).__name__ == 'Body':
            set_type = __param_filter(param, obj, "mime_type")
        if set_type:
            __set_type_properties(named_params, obj, param)
