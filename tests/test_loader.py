# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB
from __future__ import absolute_import, division, print_function

import os

import json
import pytest
from six import iteritems
import StringIO

from ramlfications import loader
from ramlfications.errors import LoadRAMLError

from .base import EXAMPLES, JSONREF
from .data.fixtures import load_fixtures as lf


def dict_equal(dict1, dict2):
    for k, v1 in list(iteritems(dict1)):
        assert k in dict2
        v2 = dict2[k]
        assert v1 == v2
    return True


def test_load_file():
    raml_file = os.path.join(EXAMPLES + "base-includes.raml")
    with open(raml_file) as f:
        raml = loader.RAMLLoader().load(f)

    expected_data = lf.load_file_expected_data
    assert dict_equal(raml, expected_data)


def test_load_file_with_nested_includes():
    raml_file = os.path.join(EXAMPLES + "nested-includes.raml")
    with open(raml_file) as f:
        raml = loader.RAMLLoader().load(f)

    expected_data = lf.load_file_with_nested_includes_expected
    assert dict_equal(raml, expected_data)


def test_load_file_with_nonyaml_include():
    raml_file = os.path.join(EXAMPLES + "nonyaml-includes.raml")
    with open(raml_file) as f:
        raml = loader.RAMLLoader().load(f)

    expected_data = {
        'not_yaml': "This is just a string.\n",
        'title': 'GitHub API Demo - Includes',
        'version': 'v3'
    }

    assert dict_equal(raml, expected_data)


def test_load_string():
    raml_str = ("""#%RAML 0.8
                name: foo
                """)
    raml = loader.RAMLLoader().load(raml_str)

    expected_data = {"name": "foo"}
    assert raml == expected_data


def test_yaml_parser_error():
    raml_obj = os.path.join(EXAMPLES, "invalid_yaml.yaml")
    with pytest.raises(LoadRAMLError) as e:
        loader.RAMLLoader().load(open(raml_obj))
    msg = "Error parsing RAML:"
    assert msg in e.value.args[0]


def test_include_json():
    raml_file = os.path.join(EXAMPLES + "json_includes.raml")
    with open(raml_file) as f:
        raml = loader.RAMLLoader().load(f)

        expected_data = lf.include_json_expected
        assert dict_equal(raml, expected_data)


def test_include_xsd():
    raml_file = os.path.join(EXAMPLES + "xsd_includes.raml")
    with open(raml_file) as f:
        raml = loader.RAMLLoader().load(f)

    expected_data = lf.include_xsd_expected
    assert dict_equal(raml, expected_data)


def test_include_markdown():
    raml_file = os.path.join(EXAMPLES + "md_includes.raml")
    with open(raml_file) as f:
        raml = loader.RAMLLoader().load(f)

    expected_data = lf.include_markdown_expected
    assert dict_equal(raml, expected_data)


def test_invalid_yaml_tag():
    raml_file = os.path.join(EXAMPLES, "invalid_yaml_tag.raml")
    with pytest.raises(LoadRAMLError) as e:
        loader.RAMLLoader().load(open(raml_file))

    msg = "Error parsing RAML:"
    assert msg in e.value.args[0]


def test_includes_has_invalid_tag():
    raml_file = os.path.join(EXAMPLES, "include_has_invalid_tag.raml")
    with pytest.raises(LoadRAMLError) as e:
        loader.RAMLLoader().load(open(raml_file))

    msg = "Error parsing RAML:"
    assert msg in e.value.args[0]


def test_jsonref_relative_empty_fragment():
    raml_file = os.path.join(JSONREF, "jsonref_empty_fragment.raml")
    with open(raml_file) as f:
        raml = loader.RAMLLoader().load(f)

    expected_data = lf.jsonref_relative_empty_fragment_expected
    assert dict_equal(raml, expected_data)


def test_jsonref_relative_nonempty_fragment():
    raml_file = os.path.join(JSONREF, "jsonref_nonempty_fragment.raml")
    with open(raml_file) as f:
        raml = loader.RAMLLoader().load(f)

    expected_data = lf.jsonref_relative_nonempty_fragment_expected
    assert dict_equal(raml, expected_data)


def test_jsonref_internal_fragment_reference():
    raml_file = os.path.join(JSONREF, "jsonref_internal_fragment.raml")
    with open(raml_file) as f:
        raml = loader.RAMLLoader().load(f)

    expected_data = lf.jsonref_internal_fragment_reference_expected
    assert dict_equal(raml, expected_data)


def test_jsonref_multiref_internal_fragments():
    raml_file = os.path.join(JSONREF,
                             "jsonref_multiref_internal_fragment.raml")
    with open(raml_file) as f:
        raml = loader.RAMLLoader().load(f)

    expected_data = lf.jsonref_multiref_internal_fragments_expected
    assert dict_equal(raml, expected_data)


