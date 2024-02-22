# -*- coding: utf-8 -*-
# Copyright (c) 2016 Spotify AB
from __future__ import absolute_import, division, print_function

import json
import os
import sys
import tempfile
from mock import Mock, patch
import pytest
import platform

import xmltodict

from ramlfications.errors import LoadRAMLError
from ramlfications import utils

from tests.base import RAML_08, UPDATE

#####
# TODO: write tests, and associated error/failure tests
#####


if sys.version_info[0] == 2:
    from io import open

if sys.version_info[0] == 2:
    from io import open


@pytest.fixture(scope="session")
def downloaded_xml():
    return os.path.join(UPDATE, "iana_mime_media_types.xml")


@pytest.fixture(scope="session")
def invalid_xml():
    return os.path.join(UPDATE, "invalid_iana_download.xml")


@pytest.fixture(scope="session")
def no_data_xml():
    return os.path.join(UPDATE, "no_data.xml")


@pytest.fixture(scope="session")
def expected_data():
    expected_json = os.path.join(UPDATE, "expected_mime_types.json")
    with open(expected_json, "r", encoding="UTF-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def parsed_xml(downloaded_xml):
    with open(downloaded_xml, "r", encoding="UTF-8") as f:
        data = f.read()
        return xmltodict.parse(data)


def test_xml_to_dict(downloaded_xml):
    with open(downloaded_xml, "r", encoding="UTF-8") as f:
        data = f.read()
        xml_data = utils._xml_to_dict(data)
        assert xml_data is not None
        assert isinstance(xml_data, dict)


def test_xml_to_dict_no_data(no_data_xml):
    with pytest.raises(utils.MediaTypeError) as e:
        with open(no_data_xml, "r", encoding="UTF-8") as f:
            data = f.read()
            utils._xml_to_dict(data)

    msg = "Error parsing XML: "
    assert msg in e.value.args[0]


def test_xml_to_dict_invalid(invalid_xml):
    with pytest.raises(utils.MediaTypeError) as e:
        with open(invalid_xml, "r", encoding="UTF-8") as f:
            data = f.read()
            utils._xml_to_dict(data)

    msg = "Error parsing XML: "
    assert msg in e.value.args[0]


def test_parse_xml_data(parsed_xml, expected_data):
    result = utils._parse_xml_data(parsed_xml)

    assert result == expected_data
    assert len(result) == len(expected_data)


@pytest.fixture(scope="session")
def incorrect_registry_count():
    xml_file = os.path.join(UPDATE, "unexpected_registry_count.xml")
    with open(xml_file, "r", encoding="UTF-8") as f:
        data = f.read()
        return xmltodict.parse(data)


def test_parse_xml_data_incorrect_reg(incorrect_registry_count):
    with pytest.raises(utils.MediaTypeError) as e:
        utils._parse_xml_data(incorrect_registry_count)

    msg = ("Expected 9 registries but parsed 2",)
    assert e.value.args == msg


@pytest.fixture(scope="session")
def no_registries():
    xml_file = os.path.join(UPDATE, "no_registries.xml")
    with open(xml_file, "r", encoding="UTF-8") as f:
        data = f.read()
        return xmltodict.parse(data)


def test_parse_xml_data_no_reg(no_registries):
    with pytest.raises(utils.MediaTypeError) as e:
        utils._parse_xml_data(no_registries)

    msg = ("No registries found to parse.",)
    assert e.value.args == msg


def test_requests_download_xml(downloaded_xml):
    utils.requests = Mock()
    with open(downloaded_xml, "r", encoding="UTF-8") as xml:
        expected = xml.read()
        utils.requests.get.return_value.text = expected
        results = utils._requests_download(utils.IANA_URL)

        assert results == expected


def test_urllib_download(downloaded_xml):
    utils.urllib = Mock()
    with open(downloaded_xml, "r", encoding="UTF-8") as xml:
        utils.urllib.urlopen.return_value = xml
        results = utils._urllib_download(utils.IANA_URL)

    with open(downloaded_xml, "r", encoding="UTF-8") as xml:
        assert results == xml.read()


@patch("ramlfications.utils._parse_xml_data")
@patch("ramlfications.utils._xml_to_dict")
@patch("ramlfications.utils._save_updated_mime_types")
def test_insecure_download_urllib_flag(_a, _b, _c, mocker, monkeypatch):
    monkeypatch.setattr(utils, "SECURE_DOWNLOAD", False)
    monkeypatch.setattr(utils, "URLLIB", True)
    utils.requests = Mock()

    mocker.patch("ramlfications.utils._urllib_download")

    utils.update_mime_types()
    utils._urllib_download.assert_called_once_with(
        'https://www.iana.org/assignments/media-types/media-types.xml')

    mocker.stopall()


@patch("ramlfications.utils._xml_to_dict")
@patch("ramlfications.utils._parse_xml_data")
@patch("ramlfications.utils._save_updated_mime_types")
def test_secure_download_requests_flag(_a, _b_, _c, mocker, monkeypatch):
    monkeypatch.setattr(utils, "SECURE_DOWNLOAD", True)
    monkeypatch.setattr(utils, "URLLIB", False)
    utils.urllib = Mock()

    mocker.patch("ramlfications.utils._requests_download")

    utils.update_mime_types()
    utils._requests_download.assert_called_once_with(
        'https://www.iana.org/assignments/media-types/media-types.xml')

    mocker.stopall()


@patch("ramlfications.utils.download_url")
@patch("ramlfications.utils._save_updated_mime_types")
def test_update_mime_types(
        mock_save_updated_mime_types,
        mock_downloaded_url,
        downloaded_xml,
        expected_data):

    with open(downloaded_xml, encoding="UTF-8") as f:
        mock_downloaded_url.return_value = f.read()

    utils.update_mime_types()

    mock_downloaded_url.assert_called_once_with(
        'https://www.iana.org/assignments/media-types/media-types.xml')

    expected_save_path = os.path.realpath(os.path.join(
        os.path.dirname(utils.__file__),
        'data/supported_mime_types.json'))
    mock_save_updated_mime_types.assert_called_once_with(
        expected_save_path,
        expected_data)


@pytest.mark.skipif(platform.system() == 'Windows',
                    reason="Skipping this test because it's Windows.")
def test_save_updated_mime_types():
    content = ["foo/bar", "bar/baz"]
    temp_output = tempfile.mkstemp()[1]
    utils._save_updated_mime_types(temp_output, content)

    result = open(temp_output, "r", encoding="UTF-8").read()
    result = json.loads(result)
    assert result == content

    os.remove(temp_output)


@pytest.fixture(scope="session")
def raml_file():
    return os.path.join(RAML_08, "complete-valid-example.raml")


def test_raml_file_is_none():
    raml_file = None
    with pytest.raises(LoadRAMLError) as e:
        utils._get_raml_object(raml_file)
    msg = ("RAML file can not be 'None'.",)
    assert e.value.args == msg


def test_raml_file_object(raml_file):
    with open(raml_file) as f:
        raml_obj = utils._get_raml_object(f)
        assert raml_obj == f


def test_not_valid_raml_obj():
    invalid_obj = 1234
    with pytest.raises(LoadRAMLError) as e:
        utils._get_raml_object(invalid_obj)
    msg = (("Can not load object '{0}': Not a basestring type or "
           "file object".format(invalid_obj)),)
    assert e.value.args == msg
