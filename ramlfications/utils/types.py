# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB


from ramlfications.errors import UnknownDataTypeError
from ramlfications.models import STANDARD_RAML_TYPES
from .common import merge_dicts
from .examples import parse_examples
from .parser import convert_camel_case


def _raw_types(root):
    return root.raw.get("types", {}) or {}


def _default_type(raw):
    # RAML 1.0: a declaration with properties defaults to object,
    # otherwise to string
    if isinstance(raw, dict) and "properties" in raw:
        return "object"
    return "string"


def _is_type_expression(declared_type):
    return isinstance(declared_type, str) and any(
        c in declared_type for c in ("|", "[", "(")
    )


def _split_union(expr):
    """Split a type expression on top-level ``|`` (ignoring parens)."""
    parts = []
    depth = 0
    current = ""
    for char in expr:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        if char == "|" and depth == 0:
            parts.append(current)
            current = ""
        else:
            current += char
    parts.append(current)
    return [p.strip() for p in parts]


def _is_parenthesized(expr):
    if not (expr.startswith("(") and expr.endswith(")")):
        return False
    depth = 0
    for i, char in enumerate(expr):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return i == len(expr) - 1
    return False


def _base_type_data(name, type_, raw, root):
    return dict(
        name=name,
        display_name=raw.get("displayName", name) if isinstance(
            raw, dict) else name,
        raw=raw,
        root=root,
        raml_version=root.raml_version,
        errors=root.errors,
        config=root.config,
        description=raw.get("description") if isinstance(raw, dict) else None,
        type=type_,
    )


def parse_type_expression(name, expr, raw, root, seen=frozenset()):
    """
    Parse a RAML 1.0 type expression: named types, arrays (``T[]``),
    unions (``A | B``), and parenthesized groupings thereof.
    """
    # imported here to avoid a circular import at module load
    from ramlfications.models.data_types import ArrayDataType, UnionDataType

    expr = expr.strip()
    while _is_parenthesized(expr):
        expr = expr[1:-1].strip()

    if expr.endswith("[]"):
        item_expr = expr[:-2].strip()
        items = parse_type_expression(None, item_expr, {}, root, seen)
        data = _base_type_data(name, "array", raw, root)
        data["items"] = items
        return ArrayDataType(**data)

    union_parts = _split_union(expr)
    if len(union_parts) > 1:
        members = [
            parse_type_expression(None, part, {}, root, seen)
            for part in union_parts
        ]
        data = _base_type_data(name, expr, raw, root)
        data["of"] = members
        return UnionDataType(**data)

    # a plain (possibly user-declared) type name
    new_raw = dict(raw) if isinstance(raw, dict) else {}
    new_raw["type"] = expr
    return parse_type(name or expr, new_raw, root, seen)


def _resolve_type_class(declared_type, root, seen):
    """
    Walk a user-declared type's inheritance chain until a built-in
    RAML type is found, returning the class to instantiate. Handles
    forward references by resolving names against the document's raw
    ``types`` declarations rather than parse order.
    """
    if declared_type in STANDARD_RAML_TYPES:
        return STANDARD_RAML_TYPES[declared_type]
    raw_types = _raw_types(root)
    if declared_type in raw_types:
        if declared_type in seen:
            msg = ("circular type reference involving "
                   "'{0}'.".format(declared_type))
            raise UnknownDataTypeError(msg)
        parent_raw = raw_types[declared_type]
        if not isinstance(parent_raw, dict):
            parent_raw = dict(type=parent_raw)
        parent_declared = parent_raw.get("type", _default_type(parent_raw))
        if isinstance(parent_declared, list):
            parent_declared = parent_declared[0]
        return _resolve_type_class(
            parent_declared, root, seen | {declared_type})
    msg = ("'{0}' is not a supported or defined RAML Data "
           "Type.".format(declared_type))
    raise UnknownDataTypeError(msg)


def _resolve_type(declared_type, raw, root, seen):
    """
    Merge ``raw`` with its ancestors' raw declarations, recursively,
    so multi-level inheritance chains resolve fully.
    """
    raw_types = _raw_types(root)
    parent = raw_types.get(declared_type)
    if parent is None:
        return raw
    if not isinstance(parent, dict):
        parent = dict(type=parent)
    merged = merge_dicts(raw, parent)
    parent_declared = parent.get("type", _default_type(parent))
    if isinstance(parent_declared, list):
        parent_declared = parent_declared[0]
    if (parent_declared not in STANDARD_RAML_TYPES and
            parent_declared not in seen):
        merged = _resolve_type(
            parent_declared, merged, root, seen | {declared_type})
    return merged


def parse_type(name, raw, root, seen=frozenset()):
    from ramlfications.models.data_types import ArrayDataType

    declared_type = raw.get("type", _default_type(raw))

    # multiple inheritance: merge every parent, class from the first
    if isinstance(declared_type, list):
        declared_parents = declared_type
        declared_type = declared_type[0]
    else:
        declared_parents = [declared_type]

    if _is_type_expression(declared_type):
        return parse_type_expression(name, declared_type, raw, root, seen)

    data_type_cls = _resolve_type_class(declared_type, root, seen)

    if declared_type not in STANDARD_RAML_TYPES:
        for parent in declared_parents:
            raw = _resolve_type(parent, raw, root, seen)

    data = dict([(convert_camel_case(k), v) for k, v in raw.items()])
    data["raw"] = raw
    data["name"] = name
    data["root"] = root
    data["description"] = raw.get("description")
    data["raml_version"] = root.raml_version
    data["display_name"] = raw.get("displayName", name)
    data.setdefault("errors", root.errors)
    data.setdefault("config", root.config)
    # TODO: what to do when it's a list?
    data["type"] = declared_type

    # TODO: super hacky, fixme
    if not issubclass(data_type_cls, ArrayDataType):
        data.pop("items", None)
    if declared_type == "string":
        # TODO: prob want to clean this up, too
        try:
            data.pop("properties")
        except KeyError:
            pass

    data.update(parse_examples(root.raml_version, data))

    node = data_type_cls(**data)
    if (issubclass(data_type_cls, ArrayDataType) and
            isinstance(node.items, str)):
        node.items = parse_type_expression(None, node.items, {}, root, seen)
    return node
