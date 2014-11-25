#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function


from ramlfications.utils import find_params
from .base import BaseTestCase


class TestUtils(BaseTestCase):
    def test_find_params_non_humanized(self):
        string = ("Return <<resourcePathName>> that have their "
                  "<<queryParamName>> matching the given value")

        exp_params = ["<<resourcePathName>>", "<<queryParamName>>"]

        params = find_params(string)
        assert len(params) == len(exp_params)
        assert sorted(params) == sorted(exp_params)

    def test_find_params_humanized(self):
        string = ("Return <<resourcePathName| !singularize>> that have "
                  "their <<queryParamName |!pluralize>> matching the "
                  "given value")

        exp_params = ["<<resourcePathName>>", "<<queryParamName>>"]

        params = find_params(string)
        assert len(params) == len(exp_params)
        assert sorted(params) == sorted(exp_params)
