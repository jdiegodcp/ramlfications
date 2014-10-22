#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from collections import defaultdict, OrderedDict

from parser import APIRoot


AVAIL_METHODS = ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']


class TreeNode(object):  # pragma: no cover
    def __init__(self, name, methods=[], children=[]):
        self.name = name
        self.children = children
        self.methods = methods

    def __str__(self, level=0):
        # color = 32 + level
        ret = "  |" if level > 0 else ""
        ret = ret + "–" * level + repr(self.name) + "\n"

        # if self.methods:
        #     for m in self.methods:
        #         ret += "  |  " + " " * level + "⌙ " + m + "\n"

        for child in self.children:
            ret += child.__str__()

        # return '\033[1;{0}m{1}\033[1;m'.format(color, ret)

        return ret

    def __repr__(self):
        return '%s' % self.name


def _count_parents(node, count):
    if node.parent:
        count += 1
        return _count_parents(node.parent, count)
    else:
        return count


def get_tree(api):
    _nodes = api.nodes
    nodes = defaultdict(list)
    for k, v in list(_nodes.items()):
        nodes[v.path].append((v.method.upper(), v))

    return nodes


def order_nodes(nodes):
    return OrderedDict(sorted(nodes.items(), key=lambda t: t[0]))


def count_parents(nodes):
    for k, v in list(nodes.items()):
        for node in v:
            print _count_parents(node[1], count=0)


def print_1_verbose(api, ordered_nodes, color):
    for k, v in list(ordered_nodes.items()):
        for node in v:
            space_count = _count_parents(node[1], count=0)
            space = "  " * space_count
        pipe = '\033[1;{0}m{1}\033[1;m'.format(color[0], "|")
        endpoint = space + "– {0}".format(k)
        print pipe + '\033[1;{0}m{1}\033[1;m'.format(color[2], endpoint)
        for node in v:
            method = space + "  ⌙ {0}".format(node[0])
            print pipe + '\033[1;{0}m{1}\033[1;m'.format(color[3], method)


def print_2_verbose(api, ordered_nodes, color):
    for k, v in list(ordered_nodes.items()):
        for node in v:
            space_count = _count_parents(node[1], count=0)
            space = "  " * space_count
        pipe = '\033[1;{0}m{1}\033[1;m'.format(color[0], "|")
        endpoint = space + "– {0}".format(k)
        print pipe + '\033[1;{0}m{1}\033[1;m'.format(color[2], endpoint)
        for node in v:
            method = space + "  ⌙ {0}".format(node[0])
            print pipe + '\033[1;{0}m{1}\033[1;m'.format(color[3], method)
            if node[1].query_params:
                print pipe + space + '     \033[1;{0}m{1}\033[1;m'.format(
                    color[4], "Query Params")
                for q in node[1].query_params:
                    print pipe + space + '      ⌙ \033[1;{0}m{1}\033[1;m'.format(
                        color[4], q.name)
            if node[1].uri_params:
                print pipe + space + '     \033[1;{0}m{1}\033[1;m'.format(
                    color[4], "URI Params")
                for u in node[1].uri_params:
                    print pipe + space + '      ⌙ \033[1;{0}m{1}\033[1;m'.format(
                        color[4], u.name)
            if node[1].form_params:
                print pipe + space + '     \033[1;{0}m{1}\033[1;m'.format(
                    color[4], "URI Params")
                for f in node[1].form_params:
                    print pipe + space + '      ⌙ \033[1;{0}m{1}\033[1;m'.format(
                        color[4], f.name)


def print_3_verbose(api, ordered_nodes, color):
    for k, v in list(ordered_nodes.items()):
        for node in v:
            space_count = _count_parents(node[1], count=0)
            space = "  " * space_count
        pipe = '\033[1;{0}m{1}\033[1;m'.format(color[0], "|")
        endpoint = space + "– {0}".format(k)
        print pipe + '\033[1;{0}m{1}\033[1;m'.format(color[2], endpoint)
        for node in v:
            method = space + "  ⌙ {0}".format(node[0])
            print pipe + '\033[1;{0}m{1}\033[1;m'.format(color[3], method)
            if node[1].query_params:
                print pipe + space + '     \033[1;{0}m{1}\033[1;m'.format(
                    color[4], "Query Params")
                for q in node[1].query_params:
                    print pipe + space + '      ⌙ \033[1;{0}m{1}\033[1;m'.format(
                        color[4], q.name) + ": {0}".format(q.display_name)
            if node[1].uri_params:
                print pipe + space + '     \033[1;{0}m{1}\033[1;m'.format(
                    color[4], "URI Params")
                for u in node[1].uri_params:
                    print pipe + space + '      ⌙ \033[1;{0}m{1}\033[1;m'.format(
                        color[4], u.name) + ": {0}".format(u.display_name)
            if node[1].form_params:
                print pipe + space + '     \033[1;{0}m{1}\033[1;m'.format(
                    color[4], "URI Params")
                for f in node[1].form_params:
                    print pipe + space + '      ⌙ \033[1;{0}m{1}\033[1;m'.format(
                        color[4], f.name) + ': {0}'.format(f.display_name)


def pprint_tree(api, ordered_nodes, light, verbosity):
    if light:
        color = (39, 32, 33, 34, 31)
    else:
        color = (30, 35, 36, 30, 35)
    print "\033[1;{0}m{1}\033[1;m".format(color[0], '=' * len(api.title))
    print '\033[1;{0}m{1}\033[1;m'.format(color[1], api.title)
    print "\033[1;{0}m{1}\033[1;m".format(color[0], '=' * len(api.title))
    print '\033[1;{0}m{1}{2}\033[1;m'.format(color[1], "Base URI: ",
                                             api.base_uri)

    if verbosity == 3:
        print_3_verbose(api, ordered_nodes, color)

    elif verbosity == 2:
        print_2_verbose(api, ordered_nodes, color)

    elif verbosity == 1:
        print_1_verbose(api, ordered_nodes, color)

    else:
        for k, v in list(ordered_nodes.items()):
            for node in v:
                space_count = _count_parents(node[1], count=0)
                space = "  " * space_count
            pipe = '\033[1;{0}m{1}\033[1;m'.format(color[0], "|")
            endpoint = space + "– {0}".format(k)
            print pipe + '\033[1;{0}m{1}\033[1;m'.format(color[2], endpoint)


def tree(ramlfile, light, verbosity):  # pragma: no cover
    api = APIRoot(ramlfile)
    nodes = get_tree(api)
    ordered_nodes = order_nodes(nodes)
    pprint_tree(api, ordered_nodes, light, verbosity)
