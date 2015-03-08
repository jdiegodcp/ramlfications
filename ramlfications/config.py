# ! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function

from six import iterkeys
from six.moves import configparser
from six.moves import BaseHTTPServer as httpserver


HTTP_METHODS = [
    "get", "post", "put", "delete", "patch", "head",
    "options", "trace", "connect"
]
HTTP_OPTIONAL = [m + "?" for m in HTTP_METHODS].extend(HTTP_METHODS)

RAML_VERSIONS = ["0.8"]
PROTOCOLS = ["HTTP", "HTTPS"]
MEDIA_TYPES = [
    "text/yaml", "text-x-yaml", "application/yaml", "application/x-yaml",
    "multipart/form-data", "text/html", "application/x-www-form-urlencoded",
    "text/plain"
]
AUTH_SCHEMES = [
    "oauth_1_0", "oauth_2_0",
    "basic", "basic_auth", "basicAuth", "basicAuthentication",
    "http_basic", "basic_authentication",
    "digest", "digest_auth", "digestAuth", "digestAuthentication",
    "digest_authentication", "http_digest"
]
HTTP_RESP_CODES = list(iterkeys(httpserver.BaseHTTPRequestHandler.responses))
PRIM_TYPES = ["string", "integer", "number", "boolean", "date", "file"]

CONFIG_VARS = [
    "auth_schemes", "resp_codes", "media_types", "protocols", "http_methods",
    "prim_types", "raml_version"
]


def add_custom_config(user_config, parser_config):
    """Add user-defined config"""
    pc = parser_config

    if user_config.has_section("custom"):
        items = user_config.items("custom")
        for i in items:
            if i not in CONFIG_VARS:
                continue
            key = i[0]
            add_items = i[1].strip().split(",")
            pc[key] = list(set(pc[key].append(add_items)))

    pc["validate"] = user_config.get("main", "validate") or False
    pc["production"] = user_config.get("main", "production") or False

    return pc


def setup_config(config_file=None):
    """
    Setup configuration for valid RAML parsing.

    :param file config_file: ``.ini`` file to be parsed (optional)
    :returns: ConfigParser instance
    """
    parser_config = {
        "auth_schemes": AUTH_SCHEMES,
        "resp_codes": HTTP_RESP_CODES,
        "media_types": MEDIA_TYPES,
        "protocols": PROTOCOLS,
        "http_methods": HTTP_METHODS,
        "raml_version": RAML_VERSIONS,
        "prim_types": PRIM_TYPES,
    }

    if config_file:
        user_config = configparser.RawConfigParser()
        user_config.read(config_file)
        parser_config = add_custom_config(user_config, parser_config)

    optional = [m + "?" for m in parser_config["http_methods"]]
    parser_config["http_optional"] = optional + parser_config["http_methods"]

    return parser_config
