# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB

"""
Post-parse validation pass for RAML 1.0 documents.

Errors are located (resource path, method, body media type, and the
document's source file when known) and appended to ``root.errors`` so
independent problems are collected and reported together instead of
failing at the first one.
"""

from ramlfications.errors import InvalidResourceNodeError


def _is_expression(name):
    return any(c in name for c in ("|", "[", "("))


def _scalar_conforms(declared_type, value):
    if declared_type == "string":
        return isinstance(value, str)
    if declared_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if declared_type == "number":
        return (isinstance(value, (int, float)) and
                not isinstance(value, bool))
    if declared_type == "boolean":
        return isinstance(value, bool)
    if declared_type == "nil":
        return value is None
    # only simple scalar annotation types are checked
    return True


def _resource_label(res):
    if res.method:
        return "{0} {1}".format(res.method, res.path)
    return res.path


def _located(msg, root):
    source = getattr(root.raw, "_raml_source_path", None)
    if source:
        return "{0} [{1}]".format(msg, source)
    return msg


def _iter_bodies(res):
    for body in res.body or []:
        yield body, "body"
    for resp in res.responses or []:
        for body in resp.body or []:
            yield body, "response {0} body".format(resp.code)


def _check_type_references(res, root, declared):
    from ramlfications.utils.libraries import library_source_path

    for body, where in _iter_bodies(res):
        name = body.type
        if not isinstance(name, str) or _is_expression(name):
            continue
        if name in declared:
            continue
        msg = ("Unresolved data type '{0}' on {1} '{2}' of resource "
               "'{3}'.".format(name, where, body.mime_type,
                               _resource_label(res)))
        lib_source = library_source_path(root, name)
        if lib_source:
            msg = "{0} [library: {1}]".format(msg, lib_source)
        root.errors.append(
            InvalidResourceNodeError(_located(msg, root)))


def _check_annotations(res, root):
    for annotation in res.annotations or []:
        annotation_type = annotation.annotation_type
        if annotation_type is None:
            continue
        declared_type = annotation_type.type
        if not isinstance(declared_type, str):
            continue
        if _scalar_conforms(declared_type, annotation.value):
            continue
        msg = ("Annotation '({0})' on resource '{1}' has value {2!r} "
               "that does not conform to its declared type "
               "'{3}'.".format(annotation.name, _resource_label(res),
                               annotation.value, declared_type))
        root.errors.append(
            InvalidResourceNodeError(_located(msg, root)))


def validate_raml10(root):
    """
    Run RAML 1.0-only validation rules against a parsed root node,
    collecting located errors into ``root.errors``.
    """
    if getattr(root, "raml_version", None) != "1.0":
        return
    # imported late: models imports the validate package at load time
    from ramlfications.models import STANDARD_RAML_TYPES

    declared = set(STANDARD_RAML_TYPES)
    declared.update(
        t.name for t in root.types or [] if isinstance(t.name, str))
    for res in root.resources or []:
        _check_type_references(res, root, declared)
        _check_annotations(res, root)
