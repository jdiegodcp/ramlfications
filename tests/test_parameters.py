# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB
from __future__ import absolute_import, division, print_function

import os

import pytest

from ramlfications import parse

from tests.base import V020EXAMPLES


@pytest.fixture(scope="session")
def api():
    ramlfile = os.path.join(V020EXAMPLES, "responses.raml")
    config = os.path.join(V020EXAMPLES, "test_config.ini")
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
