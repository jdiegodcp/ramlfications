# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB
from __future__ import absolute_import, division, print_function

from ramlfications import utils


def test_convert_camel_case():
    convert = utils.parser.convert_camel_case
    assert convert('CamelCase') == 'camel_case'
    assert convert('CamelCamelCase') == 'camel_camel_case'
    assert convert('Camel2Camel2Case') == 'camel2_camel2_case'
    assert convert('getHTTPResponseCode') == 'get_http_response_code'
    assert convert('get2HTTPResponseCode') == 'get2_http_response_code'
    assert convert('HTTPResponseCode') == 'http_response_code'
    assert convert('HTTPResponseCodeXYZ') == 'http_response_code_xyz'