def test_jsonref_absolute_local_uri(tmpdir):
    # Set up a tmp RAML file with an absolute path
    json_schema_file = tmpdir.join("json_absolute_ref.json")
    data = lf.json_ref_absolute_jsondump
    json_schema_file.write(json.dumps(data))

    raml_file = tmpdir.join("json_absolute_ref.raml")
    output = lf.json_ref_absolute_ramlfile
    raml_file.write(output.format(json_file=json_schema_file.strpath))

    # Now load it
    raml = loader.RAMLLoader().load(raml_file.read())
    expected_data = lf.json_ref_absolute_expected
    assert dict_equal(raml, expected_data)


def test_jsonref_relative_local_uri():
    # RAML file includes a JSON schema.  The JSON schema includes a
    # reference to another local JSON file (same level)
    ramlfile = os.path.join(JSONREF, "jsonref_relative_local.raml")
    with open(ramlfile, "r") as f:
        loaded_raml = loader.RAMLLoader().load(f)

    schemas = loaded_raml.get("schemas")
    expected = lf.jsonref_relative_local_expected
    actual = schemas[0].get("jsonexample")

    assert dict_equal(expected, actual)


def test_jsonref_relative_local_uri_includes():
    # RAML file includes a JSON schema.  JSON schema includes a reference
    # to another local JSON file (in another directory)
    ramlfile = os.path.join(JSONREF, "jsonref_relative_local_includes.raml")
    with open(ramlfile, "r") as f:
        loaded_raml = loader.RAMLLoader().load(f)

    schemas = loaded_raml.get("schemas")

    expected = lf.jsonref_relative_local_includes_expected

    actual = schemas[0].get("jsonexample")
    assert dict_equal(expected, actual)


def test_jsonref_remote_uri(tmpdir, httpserver):
    mock_remote_json = os.path.join(JSONREF, "jsonref_mock_remote.json")
    httpserver.serve_content(open(mock_remote_json).read())

    # since we don't know what port httpserver will be on until it's
    # created, have to create the JSON file that ref's it with the url
    # variable & RAML
    jsonfile = tmpdir.join("jsonref_remote_url.json")
    data = lf.jsonref_remote_uri_jsondump
    mock_remote_url = httpserver.url + "#properties"
    data["properties"]["images"]["items"][0]["$ref"] = mock_remote_url
    jsonfile.write(json.dumps(data))

    ramlfile = tmpdir.join("jsonref_remote_url.raml")
    output = lf.jsonref_remote_uri_raml.format(json_file=jsonfile.strpath)
    ramlfile.write(output)
    readfile = ramlfile.read()
    loaded = loader.RAMLLoader().load(readfile)
    expected = lf.json_remote_uri_expected
    assert dict_equal(expected, loaded)


def test_jsonref_relative_local_file():
    # 'file:' prepends the local filename in the JSON schema
    ramlfile = os.path.join(JSONREF, "jsonref_relative_local_file.raml")
    with open(ramlfile, "r") as f:
        loaded_raml = loader.RAMLLoader().load(f)

    schemas = loaded_raml.get("schemas")
    expected = lf.jsonref_relative_local_file_expected
    actual = schemas[0].get("jsonexample")

    assert dict_equal(expected, actual)


def test_jsonref_relative_local_includes_file():
    # 'file:' prepends the local filename in the JSON schema
    filename = "jsonref_relative_local_includes_file.raml"
    ramlfile = os.path.join(JSONREF, filename)
    with open(ramlfile, "r") as f:
        loaded_raml = loader.RAMLLoader().load(f)

    schemas = loaded_raml.get("schemas")
    expected = lf.jsonref_relative_local_includes_expected
    actual = schemas[0].get("jsonexample")

    assert dict_equal(expected, actual)


def test_jsonref_absolute_local_uri_file(tmpdir):
    # Set up a tmp RAML file with an absolute path
    json_schema_file = tmpdir.join("json_absolute_ref_file.json")
    data = lf.json_ref_absolute_jsondump_file
    json_schema_file.write(json.dumps(data))

    raml_file = tmpdir.join("json_absolute_ref_file.raml")
    output = lf.json_ref_absolute_ramlfile
    raml_file.write(output.format(json_file=json_schema_file.strpath))

    # Now load it
    raml = loader.RAMLLoader().load(raml_file.read())
    expected_data = lf.json_ref_absolute_expected
    assert dict_equal(raml, expected_data)


def test_parse_version():
    f = StringIO.StringIO("#%RAML 0.8")
    raml = loader.RAMLLoader().load(f)
    assert raml._raml_version == "0.8"


def test_parse_badversion():
    f = StringIO.StringIO("#%ssRAML 0.8")
    with pytest.raises(LoadRAMLError) as e:
        loader.RAMLLoader().load(f)
    msg = "Error raml file shall start with #%RAML"
    assert msg in e.value.args[0]


def test_parse_noversion():
    f = StringIO.StringIO("{}")
    with pytest.raises(LoadRAMLError) as e:
        loader.RAMLLoader().load(f)
    msg = "Error raml file shall start with #%RAML"
    assert msg in e.value.args[0]
