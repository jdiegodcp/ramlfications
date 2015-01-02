# ! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function

import ConfigParser
import os

from six.moves import BaseHTTPServer as httpserver


config = ConfigParser.RawConfigParser()
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
    "multipart/form-data"
]
AUTH_SCHEMES = [
    'oauth_1_0', 'oauth_2_0',
    'basic', 'basic_auth', 'basicAuth', 'basicAuthentication',
    'basic_authentication', 'digest', 'digest_auth', 'digestAuth',
    'digestAuthentication', 'digest_authentication'
]
HTTP_RESP_CODES = httpserver.BaseHTTPRequestHandler.responses.keys()
PRIM_TYPES = ['string', 'integer', 'number', 'boolean', 'date', 'file']

HTTP_RESP_CODES.extend(config.get('custom_add', 'resp_codes'))
AUTH_SCHEMES.extend(config.get('custom_add', 'auth_schemes'))

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
