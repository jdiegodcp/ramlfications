# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB

"""
Standalone parsing of RAML 1.0 typed fragment files.

Each ``create_root_*`` function turns a loaded fragment document into
the parsed object the same declaration would produce when defined
inline in an API document.
"""

from ramlfications.models.libraries import Library
from ramlfications.models.root import Documentation
from ramlfications.utils.libraries import (
    attach_library_members, load_libraries
)
from ramlfications.utils.nodelist import NodeList

from .parser import (
    AnnotationTypeParser, DataTypeParser, ResourceTypeParser,
    SecuritySchemeParser, TraitParser
)


def _as_section(loaded_raml, section):
    """Wrap a fragment's body as a single-entry root-style section."""
    name = loaded_raml.get("displayName")
    return {section: {name: loaded_raml}}


def create_root_trait(loaded_raml, root, config):
    data = _as_section(loaded_raml, "traits")
    return TraitParser(data, root, config).create_nodes().one()


def create_root_resource_type(loaded_raml, root, config):
    # one ResourceTypeNode is created per method, so a fragment
    # declaring several methods parses to several nodes
    data = _as_section(loaded_raml, "resourceTypes")
    return ResourceTypeParser(data, root, config).create_nodes()


def create_root_security_scheme(loaded_raml, root, config):
    data = _as_section(loaded_raml, "securitySchemes")
    return SecuritySchemeParser(data, root, config).create_nodes().one()


def create_root_documentation_item(loaded_raml, root, config):
    return Documentation(
        loaded_raml.get("title"), loaded_raml.get("content"))


def create_root_library(loaded_raml, root, config):
    uses = load_libraries(loaded_raml, config)

    def _parse(parser_cls):
        return parser_cls(loaded_raml, root, config).create_nodes() or None

    root.uses = uses
    root.types = _parse(DataTypeParser)
    root.annotation_types = _parse(AnnotationTypeParser)
    root.traits = _parse(TraitParser)
    root.resource_types = _parse(ResourceTypeParser)
    root.security_schemes = _parse(SecuritySchemeParser)
    if uses:
        attach_library_members(root)

    def _own(nodes):
        # members declared by this library itself; dotted names come
        # from nested `uses` libraries and live on Library.uses
        own = NodeList(
            n for n in nodes or [] if n.name and "." not in n.name)
        return own or None

    return Library(
        name=loaded_raml.get("displayName"),
        raw=loaded_raml,
        usage=loaded_raml.get("usage"),
        uses=uses,
        types=_own(root.types),
        annotation_types=_own(root.annotation_types),
        traits=_own(root.traits),
        resource_types=_own(root.resource_types),
        security_schemes=_own(root.security_schemes),
    )
