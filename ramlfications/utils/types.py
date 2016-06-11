# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB

from __future__ import absolute_import, division, print_function

from six import iteritems

from ramlfications.errors import UnknownDataTypeError
from ramlfications.models import RAML_DATA_TYPES
from .parser import convert_camel_case


def parse_type(name, raw, root):
    declared_type = raw.get("type", "string")
    # TODO: maybe move this error checking into validation
    try:
        data_type_cls = RAML_DATA_TYPES[declared_type]
    except KeyError:
        msg = ("'{0}' is not a supported or defined RAML Data "
               "Type.".format(declared_type))
        raise UnknownDataTypeError(msg)

    data = dict([(convert_camel_case(k), v) for k, v in iteritems(raw)])
    data["raw"] = raw
    data["name"] = name
    data["root"] = root
    data["description"] = raw.get("description")
    data["raml_version"] = root.raml_version
    data["display_name"] = raw.get("displayName", name)
    return data_type_cls(**data)
