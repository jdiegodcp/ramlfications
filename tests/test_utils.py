# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB
import sys

import json
import os
import tempfile
from mock import Mock, patch
import pytest
import xmltodict

from ramlfications import utils

from .base import UPDATE


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
    utils._urllib_download.assert_called_once()

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
    utils._requests_download.assert_called_once()

    mocker.stopall()


@patch("ramlfications.utils._xml_to_dict")
@patch("ramlfications.utils._parse_xml_data")
@patch("ramlfications.utils._requests_download")
@patch("ramlfications.utils._urllib_download")
@patch("ramlfications.utils._save_updated_mime_types")
def test_update_mime_types(_a, _b, _c, _d, _e, downloaded_xml):
    utils.requests = Mock()

    with open(downloaded_xml, "r", encoding="UTF-8") as raw_data:
        utils.update_mime_types()
        utils._requests_download.assert_called_once()
        utils._requests_download.return_value = raw_data.read()
        utils._xml_to_dict.assert_called_once()
        utils._parse_xml_data.assert_called_once()
        utils._save_updated_mime_types.assert_called_once()


def test_save_updated_mime_types():
    content = ["foo/bar", "bar/baz"]
    temp_output = tempfile.mkstemp()[1]
    utils._save_updated_mime_types(temp_output, content)

    result = open(temp_output, "r", encoding="UTF-8").read()
    result = json.loads(result)
    assert result == content

    os.remove(temp_output)


def test_convert_camel_case():
    convert = utils.parser.convert_camel_case
    assert convert('CamelCase') == 'camel_case'
    assert convert('CamelCamelCase') == 'camel_camel_case'
    assert convert('Camel2Camel2Case') == 'camel2_camel2_case'
    assert convert('getHTTPResponseCode') == 'get_http_response_code'
    assert convert('get2HTTPResponseCode') == 'get2_http_response_code'
    assert convert('HTTPResponseCode') == 'http_response_code'
    assert convert('HTTPResponseCodeXYZ') == 'http_response_code_xyz'
