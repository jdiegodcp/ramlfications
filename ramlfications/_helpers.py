# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB
import sys

if sys.version_info[0] == 2:
    from io import open

import os

import six

from .errors import LoadRAMLError
from .loader import RAMLLoader


def load_file(raml_file):
    try:
        with _get_raml_object(raml_file) as raml:
            return RAMLLoader().load(raml)
    except IOError as e:
        raise LoadRAMLError(e)


def load_string(raml_str):
    return RAMLLoader().load(raml_str)


def _get_raml_object(raml_file):
    """
    Returns a file object.
    """
    if raml_file is None:
        msg = "RAML file can not be 'None'."
        raise LoadRAMLError(msg)

    if isinstance(raml_file, six.text_type) or isinstance(
            raml_file, bytes):
        return open(os.path.abspath(raml_file), 'r', encoding="UTF-8")
    elif hasattr(raml_file, 'read'):
        return raml_file
    else:
        msg = ("Can not load object '{0}': Not a basestring type or "
               "file object".format(raml_file))
        raise LoadRAMLError(msg)
