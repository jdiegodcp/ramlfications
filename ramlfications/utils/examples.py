# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from six import iteritems

from ramlfications.errors import InvalidRAMLStructureError
from ramlfications.models.base import BaseContent
from ramlfications.models.examples import Example
from ramlfications.utils.nodelist import NodeList


def parse_examples(raml_version, data):
    #
    # This is the only place that knows when to supply examples and when
    # not, and that checks when both are supplied.
    #
    # This is also responsible for generating structured Example objects
    # when appropriate (RAML >= 1.0).
    #
    data = data or {}
    kw = {}
    example = data.get("example")

    if raml_version == "0.8":
        if "examples" in data:
            del data["examples"]
            # TODO: Emit a lint warning if there's an examples node and
            # we're processing RAML 0.8: authors may be expecting it to
            # be honored.
        kw["example"] = example

    if raml_version != "0.8":
        if "example" in data:
            kw["example"] = parse_example(None, example)

        kw["examples"] = None
        if "examples" in data:
            if "example" in data:
                # TODO: Emit a lint warning during validation.
                raise InvalidRAMLStructureError(
                    "example and examples cannot co-exist")
            examples = data["examples"]
            # Must be a map:
            if not isinstance(examples, dict):
                # Need to decide what exception to make this.
                raise InvalidRAMLStructureError("examples must be a map node")
            kw["examples"] = NodeList([parse_example(nm, val)
                                       for nm, val in iteritems(examples)])

    return kw


def parse_example(name, node):
    data = dict(name=name, value=node)
    if name:
        data["display_name"] = name
    if isinstance(node, dict) and "value" in node:
        data["value"] = node["value"]
        data["description"] = BaseContent(node.get("description", ""))
        data["display_name"] = node.get("displayName", name)
        data["strict"] = node.get("strict", True)

    return Example(**data)
