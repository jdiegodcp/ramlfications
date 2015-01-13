# ! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function

import os

from six import iterkeys
from six.moves import configparser
from six.moves import BaseHTTPServer as httpserver


config = configparser.RawConfigParser()
config_file = os.path.dirname(os.path.realpath(__file__)) + '/config.ini'
config.read(config_file)

AVAILABLE_METHODS = ['get', 'post', 'put', 'delete', 'patch', 'head',
                     'options', 'trace', 'connect']
HTTP_METHODS = [
    "get", "post", "put", "delete", "patch", "options",
    "head", "trace", "connect", "get?", "post?", "put?", "delete?",
    "patch?", "options?", "head?", "trace?", "connect?"
]

RAML_VERSIONS = ["0.8"]
HTTP_PROTOCOLS = ["HTTP", "HTTPS"]
MEDIA_TYPES = [
    "text/yaml", "text-x-yaml", "application/yaml", "application/x-yaml",
    "multipart/form-data", "text/html", "application/x-www-form-urlencoded",
    "text/plain"
]
AUTH_SCHEMES = [
    'oauth_1_0', 'oauth_2_0',
    'basic', 'basic_auth', 'basicAuth', 'basicAuthentication', 'http_basic',
    'basic_authentication', 'digest', 'digest_auth', 'digestAuth',
    'digestAuthentication', 'digest_authentication', 'http_digest'
]
HTTP_RESP_CODES = list(iterkeys(httpserver.BaseHTTPRequestHandler.responses))
PRIM_TYPES = ['string', 'integer', 'number', 'boolean', 'date', 'file']

custom_resp_codes = config.get('custom_add', 'resp_codes').strip().split(',')
HTTP_RESP_CODES.extend([int(c) for c in custom_resp_codes])

custom_auth_schemes = config.get('custom_add', 'auth_schemes').strip().split(',')
AUTH_SCHEMES.extend(custom_auth_schemes)

custom_media_types = config.get('custom_add', 'media_types').strip().split(',')
MEDIA_TYPES.extend(custom_media_types)

config.add_section('defaults')
config.set('defaults', 'available_methods', AVAILABLE_METHODS)
config.set('defaults', 'http_methods', HTTP_METHODS)
config.set('defaults', 'raml_versions', RAML_VERSIONS)
config.set('defaults', 'protocols', HTTP_PROTOCOLS)
config.set('defaults', 'media_types', MEDIA_TYPES)
config.set('defaults', 'prim_types', PRIM_TYPES)

config.add_section('custom')
config.set('custom', 'auth_schemes', AUTH_SCHEMES)
config.set('custom', 'resp_codes', HTTP_RESP_CODES)
