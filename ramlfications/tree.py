#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function


from collections import defaultdict

try:
    from collections import OrderedDict
except ImportError:  # pragma: no cover
    from ordereddict import OrderedDict  # pragma: no cover

import sys

from ansi.colour import fg

from .parser import APIRoot


# "light" font for dark background screens
# "dark" font for light background screens
COLOR_MAP = {
    "light": (fg.white,
              fg.yellow,
              fg.brightgreen,
              fg.brightblue,
              fg.brightcyan),
    "dark": (fg.black,
             fg.darkgrey,
             fg.darkgrey,
             fg.magenta,
             fg.blue)
}


def _get_node_level(node, count):
    if node.parent:
        count += 1
        return _get_node_level(node.parent, count)
    else:
        return count


def _get_tree(api):
    _resources = api.resources
    resources = defaultdict(list)
    # Can _resources be None? If yes, the next line crashes.
    # LR: hmm if resources are none, then no endpoints are defined in RAML
    # pretty much required
    # TODO: add validation if no resources are defined
    for k, v in list(_resources.items()):
        resources[v.path].append((v.method.upper(), v))

    return resources


def _order_resources(resources):
    return OrderedDict(sorted(resources.items(), key=lambda t: t[0]))


def _create_space(v):
    for node in v:
        space_count = _get_node_level(node[1], count=0)
        space = "  " * space_count
    return space


def _set_ansi(string, screen_color, line_color):
    if screen_color:
        return COLOR_MAP[screen_color][line_color](string)
    return string


def _print_line(sp, msg, color, line_color):
    pipe = _set_ansi("|", color, 0)
    output = pipe + sp + _set_ansi(msg, color, line_color) + "\n"
    sys.stdout.write(output)


def _return_param_type(node):
    params = OrderedDict()
    if node[1].query_params:
        params["Query Params"] = node[1].query_params
    if node[1].uri_params:
        params["URI Params"] = node[1].uri_params
    if node[1].form_params:
        params["Form Params"] = node[1].form_params
    return params


def _params(space, node, color, desc):
    params = _return_param_type(node)
    for k, v in list(params.items()):
        _print_line(space + '     ', k, color, 4)
        for p in v:
            if desc:
                desc = ": " + p.display_name
            else:
                desc = ''
            _print_line(space + '      ⌙ ',  p.name + desc, color, 4)


def _print_verbosity(ordered_resources, color, verbosity):
    for k, v in list(ordered_resources.items()):
        space = _create_space(v)
        _print_line(space, "- " + k, color, 2)
        if verbosity > 0:
            for node in v:
                _print_line(space, "  ⌙ " + node[0], color, 3)
                if verbosity > 1:
                    desc = verbosity == 3
                    _params(space, node, color, desc)


def _print_metadata(api, color):
    head = _set_ansi("=" * len(api.title), color, 0) + "\n"
    head += _set_ansi(api.title, color, 1) + "\n"
    head += _set_ansi("=" * len(api.title), color, 0) + "\n"
    head += _set_ansi("Base URI: " + api.base_uri, color, 1) + "\n"

    sys.stdout.write(head)


def pprint_tree(api, ordered_resources, print_color, verbosity):
    # Verify layout of arguments. For example, print_color must be a list
    # of exactly length three. Then verify that each list element is an
    # integer(?) too.

    # LR - print_color is verified in __main__.py with the use of ``click``
    _print_metadata(api, print_color)
    _print_verbosity(ordered_resources, print_color, verbosity)


def ttree(load_obj, color, output, verbosity):  # pragma: no cover
    # Function below can throw exceptions. Document these.
    # LR: Any exceptions are caught in the __main__.py, which is
    # the entry point for this module.
    api = APIRoot(load_obj)
    resources = _get_tree(api)
    ordered_resources = _order_resources(resources)

    if output:
        sys.stdout = output  # file is opened via @click from __main__.py
        pprint_tree(api, ordered_resources, color, verbosity)
        output.close()
    else:
        pprint_tree(api, ordered_resources, color, verbosity)
