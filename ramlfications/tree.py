# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function

from ramlfications.utils.common import OrderedDict
import sys

from six import iteritems, itervalues
from termcolor import colored

from .config import setup_config
from .parser import parse_raml

COLOR_MAP = {
    "light": (('white', None),
              ('yellow', None),
              ('green', 'bold'),
              ('blue', 'bold'),
              ('cyan', 'bold')),
    "dark": (('grey', None),
             ('grey', 'bold'),
             ('grey', 'bold'),
             ('magenta', None),
             ('blue', None))
}


def _get_node_level(node, count):
    if node.parent:
        count += 1
        return _get_node_level(node.parent, count)
    else:
        return count


def _get_tree(api):
    resources = OrderedDict()
    for r in api.resources:
        if r.method is not None:
            key = r.method.upper() + " " + r.path
        else:
            key = r.path
        resources[key] = r

    return resources


def _create_space(v):
    space_count = _get_node_level(v, count=0)
    space = "  " * space_count
    return space


def _set_ansi(string, screen_color, line_color):
    if screen_color:
        color, attr = COLOR_MAP[screen_color][line_color]
        if attr:
            return colored(string, color, attrs=[attr])
        return colored(string, color)
    return string


def _print_line(sp, msg, color, line_color):
    pipe = _set_ansi("|", color, 2)
    output = pipe + _set_ansi(sp + msg, color, line_color) + "\n"
    sys.stdout.write(output)


def _return_param_type(node):
    params = OrderedDict()
    if node.query_params:
        params["Query Params"] = node.query_params
    if node.uri_params:
        params["URI Params"] = node.uri_params
    if node.form_params:
        params["Form Params"] = node.form_params
    return params


def _params(space, node, color, desc):
    params = _return_param_type(node)
    for k, v in list(iteritems(params)):
        _print_line(space + '     ', k, color, 4)
        for p in v:
            if desc:
                desc = ": " + p.display_name
            else:
                desc = ''
            _print_line(space + '      ⌙ ', p.name + desc, color, 4)


def _print_verbosity(resources, color, verbosity):
    for r in list(itervalues(resources)):
        space = _create_space(r)
        _print_line(space, "- " + r.path, color, 2)
        if verbosity > 0:
            if r.method:
                _print_line(space, "  ⌙ " + r.method.upper(), color, 3)
            else:
                continue
            if verbosity > 1:
                desc = verbosity == 3
                _params(space, r, color, desc)


def _print_metadata(api, color):
    if not api.title:
        api.title = "MISSING TITLE"
    head = _set_ansi("=" * len(api.title), color, 0) + "\n"
    head += _set_ansi(api.title, color, 1) + "\n"
    head += _set_ansi("=" * len(api.title), color, 0) + "\n"
    head += _set_ansi("Base URI: " + api.base_uri, color, 1) + "\n"

    sys.stdout.write(head)


def _print_tree(api, ordered_resources, print_color, verbosity):
    _print_metadata(api, print_color)
    _print_verbosity(ordered_resources, print_color, verbosity)


def tree(load_obj, color, output, verbosity, validate, config):  # NOCOV
    """
    Create a tree visualization of given RAML file.

    :param dict load_obj: Loaded RAML File
    :param str color: ``light``, ``dark`` or ``None`` (default) for the color
        output
    :param str output: Path to output file, if given
    :param str verbosity: Level of verbosity to print out
    :return: ASCII Tree representation of API
    :rtype: stdout to screen or given file name
    :raises InvalidRootNodeError: API metadata is invalid according to RAML \
        `specification <http://raml.org/spec.html>`_.
    :raises InvalidResourceNodeError: API resource endpoint is invalid \
        according to RAML `specification <http://raml.org/spec.html>`_.
    :raises InvalidParameterError: Named parameter is invalid \
        according to RAML `specification <http://raml.org/spec.html>`_.
    """
    config = setup_config(config)
    api = parse_raml(load_obj, config)
    resources = _get_tree(api)

    if output:
        sys.stdout = output  # file is opened via @click from __main__.py
        _print_tree(api, resources, color, verbosity)
        output.close()
    else:
        _print_tree(api, resources, color, verbosity)
