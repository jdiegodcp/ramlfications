# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB


from ramlfications.models.annotations import Annotation

from .nodelist import NodeList


def _annotation_type_for(name, root):
    declared = getattr(root, "annotation_types", None) or []
    for annotation_type in declared:
        if annotation_type.name == name:
            return annotation_type
    return None


def parse_annotations(raw, root):
    """
    Extract ``(name): value`` annotations applied on a raw node mapping,
    returning a NodeList of :py:class:`.models.annotations.Annotation`
    objects (or ``None``).
    """
    if getattr(root, "raml_version", None) != "1.0":
        return None
    if not isinstance(raw, dict):
        return None
    annotations = NodeList()
    for key, value in raw.items():
        if not isinstance(key, str):
            continue
        if key.startswith("(") and key.endswith(")"):
            name = key[1:-1].strip()
            annotations.append(Annotation(
                name=name,
                value=value,
                annotation_type=_annotation_type_for(name, root),
            ))
    return annotations or None
