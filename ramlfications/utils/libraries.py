# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB


import os
import re

from ramlfications.errors import LoadRAMLError
from ramlfications.models.libraries import Library
from ramlfications.utils.common import OrderedDict

from .nodelist import NodeList


# (RAML section, root node attribute holding the parsed objects)
LIBRARY_SECTIONS = (
    ("types", "types"),
    ("annotationTypes", "annotation_types"),
    ("traits", "traits"),
    ("resourceTypes", "resource_types"),
    ("securitySchemes", "security_schemes"),
)

_TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_\-.]*")


def load_libraries(data, config):
    """
    Resolve a root document's ``uses`` declarations.

    Loads each referenced library file (recursively, for libraries used
    by libraries), injects every member into ``data``'s own sections
    under the dotted ``LibName.member`` notation — with references
    internal to a library rewritten to their dotted form — and returns
    a NodeList of :py:class:`.models.libraries.Library` (or ``None``).
    """
    uses = data.get("uses")
    if not uses or not isinstance(uses, dict):
        return None
    source = getattr(data, "_raml_source_path", None)
    if source:
        base_dir = os.path.dirname(os.path.abspath(source))
    else:
        base_dir = os.getcwd()
    libraries = NodeList()
    for alias, path in list(uses.items()):
        library, flattened = _flatten_library(
            alias, path, base_dir, config, ())
        libraries.append(library)
        _inject(data, flattened)
    _set_prefixes(libraries)
    return libraries or None


def library_source_path(root, name):
    """
    Source file of the library declaring the dotted ``name``, walking
    into nested libraries, or ``None`` when ``name`` is not a library
    member (or the source file is unknown).
    """
    def _walk(libraries):
        for lib in libraries or []:
            if name.startswith(lib.prefix):
                nested = _walk(lib.uses)
                return nested or getattr(
                    lib.raw, "_raml_source_path", None)
        return None

    if not isinstance(name, str):
        return None
    return _walk(getattr(root, "uses", None))


def attach_library_members(root):
    """
    After the main parse pass, point each Library object at the parsed
    member nodes belonging to its namespace.
    """
    def _members(nodes, prefix):
        matched = NodeList(
            n for n in nodes or []
            if n.name.startswith(prefix) and
            "." not in n.name[len(prefix):])
        return matched or None

    def _attach(libraries):
        for lib in libraries or []:
            for _, attr_name in LIBRARY_SECTIONS:
                nodes = getattr(root, attr_name, None)
                setattr(lib, attr_name, _members(nodes, lib.prefix))
            _attach(lib.uses)

    _attach(root.uses)


def _load_library_file(path, base_dir, seen):
    from ramlfications.utils import load_file

    if not os.path.isabs(path):
        path = os.path.join(base_dir, path)
    path = os.path.abspath(path)
    if path in seen:
        msg = ("Error loading RAML library: circular 'uses' reference "
               "involving: {0}".format(path))
        raise LoadRAMLError(msg)
    if not os.path.isfile(path):
        msg = ("Error loading RAML library: file does not exist: "
               "{0}".format(path))
        raise LoadRAMLError(msg)
    loaded = load_file(path)
    if loaded._raml_fragment_type != "Library":
        msg = ("Error loading RAML library: '{0}' is not a "
               "'#%RAML 1.0 Library' fragment".format(path))
        raise LoadRAMLError(msg)
    return path, loaded


