# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function


from io import open
import json
import logging
import os
import sys

import six
import xmltodict


PYVER = sys.version_info[:3]

if PYVER == (2, 7, 9) or PYVER == (3, 4, 3):  # NOCOV
    import six.moves.urllib.request as urllib
    import six.moves.urllib.error as urllib_error
    URLLIB = True
    SECURE_DOWNLOAD = True
else:
    try:  # NOCOV
        import requests
        URLLIB = False
        SECURE_DOWNLOAD = True
    except ImportError:
        import six.moves.urllib.request as urllib
        import six.moves.urllib.error as urllib_error
        URLLIB = True
        SECURE_DOWNLOAD = False

from ramlfications.errors import MediaTypeError, LoadRAMLError
from ramlfications.loader import RAMLLoader


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


def setup_logger(key):
    """General logger"""
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    msg = "{key} - %(levelname)s - %(message)s".format(key=key)
    formatter = logging.Formatter(msg)
    console.setFormatter(formatter)

    log.addHandler(console)
    return log


def _requests_download(url):
    """Download a URL using ``requests`` library"""
    try:
        response = requests.get(url)
        return response.text
    except requests.exceptions.RequestException as e:
        msg = "Error downloading from {0}: {1}".format(url, e)
        raise MediaTypeError(msg)


def _urllib_download(url):
    """Download a URL using ``urllib`` library"""
    try:
        response = urllib.urlopen(url)
    except urllib_error.URLError as e:
        msg = "Error downloading from {0}: {1}".format(url, e)
        raise MediaTypeError(msg)
    return response.read()


def download_url(url):
    """
    General download function, given a URL.

    If running 2.7.8 or earlier, or 3.4.2 or earlier, then use
    ``requests`` if it's installed.  Otherwise, use ``urllib``.
    """
    log = setup_logger("DOWNLOAD")
    if SECURE_DOWNLOAD and not URLLIB:
        return _requests_download(url)
    elif SECURE_DOWNLOAD and URLLIB:
        return _urllib_download(url)
    msg = ("Downloading over HTTPS but can not verify the host's "
           "certificate.  To avoid this in the future, `pip install"
           " \"requests[security]\"`.")
    log.warn(msg)
    return _urllib_download(url)


def _xml_to_dict(response_text):
    """Parse XML response from IANA into a Python ``dict``."""
    try:
        return xmltodict.parse(response_text)
    except xmltodict.expat.ExpatError as e:
        msg = "Error parsing XML: {0}".format(e)
        raise MediaTypeError(msg)


def _extract_mime_types(registry):
    """
    Parse out MIME types from a defined registry (e.g. "application",
    "audio", etc).
    """
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


def _parse_xml_data(xml_data):
    """Parse the given XML data."""
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


def _save_updated_mime_types(output_file, mime_types):
    """Save the updated MIME Media types within the package."""
    # not sure why json.dump(mime_types) doesn't work, raises a TypeError
    # saying it should be unicode. So loading in memory then making the
    # str -> unicode
    data = json.dumps(mime_types)
    with open(output_file, "w", encoding="UTF-8") as f:
        f.write(unicode(data))


def update_mime_types():
    """
    Update MIME Media Types from IANA.  Requires internet connection.
    """
    log = setup_logger("UPDATE")

    log.debug("Getting XML data from IANA")
    raw_data = download_url(IANA_URL)
    log.debug("Data received; parsing...")
    xml_data = _xml_to_dict(raw_data)
    mime_types = _parse_xml_data(xml_data)

    current_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(current_dir, "data")
    output_file = os.path.join(data_dir, "supported_mime_types.json")

    _save_updated_mime_types(output_file, mime_types)

    log.debug("Done! Supported IANA MIME media types have been updated.")


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
