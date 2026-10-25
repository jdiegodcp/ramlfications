# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB

import os

import pytest

from ramlfications import parse
from ramlfications.parser.parameters import ParameterParser

from tests.base import RAML_08


@pytest.fixture(scope="session")
def api():
    ramlfile = os.path.join(RAML_08, "responses.raml")
    config = os.path.join(RAML_08, "test_config.ini")
    return parse(ramlfile, config)


def test_create_response(api):
    res = api.resources[0]
    assert len(res.responses) == 1

    resp = res.responses[0]
    assert resp.code == 200
    desc = "This is the 200 resp description for get widgets"
    assert resp.description.raw == desc
    assert len(resp.body) == 1
    assert len(resp.headers) == 2


#####
# TODO: COMPLETE ME
#####


def test_substitute_path_params_with_string_type():
    kwargs = {"resource_path": "/root/widget-d", "type_": "collection-item"}
    parser = ParameterParser("body", kwargs)
    resolved = {"application/json": {"schema": "<<resourcePathName>>"},
                "text/plain": {"example": "<<resourcePath>>"}}

    result = parser._substitute_params(resolved)

    # resourcePathName is the rightmost path segment, not "root/widget-d"
    assert result["application/json"]["schema"] == "widget-d"
    assert result["text/plain"]["example"] == "/root/widget-d"


def test_substitute_params_does_not_mutate_assignment():
    type_ = {"collection": {"item": "job"}}
    kwargs = {"resource_path": "/jobs", "type_": type_}
    parser = ParameterParser("body", kwargs)

    result = parser._substitute_params(
        {"schema": "<<item>>", "example": "<<resourcePathName>>"})

    assert result == {"schema": "job", "example": "jobs"}
    assert type_ == {"collection": {"item": "job"}}
