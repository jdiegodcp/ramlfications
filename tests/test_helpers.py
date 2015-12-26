# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB
import os

import pytest

from ramlfications.errors import LoadRAMLError
from ramlfications.utils import _get_raml_object

from .base import EXAMPLES


@pytest.fixture(scope="session")
def raml_file():
    return os.path.join(EXAMPLES + "complete-valid-example.raml")


def test_raml_file_is_none():
    raml_file = None
    with pytest.raises(LoadRAMLError) as e:
        _get_raml_object(raml_file)
    msg = ("RAML file can not be 'None'.",)
    assert e.value.args == msg


def test_raml_file_object(raml_file):
    with open(raml_file) as f:
        raml_obj = _get_raml_object(f)
        assert raml_obj == f


def test_not_valid_raml_obj():
    invalid_obj = 1234
    with pytest.raises(LoadRAMLError) as e:
        _get_raml_object(invalid_obj)
    msg = (("Can not load object '{0}': Not a basestring type or "
           "file object".format(invalid_obj)),)
    assert e.value.args == msg
