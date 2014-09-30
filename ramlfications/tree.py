#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from loader import RAMLLoader
from parser import Node, NodeStack


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


def root_nodes(raml):  # pragma: no cover
    available_methods = ['get', 'post', 'put', 'delete',
                         'patch', 'head', 'options']
    node_stack = []
    tree_nodes = []
    for k, v in list(raml.items()):
        if k.startswith("/"):
            root = TreeNode(k)
            _methods = []
            for method in available_methods:
                if method in raml[k].keys():
                    _methods.append(method)
                    node = Node(name=k, data=v, method=method)
                    node_stack.append(node)
            root.methods = set(_methods)
            tree_nodes.append(root)

    return node_stack, tree_nodes


def get_children(root, node_stack):  # pragma: no cover
    available_methods = ['get', 'post', 'put', 'delete',
                         'patch', 'head', 'options']

    try:
        print "Root: ", root.name
        node_names = [n.name for n in node_stack]
        node_index = node_names.index(root.name)
        node_root = node_stack.pop(node_index)

        children = []
        methods = []
        if node_root.data:
            for child_k, child_v in list(node_root.data.items()):
                if child_k.startswith("/"):
                    child_node = TreeNode(name=child_k)
                    print "Child: ", child_node.name
                    for method in available_methods:
                        if method in node_root.data[child_k].keys():
                            methods.append(method)
                        node = Node(child_k, child_v, method, node_root)
                        node_stack.append(node)
                    children.append(child_node)
        print "Children: ", children
        root.children = children
        root.methods = methods

        return root, node_stack
    except ValueError:
        return None, node_stack
    except AttributeError:
        return root, None
    except TypeError:
        return None, None


def child_nodes(node_stack):  # pragma: no cover
    available_methods = ['get', 'post', 'put', 'delete',
                         'patch', 'head', 'options']

    while node_stack:
        current = node_stack.pop(0)
        _current = TreeNode(current.display_name, methods=list(current.method))
        if current.data:
            _children = []
            _methods = [k for k, v in list(current.data.items()) if k in available_methods]
            for child_k, child_v in list(current.data.items()):
                if child_k.startswith("/"):
                    _methods = []
                    for method in available_methods:
                        if method in current.data[child_k].keys():
                            child = Node(child_k, child_v, method, current)
                            node_stack.append(child)
                            leaf = TreeNode(child.name, methods=method)
                            if leaf not in _children:
                                _children.append(leaf)
            _current.children = _children
            _current.methods = _methods
        yield _current


# def get_children(raml):
#     children = []
#     remaining = {}

#     for key, value in list(raml.items()):
#         if key.startswith("/"):
#             methods = []
#             for method in AVAIL_METHODS:
#                 if method in raml[key].keys():
#                     methods.append(method)
#             node = TreeNode(key, methods=methods)
#             children.append(node)
#             remaining[key] = value
#     return children, remaining


def main():  # pragma: no cover
    raml_file = "/Users/lynnroot/Dev/spotify/ramlfications/tests/examples/spotify-web-api.raml"
    raml = RAMLLoader(raml_file).raml

    s_nodes, r_nodes = root_nodes(raml)
    #c_nodes = list(child_nodes(r_nodes))

    # children, remaining = get_children(raml)
    root = TreeNode('Spotify API', methods=None, children=r_nodes)

    node_stack = list(NodeStack(raml).yield_nodes())

    while node_stack:
        for r in r_nodes:
            node, node_stack = get_children(r, node_stack)
            root.children.append(node)
            if not node_stack:
                break

    # for child in children:
    #     _children, _remaining = get_children(remaining[child.name])
    #     child_index = root.children.index(child)
    #     root.children[child_index].children = _children

    print root

if __name__ == '__main__':
    main()
