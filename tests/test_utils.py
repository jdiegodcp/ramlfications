# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB
import json
import os

from mock import Mock
import pytest
import xmltodict

from ramlfications import utils

from .base import UPDATE


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
    with open(expected_json, "r") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def parsed_xml(downloaded_xml):
    with open(downloaded_xml, "r") as f:
        data = f.read()
        return xmltodict.parse(data)


def test_xml_to_dict(downloaded_xml):
    with open(downloaded_xml, "r") as f:
        data = f.read()
        xml_data = utils.xml_to_dict(data)
        assert xml_data is not None
        assert isinstance(xml_data, dict)


def test_xml_to_dict_no_data(no_data_xml):
    with pytest.raises(utils.MediaTypeError) as e:
        with open(no_data_xml, "r") as f:
            data = f.read()
            utils.xml_to_dict(data)

    msg = "Error parsing XML: "
    assert msg in e.value.args[0]


def test_xml_to_dict_invalid(invalid_xml):
    with pytest.raises(utils.MediaTypeError) as e:
        with open(invalid_xml, "r") as f:
            data = f.read()
            utils.xml_to_dict(data)

    msg = "Error parsing XML: "
    assert msg in e.value.args[0]


def test_parse_xml_data(parsed_xml, expected_data):
    result = utils.parse_xml_data(parsed_xml)

    assert result == expected_data
    assert len(result) == len(expected_data)


@pytest.fixture(scope="session")
def incorrect_registry_count():
    xml_file = os.path.join(UPDATE, "unexpected_registry_count.xml")
    with open(xml_file, "r") as f:
        data = f.read()
        return xmltodict.parse(data)


def test_parse_xml_data_incorrect_reg(incorrect_registry_count):
    with pytest.raises(utils.MediaTypeError) as e:
        utils.parse_xml_data(incorrect_registry_count)

    msg = ("Expected 9 registries but parsed 2",)
    assert e.value.args == msg


@pytest.fixture(scope="session")
def no_registries():
    xml_file = os.path.join(UPDATE, "no_registries.xml")
    with open(xml_file, "r") as f:
        data = f.read()
        return xmltodict.parse(data)


def test_parse_xml_data_no_reg(no_registries):
    with pytest.raises(utils.MediaTypeError) as e:
        utils.parse_xml_data(no_registries)

    msg = ("No registries found to parse.",)
    assert e.value.args == msg


def test_secure_download_xml(downloaded_xml):
    utils.requests = Mock()
    with open(downloaded_xml) as xml:
        expected = xml.read()
        utils.requests.get.return_value.text = expected
        results = utils.secure_download_xml()

        assert results == expected


def test_insecure_download(downloaded_xml):
    utils.urllib = Mock()
    with open(downloaded_xml) as xml:
        utils.urllib.urlopen.return_value = xml
        results = utils.insecure_download_xml()

    with open(downloaded_xml) as xml:
        assert results == xml.read()


def test_insecure_download_flag(monkeypatch):
    monkeypatch.setattr(utils, "SECURE_DOWNLOAD", False)

    # lots of mocking D:
    utils.urllib2 = Mock()
    utils.xml_to_dict = Mock()
    utils.parse_xml_data = Mock()
    utils.save_data = Mock()
    utils.insecure_download_xml = Mock()

    utils.update_mime_types()
    utils.insecure_download_xml.assert_called_once()


def test_secure_download_flag(monkeypatch):
    monkeypatch.setattr(utils, "SECURE_DOWNLOAD", True)

    # lots of mocking D:
    utils.requests = Mock()
    utils.xml_to_dict = Mock()
    utils.parse_xml_data = Mock()
    utils.save_data = Mock()
    utils.secure_download_xml = Mock()

    utils.update_mime_types()
    utils.secure_download_xml.assert_called_once()


def test_update_mime_types(downloaded_xml):
    utils.requests = Mock()
    utils.xml_to_dict = Mock()
    utils.parse_xml_data = Mock()
    utils.save_data = Mock()
    utils.secure_download_xml = Mock()

    with open(downloaded_xml, "r") as raw_data:
        utils.update_mime_types()
        utils.secure_download_xml.assert_called_once()
        utils.secure_download_xml.return_value = raw_data.read()
        utils.xml_to_dict.assert_called_once()
        utils.parse_xml_data.assert_called_once()
        utils.save_data.assert_called_once()
