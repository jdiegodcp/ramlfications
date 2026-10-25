# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB

import copy
import os

from ramlfications import utils
from ramlfications.config import setup_config
from ramlfications.parser.parser import RootParser

from tests.base import RAML_08


def test_convert_camel_case():
    convert = utils.parser.convert_camel_case
    assert convert('CamelCase') == 'camel_case'
    assert convert('CamelCamelCase') == 'camel_camel_case'
    assert convert('Camel2Camel2Case') == 'camel2_camel2_case'
    assert convert('getHTTPResponseCode') == 'get_http_response_code'
    assert convert('get2HTTPResponseCode') == 'get2_http_response_code'
    assert convert('HTTPResponseCode') == 'http_response_code'
    assert convert('HTTPResponseCodeXYZ') == 'http_response_code_xyz'


def test_resolve_inherited_scalar_substitutes_type_params():
    raml = utils.load_file(
        os.path.join(RAML_08, "parameterised-internal-resource.raml"))
    config = setup_config(os.path.join(RAML_08, "test-config.ini"))
    root = RootParser(raml, config).create_node()
    type_ = {"collection-custom-variable": {"resourceType": "job"}}
    raw_before = copy.deepcopy(root.raw["resourceTypes"])

    resolve = utils.parser.resolve_inherited_scalar
    desc = resolve("description", ["method", "resource", "types"],
                   root=root, type_=type_, method="get",
                   resource_path="/jobs")

    assert desc == "Get all the jobs"
    # substitution must not leak into the caller's data or the raw RAML
    assert type_ == {"collection-custom-variable": {"resourceType": "job"}}
    assert root.raw["resourceTypes"] == raw_before
