# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB

"""
RAML 1.0 Overlay and Extension merging.

An overlay or extension names its target API through ``extends``; the
target is loaded and the overlay/extension document is merged into it
per the RAML 1.0 merging rules (maps merge recursively, other values
are replaced). Overlays additionally MUST NOT change behavioral
aspects of the target: they may only add or override documentation-
oriented properties (titles, descriptions, documentation, examples,
annotations and annotation types) on nodes that already exist.
"""

import os

from ramlfications.errors import InvalidOverlayError, LoadRAMLError


# properties an overlay may add or override; a key in this set is
# allowed along with its whole subtree
_OVERLAY_ALLOWED_KEYS = frozenset([
    "title", "displayName", "description", "documentation", "usage",
    "example", "examples", "annotationTypes", "uses",
])

# keys of the overlay document itself that are not merged into the
# target (RAML 1.0: `extends` and `usage` describe the overlay)
_NOT_MERGED_KEYS = ("extends", "usage")


def merge_extends(loaded_raml, config):
    """
    Resolve and load the ``extends`` target of an Overlay/Extension
    document, merge the document into it, and return the merged target
    (a ``Root``-fragment RAMLDict ready for normal parsing).
    """
    from ramlfications.utils import load_file

    fragment_type = loaded_raml._raml_fragment_type
    extends = loaded_raml.get("extends")
    if not extends or not isinstance(extends, str):
        msg = ("Error parsing RAML {0}: an 'extends' property naming "
               "the target document is required".format(fragment_type))
        raise LoadRAMLError(msg)

    source = getattr(loaded_raml, "_raml_source_path", None)
    base_dir = os.path.dirname(os.path.abspath(source)) if source else ""
    path = extends
    if not os.path.isabs(path):
        path = os.path.join(base_dir, path)
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        msg = ("Error parsing RAML {0}: 'extends' target does not "
               "exist: {1}".format(fragment_type, path))
        raise LoadRAMLError(msg)

    target = load_file(path)
    # a chain of overlays/extensions is applied bottom-up
    if target._raml_fragment_type in ("Overlay", "Extension"):
        target = merge_extends(target, config)
    if target._raml_fragment_type != "Root":
        msg = ("Error parsing RAML {0}: 'extends' target must be a "
               "RAML API document: {1}".format(fragment_type, path))
        raise LoadRAMLError(msg)

    if fragment_type == "Overlay":
        _assert_non_behavioral(loaded_raml, target, path="")

    _merge(target, loaded_raml)
    return target


def _merge(target, source):
    for key, value in source.items():
        if key in _NOT_MERGED_KEYS:
            continue
        if (key in target and isinstance(target[key], dict) and
                isinstance(value, dict)):
            _merge(target[key], value)
        else:
            target[key] = value
    return target


def _is_annotation_key(key):
    return (isinstance(key, str) and key.startswith("(") and
            key.endswith(")"))


def _assert_non_behavioral(overlay_node, target_node, path):
    """
    Walk the overlay against its target: any key outside the allowed
    set must already exist in the target as a map (a path traversed to
    reach an allowed property), otherwise the overlay adds or changes
    a behavioral aspect and is rejected.
    """
    for key, value in overlay_node.items():
        if path == "" and key in _NOT_MERGED_KEYS:
            continue
        if key in _OVERLAY_ALLOWED_KEYS or _is_annotation_key(key):
            continue
        key_path = "{0}/{1}".format(path, key)
        target_value = (
            target_node.get(key) if isinstance(target_node, dict)
            else None)
        if isinstance(value, dict) and isinstance(target_value, dict):
            _assert_non_behavioral(value, target_value, key_path)
            continue
        msg = ("Overlay may not change the behavioral aspects of its "
               "target; disallowed node at '{0}'".format(key_path))
        raise InvalidOverlayError(msg)
