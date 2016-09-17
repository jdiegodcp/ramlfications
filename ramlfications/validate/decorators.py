# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB

from __future__ import absolute_import, division, print_function


from ramlfications.errors import BaseRAMLError


# TODO: maybe move this to validate/utils.py
def collecterrors(func):
    def func_wrapper(inst, attr, value):
        try:
            func(inst, attr, value)
        except BaseRAMLError as e:
            inst.errors.append(e)

    return func_wrapper
