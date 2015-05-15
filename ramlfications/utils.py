# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function


import json
import logging
import os
import sys

import xmltodict

PYVER = sys.version_info[:3]

if PYVER == (2, 7, 9) or PYVER == (3, 4, 3):
    import six.moves.urllib.request as urllib
    URLLIB = True
    SECURE_DOWNLOAD = True
else:
    try:  # NOCOV
        import requests
        URLLIB = False
        SECURE_DOWNLOAD = True
    except ImportError:
        import six.moves.urllib.request as urllib
        URLLIB = True
        SECURE_DOWNLOAD = False

from .errors import MediaTypeError


IANA_URL = "https://www.iana.org/assignments/media-types/media-types.xml"


def load_schema(data):
    """
    Load Schema/Example data depending on its type (JSON, XML).

    If error in parsing as JSON and XML, just returns unloaded data.

    :param str data: schema/example data
    """
    try:
        return json.loads(data)
    except Exception:  # POKEMON!
        pass

    try:
        return xmltodict.parse(data)
    except Exception:  # GOTTA CATCH THEM ALL
        pass

    return data


def requests_download_xml():
    try:
        response = requests.get(IANA_URL)
        return response.text
    except requests.exceptions.RequestException as e:
        msg = "Error downloading XML from IANA: {0}".format(e)
        raise MediaTypeError(msg)


def urllib_download_xml():
    try:
        response = urllib.urlopen(IANA_URL)
    except urllib.URLError as e:
        msg = "Error downloading XML from IANA: {0}".format(e)
        raise MediaTypeError(msg)
    return response.read()


def xml_to_dict(response_text):
    try:
        return xmltodict.parse(response_text)
    except xmltodict.expat.ExpatError as e:
        msg = "Error parsing XML: {0}".format(e)
        raise MediaTypeError(msg)


def _extract_mime_types(registry):
    mime_types = []
    records = registry.get("record", {})
    reg_name = registry.get("@id")
    for rec in records:
        mime = rec.get("file", {}).get("#text")
        if mime:
            mime_types.append(mime)
        else:
            mime = rec.get("name")
            if mime:
                hacked_mime = reg_name + "/" + mime
                mime_types.append(hacked_mime)
    return mime_types


def parse_xml_data(xml_data):
    registries = xml_data.get("registry", {}).get("registry")
    if not registries:
        msg = "No registries found to parse."
        raise MediaTypeError(msg)
    if len(registries) is not 9:
        msg = ("Expected 9 registries but parsed "
               "{0}".format(len(registries)))
        raise MediaTypeError(msg)
    all_mime_types = []
    for registry in registries:
        mime_types = _extract_mime_types(registry)
        all_mime_types.extend(mime_types)

    return all_mime_types


def save_data(output_file, mime_types):
    with open(output_file, "w") as f:
        json.dump(mime_types, f)


def update_mime_types():
    def setup_logger():
        log = logging.getLogger(__name__)
        log.setLevel(logging.DEBUG)
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        msg = "updating MIME types - %(levelname)s - %(message)s"
        formatter = logging.Formatter(msg)
        console.setFormatter(formatter)

        log.addHandler(console)
        return log

    log = setup_logger()

    log.debug("Getting XML data from IANA")
    if SECURE_DOWNLOAD and not URLLIB:
        raw_data = requests_download_xml()
    elif SECURE_DOWNLOAD and URLLIB:
        raw_data = urllib_download_xml()
    else:
        msg = ("Downloading over HTTPS but can not verify the host's "
               "certificate.  To avoid this in the future, `pip install"
               " \"requests[security]\"`.")
        log.warn(msg)
        raw_data = urllib_download_xml()

    log.debug("Data received; parsing...")
    xml_data = xml_to_dict(raw_data)
    mime_types = parse_xml_data(xml_data)

    current_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(current_dir, "data")
    output_file = os.path.join(data_dir, "supported_mime_types.json")

    save_data(output_file, mime_types)

    log.debug("Done! Supported IANA MIME media types have been updated.")