def _flatten_library(alias, path, base_dir, config, seen):
    """
    Load one library and return ``(Library, flattened)``, where
    ``flattened`` maps each RAML section to an OrderedDict of
    ``alias.member`` names, with declarations rewritten so references
    between library members use the dotted names as well.
    """
    path, loaded = _load_library_file(path, base_dir, seen)

    merged = dict((s, OrderedDict()) for s, _ in LIBRARY_SECTIONS)
    for section, _ in LIBRARY_SECTIONS:
        declarations = loaded.get(section) or {}
        if isinstance(declarations, dict):
            merged[section].update(declarations)

    nested_libs = NodeList()
    nested_uses = loaded.get("uses") or {}
    for nested_alias, nested_path in list(nested_uses.items()):
        nested_lib, nested_flat = _flatten_library(
            nested_alias, nested_path, os.path.dirname(path),
            config, seen + (path,))
        nested_libs.append(nested_lib)
        for section, _ in LIBRARY_SECTIONS:
            merged[section].update(nested_flat[section])

    maps = _rename_maps(alias, merged)
    flattened = {}
    for section, _ in LIBRARY_SECTIONS:
        flattened[section] = OrderedDict(
            ("{0}.{1}".format(alias, name), _rewrite_node(decl, maps))
            for name, decl in merged[section].items())

    library = Library(
        name=alias,
        raw=loaded,
        usage=loaded.get("usage"),
        uses=nested_libs or None,
    )
    return library, flattened


def _inject(data, flattened):
    for section, _ in LIBRARY_SECTIONS:
        members = flattened.get(section)
        if not members:
            continue
        existing = data.get(section)
        if not isinstance(existing, dict):
            existing = OrderedDict()
            data[section] = existing
        for name, decl in members.items():
            existing.setdefault(name, decl)


def _set_prefixes(libraries, parent_prefix=""):
    for lib in libraries or []:
        lib.prefix = parent_prefix + lib.name + "."
        _set_prefixes(lib.uses, lib.prefix)


def _rename_maps(alias, merged):
    def _map(*sections):
        rename = {}
        for section in sections:
            for name in merged[section]:
                rename[name] = "{0}.{1}".format(alias, name)
        return rename

    return {
        # `type`/`items` positions can name data types or, on resource
        # type applications, resource types — one map covers both
        "types": _map("types", "resourceTypes"),
        "annotations": _map("annotationTypes"),
        "traits": _map("traits"),
        "schemes": _map("securitySchemes"),
    }


def _rewrite_expression(expr, rename):
    return _TOKEN.sub(lambda m: rename.get(m.group(0), m.group(0)), expr)


def _rewrite_type_value(value, maps):
    if isinstance(value, str):
        return _rewrite_expression(value, maps["types"])
    if isinstance(value, list):
        return [_rewrite_type_value(v, maps) for v in value]
    return _rewrite_node(value, maps)


def _rewrite_refs(value, rename):
    # `is`/`securedBy` entries: name strings, ``None`` (optional
    # security), or single-key maps of name -> parameters
    def _one(item):
        if isinstance(item, str):
            return rename.get(item, item)
        if isinstance(item, dict) and len(item) == 1:
            name = list(item.keys())[0]
            if name in rename:
                return OrderedDict(
                    [(rename[name], list(item.values())[0])])
        return item

    if isinstance(value, list):
        return [_one(v) for v in value]
    return _one(value)


def _rewrite_properties(properties, maps):
    rewritten = OrderedDict()
    for name, decl in properties.items():
        if isinstance(decl, str):
            rewritten[name] = _rewrite_expression(decl, maps["types"])
        else:
            rewritten[name] = _rewrite_node(decl, maps)
    return rewritten


def _rewrite_node(node, maps):
    if isinstance(node, dict):
        rewritten = OrderedDict()
        for key, value in node.items():
            new_key = key
            if (isinstance(key, str) and key.startswith("(") and
                    key.endswith(")")):
                inner = key[1:-1].strip()
                if inner in maps["annotations"]:
                    new_key = "({0})".format(maps["annotations"][inner])
            if key in ("type", "items"):
                rewritten[new_key] = _rewrite_type_value(value, maps)
            elif key == "is":
                rewritten[new_key] = _rewrite_refs(value, maps["traits"])
            elif key == "securedBy":
                rewritten[new_key] = _rewrite_refs(value, maps["schemes"])
            elif key == "properties" and isinstance(value, dict):
                rewritten[new_key] = _rewrite_properties(value, maps)
            else:
                rewritten[new_key] = _rewrite_node(value, maps)
        return rewritten
    if isinstance(node, list):
        return [_rewrite_node(item, maps) for item in node]
    return node
