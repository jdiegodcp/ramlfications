#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function

from collections import defaultdict

try:
    from collections import OrderedDict
except ImportError:  # pragma: no cover
    from ordereddict import OrderedDict  # pragma: no cover

from .parser import APIRoot


def _count_parents(node, count):
    if node.parent:
        count += 1
        return _count_parents(node.parent, count)
    else:
        return count


def get_tree(api):
    _resources = api.resources
    resources = defaultdict(list)
    for k, v in list(_resources.items()):
        resources[v.path].append((v.method.upper(), v))

    return resources


def order_resources(resources):
    return OrderedDict(sorted(resources.items(), key=lambda t: t[0]))


def _create_space(v):
    for node in v:
        space_count = _count_parents(node[1], count=0)
        space = "  " * space_count
    return space


def verbose_mapping(verbose_level):
    return {
        0: _level_zero,
        1: _level_one,
        2: _level_two,
        3: _level_three
    }[verbose_level]


def color_mapping(color):
    return {
        "light": (39, 32, 33, 34, 31),
        "dark": (30, 35, 36, 30, 35)
    }[color]


def _base(space, k, color):
    pipe = '\033[1;{0}m{1}\033[1;m'.format(color[0], "|")
    endpoint = space + "– {0}".format(k)
    print(pipe + '\033[1;{0}m{1}\033[1;m'.format(color[2], endpoint))


def __print(space, color, msg):
    pipe = '\033[1;{0}m{1}\033[1;m'.format(color[0], "|")
    _msg = pipe + space + '\033[1;{0}m{1}\033[1;m'.format(color[4], msg)
    print(_msg)


def _method(space, node, color):
    pipe = '\033[1;{0}m{1}\033[1;m'.format(color[0], "|")
    method = space + "  ⌙ {0}".format(node[0])
    print(pipe + '\033[1;{0}m{1}\033[1;m'.format(color[3], method))


def _params(space, node, color, desc):
    if node[1].query_params:
        __print(space + '     ', color, "Query Params")
        for q in node[1].query_params:
            if desc:
                desc = ": " + q.display_name
            else:
                desc = ''
            __print(space + '      ⌙ ', color, q.name + desc)
    if node[1].uri_params:
        __print(space + '     ', color, "URI Params")
        for u in node[1].uri_params:
            if desc:
                desc = ": " + u.display_name
            else:
                desc = ''
            __print(space + '      ⌙ ', color, u.name + desc)
    if node[1].form_params:
        __print(space + '     ', color, "Form Params")
        for f in node[1].form_params:
            if desc:
                desc = ": " + f.display_name
            else:
                desc = ''
            __print(space + '      ⌙ ', color, f.name + desc)


def _level_zero(ordered_resources, color):
    for k, v in list(ordered_resources.items()):
        space = _create_space(v)
        pipe = '\033[1;{0}m{1}\033[1;m'.format(color[0], "|")
        endpoint = space + "– {0}".format(k)
        print(pipe + '\033[1;{0}m{1}\033[1;m'.format(color[2], endpoint))


def _level_one(ordered_resources, color):
    for k, v in list(ordered_resources.items()):
        space = _create_space(v)
        _base(space, k, color)
        for node in v:
            _method(space, node, color)


def _level_two(ordered_resources, color):
    for k, v in list(ordered_resources.items()):
        space = _create_space(v)
        _base(space, k, color)
        for node in v:
            _method(space, node, color)
            _params(space, node, color, False)


def _level_three(ordered_resources, color):
    for k, v in list(ordered_resources.items()):
        space = _create_space(v)
        _base(space, k, color)
        for node in v:
            _method(space, node, color)
            _params(space, node, color, True)


def pprint_tree(api, ordered_resources, print_color, verbosity):
    color = color_mapping(print_color)

    print("\033[1;{0}m{1}\033[1;m".format(color[0], '=' * len(api.title)))
    print('\033[1;{0}m{1}\033[1;m'.format(color[1], api.title))
    print("\033[1;{0}m{1}\033[1;m".format(color[0], '=' * len(api.title)))
    print('\033[1;{0}m{1}{2}\033[1;m'.format(color[1], "Base URI: ",
                                             api.base_uri))

    verbose_mapping(verbosity)(ordered_resources, color)


def ttree(load_obj, light, verbosity):  # pragma: no cover
    api = APIRoot(load_obj)
    resources = get_tree(api)
    ordered_resources = order_resources(resources)
    pprint_tree(api, ordered_resources, light, verbosity)
