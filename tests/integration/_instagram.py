#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

import json
import os

import pytest

from ramlfications import loader
from ramlfications import parse
from ramlfications import parser as pw
from ramlfications.config import setup_config
from ramlfications.raml import RootNode, ResourceTypeNode, TraitNode
from tests.base import EXAMPLES


@pytest.fixture
def raml():
    raml_file = os.path.join(EXAMPLES + "instagram.raml")
    return loader.RAMLLoader().load(raml_file)


def test_parse_raml(raml):
    config = setup_config(EXAMPLES + "instagram-config.ini")
    root = pw.parse_raml(raml, config)
    assert isinstance(root, RootNode)
