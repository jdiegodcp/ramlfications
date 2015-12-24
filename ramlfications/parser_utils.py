# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function


from six import itervalues, iterkeys

from .parameters import SecurityScheme
from .utils import _get_scheme
# functions used to parse the same shit in parser.py


# resource, resource type
def security_schemes(secured, root):
    """Set resource's assigned security scheme objects."""
    if secured:
        secured_objs = []
        for item in secured:
            assigned_scheme = _get_scheme(item, root)
            if assigned_scheme:
                raw_data = list(itervalues(assigned_scheme))[0]
                scheme = SecurityScheme(
                    name=list(iterkeys(assigned_scheme))[0],
                    raw=raw_data,
                    type=raw_data.get("type"),
                    described_by=raw_data.get("describedBy"),
                    desc=raw_data.get("description"),
                    settings=raw_data.get("settings"),
                    config=root.config,
                    errors=root.errors
                )
                secured_objs.append(scheme)
        return secured_objs
    return None
