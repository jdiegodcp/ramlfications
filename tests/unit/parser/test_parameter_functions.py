# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

"""
``<<parameter>>`` substitution and parameter functions, end to end through
``ramlfications.parse``, per RAML version.
"""

import pytest

from ramlfications import parse
from ramlfications.errors import InvalidRAMLStructureError


RAML08 = """#%RAML 0.8
title: Demo
baseUri: https://api.example.com
resourceTypes:
  - t:
      get:
        description: "{desc}"
{path}:
  type: {type_}
"""

RAML10 = """#%RAML 1.0
title: Demo
resourceTypes:
  t:
    get:
      description: "{desc}"
{path}:
  type: {type_}
"""

TEMPLATES = {"0.8": RAML08, "1.0": RAML10}
GIZMO = "{ t: { thing: gizmo } }"


def _description(version, desc, path="/widgets", type_=GIZMO, config=None):
    raml = TEMPLATES[version].format(desc=desc, path=path, type_=type_)
    api = parse(raml, config)
    get = [r for r in api.resources if r.method == "get"][0]
    return get.description.raw


# Requirement: Adjacent parameters are substituted independently
@pytest.mark.parametrize("version", ["0.8", "1.0"])
@pytest.mark.parametrize("desc,expected", [
    ("<<thing>>-<<resourcePathName>>", "gizmo-widgets"),
    ("<<resourcePathName>>/<<thing>>", "widgets/gizmo"),
    ("<<thing>><<resourcePathName>>", "gizmowidgets"),
    ("<<thing | !pluralize>>-<<resourcePathName>>", "gizmos-widgets"),
    ("<< thing >> and <<thing>>", "gizmo and gizmo"),
])
def test_adjacent_placeholders(version, desc, expected):
    assert _description(version, desc) == expected


# Requirement: Parameter functions follow the RAML version
@pytest.mark.parametrize("func,value,expected", [
    ("uppercase", "userId", "USERID"),
    ("lowercase", "userId", "userid"),
    ("lowercamelcase", "UserId", "userId"),
    ("uppercamelcase", "userId", "UserId"),
    ("lowerunderscorecase", "userId", "user_id"),
    ("upperunderscorecase", "userId", "USER_ID"),
    ("lowerhyphencase", "userId", "user-id"),
    ("upperhyphencase", "userId", "USER-ID"),
    ("lowercamelcase", "user_id", "userId"),
    ("uppercamelcase", "user-id", "UserId"),
])
def test_raml10_case_functions(func, value, expected):
    desc = "<<thing | !%s>>" % func
    type_ = "{ t: { thing: %s } }" % value
    assert _description("1.0", desc, type_=type_) == expected


@pytest.mark.parametrize("version", ["0.8", "1.0"])
@pytest.mark.parametrize("path,func,expected", [
    ("/users", "singularize", "Get one user"),
    ("/user", "singularize", "Get one user"),
    ("/user", "pluralize", "Get one users"),
    ("/users", "pluralize", "Get one users"),
])
def test_singularize_pluralize_keep_requested_form(version, path, func,
                                                   expected):
    desc = "Get one <<resourcePathName | !%s>>" % func
    assert _description(version, desc, path=path, type_="t") == expected


# Requirement: Unknown or version-disallowed parameter functions raise
# RAML errors
RAML10_FUNCTION_LIST = (
    "!singularize, !pluralize, !uppercase, !lowercase, !lowercamelcase, "
    "!uppercamelcase, !lowerunderscorecase, !upperunderscorecase, "
    "!lowerhyphencase, !upperhyphencase"
)


@pytest.mark.parametrize("version,func,msg", [
    ("0.8", "uppercase",
     "'!uppercase' is a RAML 1.0 parameter function and is not valid in a "
     "RAML 0.8 document."),
    ("0.8", "upercase",
     "'!upercase' is not a RAML parameter function. Valid functions: "
     "!singularize, !pluralize."),
    ("1.0", "upercase",
     "'!upercase' is not a RAML parameter function. Valid functions: "
     + RAML10_FUNCTION_LIST + "."),
    ("1.0", "inflect",
     "'!inflect' is not a RAML parameter function. Valid functions: "
     + RAML10_FUNCTION_LIST + "."),
])
def test_function_errors(version, func, msg):
    with pytest.raises(InvalidRAMLStructureError) as e:
        _description(version, "<<thing | !%s>>" % func)
    assert str(e.value) == msg


def test_function_error_with_validation_off(tmp_path):
    config = tmp_path / "config.ini"
    config.write_text("[main]\nvalidate = False\n")
    with pytest.raises(InvalidRAMLStructureError) as e:
        _description("0.8", "<<thing | !upercase>>", config=str(config))
    assert str(e.value) == (
        "'!upercase' is not a RAML parameter function. Valid functions: "
        "!singularize, !pluralize.")
