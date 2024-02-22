# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function

import re


def validate_mime_type(value):
    """
    Assert a valid MIME media type for request/response body.
    """
    regex_str = re.compile(r"application\/[A-Za-z.-0-1]*?(json|xml)")
    match = re.search(regex_str, value)
    return match
