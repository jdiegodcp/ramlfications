#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB
from __future__ import absolute_import, division, print_function


import os

from tests.base import JSONREF


# For test_loader.py::test_load_file
load_file_expected_data = {
    'external': {
        'propertyA': 'valueA',
        'propertyB': 'valueB'
    },
    'foo': {
        'foo': 'FooBar',
        'bar': 'BarBaz'
    },
    'title': 'GitHub API Demo - Includes',
    'version': 'v3'
}

# For test_loader.py::test_load_file_with_nested_includes
load_file_with_nested_includes_expected = {
    'include_one': {
        'external': {
            'propertyA': 'valueA',
            'propertyB': 'valueB'
        },
        'foo': {
            'foo': 'FooBar',
            'bar': 'BarBaz'
        },
        'not_yaml': "This is just a string.\n",
    },
    'title': 'GitHub API Demo - Includes',
    'version': 'v3'
}

# For test_loader.py::test_include_json
include_json_expected = {
    "title": "Sample API Demo - JSON Includes",
    "version": "v1",
    "baseUri": "http://json.example.com",
    "schemas": [{
        "json": {
            "name": "foo",
            "false": True
        },
    }],
    "/foo": {
        "displayName": "foo resource"
    }
}

# For test_loader.py::test_include_xsd
include_xsd_raw = """<?xml version="1.0" encoding="UTF-8"?>
<root>
   <false>true</false>
   <name>foo</name>
</root>
"""

include_xsd_expected = {
    "title": "Sample API Demo - XSD Includes",
    "version": "v1",
    "baseUri": "http://xml.example.com",
    "schemas": [{
        "xml": include_xsd_raw,
    }],
    "/foo": {
        "displayName": "foo resource",
    },
}

# For test_loader.py::test_include_markdown
include_markdown_raw = """## Foo

*Bacon ipsum dolor* amet pork belly _doner_ rump brisket. [Cupim jerky \
shoulder][0] ball tip, jowl bacon meatloaf shank kielbasa turducken corned \
beef beef turkey porchetta.

### Doner meatball pork belly andouille drumstick sirloin

Porchetta picanha tail sirloin kielbasa, pig meatball short ribs drumstick \
jowl. Brisket swine spare ribs picanha t-bone. Ball tip beef tenderloin jowl \
doner andouille cupim meatball. Porchetta hamburger filet mignon jerky flank, \
meatball salami beef cow venison tail ball tip pork belly.

[0]: https://baconipsum.com/?paras=1&type=all-meat&start-with-lorem=1
"""

include_markdown_expected = {
    "title": "Sample API Demo - Markdown Includes",
    "version": "v1",
    "baseUri": "http://markdown.example.com",
    "/foo": {
        "displayName": "foo resource"
    },
    "documentation": [{
        "title": "example",
        "content": include_markdown_raw,
    }],
}

# For test_loader.py::test_jsonref_relative_empty_fragment
jsonref_relative_empty_fragment_expected = {
    "title": "Sample API Demo - JSON Includes",
    "version": "v1",
    "baseUri": "http://json.example.com",
    "schemas": [{
        "json": {
            "name": "foo",
            "false": True
        },
    }],
    "/foo": {
        "displayName": "foo resource"
    }
}

# For test_loader.py::test_json_ref_in_schema_relative_nonempty_fragment
jsonref_relative_nonempty_fragment_expected = {
    "title": "Sample API Demo - JSON Includes",
    "version": "v1",
    "baseUri": "http://json.example.com",
    "schemas": [{
        "json": {
            "first_name": "foo",
            "second_name": "bar"
        },
    }],
    "/foo": {
        "displayName": "foo resource"
    }
}

# For test_loader.py::test_jsonref_internal_fragment_reference
jsonref_internal_fragment_reference_expected = {
    "title": "Sample API Demo - JSON Includes",
    "version": "v1",
    "baseUri": "http://json.example.com",
    "schemas": [{
        "json": {
            "references":
            {
                "internal": "yes",
            },
            "name": "foo",
            "is_this_internal?": ["yes"],
        },
    }],
    "/foo": {
        "displayName": "foo resource"
    }
}

# For test_loader.py::test_jsonref_multiref_internal_fragments
jsonref_multiref_internal_fragments_expected = {
    "title": "Sample API Demo - JSON Includes",
    "version": "v1",
    "baseUri": "http://json.example.com",
    "schemas": [{
        "json": {
            "references":
            {
                "internal": "yes",
                "two": True,
            },
            "name": "foo",
            "is_this_internal?": "yes",
            "two_references": True,
        },
    }],
    "/foo": {
        "displayName": "foo resource",
    }
}


# For test_loader.py::test_jsonref_absolute_local_uri
json_ref_absolute_jsonfile = os.path.join(JSONREF, "jsonref_example.json")

json_ref_absolute_jsondump = {
    "second_name": "bar",
    "$ref": json_ref_absolute_jsonfile
}

json_ref_absolute_ramlfile = ("""#%RAML 0.8
title: Sample API Demo - JSON Includes
version: v1
schemas:
    - json: !include {json_file}
baseUri: http://json.example.com
/foo:
  displayName: foo resource
""")


json_ref_absolute_expected = {
    "title": "Sample API Demo - JSON Includes",
    "version": "v1",
    "baseUri": "http://json.example.com",
    "schemas": [{
        "json": {
            "name": "foo",
            "false": True
        },
    }],
    "/foo": {
        "displayName": "foo resource"
    }
}


# for test_loader.py::test_jsonref_relative_local_uri
jsonref_relative_local_expected = {
    '$schema': 'http://json-schema.org/draft-03/schema',
    'properties': {
        'album_type': {
            'description': ("The type of the album: one of 'album', "
                            "'single', or 'compilation'."),
            'type': 'string'
        },
        'artists': {
            'description': ("The artists of the album. Each artist "
                            "object includes a link in href to more "
                            "detailed information about the artist."),
            'items': [{
                'popularity': {
                    'type': 'integer',
                    'description': ("The popularity of the artist. The "
                                    "value will be between 0 and 100, "
                                    "with 100 being the most popular. "
                                    "The artist's popularity is "
                                    "calculated from the popularity of "
                                    "all the artist's tracks.")
                },
                'type': {
                    'type': 'string',
                    'description': "The object type: 'artist'"
                },
                'name': {
                    'type': 'string',
                    'description': 'The name of the artist.'
                },
                'uri': {
                    'type': 'string',
                    'description': 'The Spotify URI for the artist.'
                }
            }],
            'type': 'array'
        }
    },
    'type': 'object'
}

# for test_loader.py::test_jsonref_relative_local_uri_includes
jsonref_relative_local_includes_expected = {
    '$schema': 'http://json-schema.org/draft-03/schema',
    'properties': {
        'album_type': {
            'description': ("The type of the album: one of 'album', "
                            "'single', or 'compilation'."),
            'type': u'string'
        },
        'artists': {
            'description': ("The artists of the album. Each artist "
                            "object includes a link in href to more "
                            "detailed information about the artist."),
            'items': [{
                'genres': {
                    'items': {
                        'type': 'string'
                    },
                    'type': 'array',
                    'description': ("A list of the genres the artist is "
                                    "associated with. For example: 'Prog "
                                    "Rock', 'Post-Grunge'. (If not yet "
                                    "classified, the array is empty.)")
                },
                'name': {
                    'type': 'string',
                    'description': 'The name of the artist.'
                },
                'external_urls': {
                    '': [{
                        'type': 'string'
                    }],
                    'type': 'object',
                    'description': 'Known external URLs for this artist.'
                },
                'popularity': {
                    'type': 'integer',
                    'description': ("The popularity of the artist. The "
                                    "value will be between 0 and 100, "
                                    "with 100 being the most popular. "
                                    "The artist's popularity is "
                                    "calculated from the popularity of "
                                    "all the artist's tracks.")
                },
                'uri': {
                    'type': 'string',
                    'description': 'The Spotify URI for the artist.'
                },
                'href': {
                    'type': 'string',
                    'description': ("A link to the Web API endpoint "
                                    "providing full details of the "
                                    "artist.")
                },
                'images': {
                    'items': {
                        'url': {
                            'type': 'string',
                            'description': ("The source URL of the "
                                            "image.")
                        },
                        'width': {
                            'type': 'integer',
                            'description': ("The image width in pixels. "
                                            "If unknown: null or not "
                                            "returned.")
                        },
                        'height': {
                            'type': 'integer',
                            'description': ("The image height in "
                                            "pixels. If unknown: "
                                            "null or not returned.")
                        }
                    },
                    'type': 'array',
                    'description': ("Images of the artist in "
                                    "various sizes, widest first.")
                },
                'type': {
                    'type': 'string',
                    'description': ("The object type: 'artist'")
                },
                'id': {
                    'type': 'string',
                    'description': ("The Spotify ID for the artist.")
                }
            }],
            'type': 'array'
        }
    },
    'type': 'object'
}


# for test_loader.py::test_jsonref_remote_uri
jsonref_remote_uri_jsondump = {
    "$schema": "http://json-schema.org/draft-03/schema",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "The name of the artist."
        },
        "images": {
            "type": "array",
            "description": "Images associated with artist",
            "items": [{"$ref": "{url}"}]
        }
    }
}

jsonref_remote_uri_raml = ("""#%RAML 0.8
title: Sample API Demo - JSON Includes
version: v1
schemas:
    - json: !include {json_file}
baseUri: http://json.example.com
/foo:
  displayName: foo resource
""")


json_remote_uri_expected = {
    "title": "Sample API Demo - JSON Includes",
    "version": "v1",
    "baseUri": "http://json.example.com",
    "schemas": [{
        "json": {
            "$schema": "http://json-schema.org/draft-03/schema",
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the artist."
                },
                "images": {
                    "type": "array",
                    "description": "Images associated with artist",
                    "items": [{
                        "height": {
                            "type": "integer",
                            "description": ("The image height in pixels. "
                                            "If unknown: null or not "
                                            "returned.")
                        },
                        "url": {
                            "type": "string",
                            "description": "The source URL of the image."
                        },
                        "width": {
                            "type": "integer",
                            "description": ("The image width in pixels. "
                                            "If unknown: null or not "
                                            "returned.")
                        }
                    }]
                }
            },
        }
    }],
    "/foo": {
        "displayName": "foo resource"
    }
}

jsonref_relative_local_file_expected = {
    "$schema": "http://json-schema.org/draft-03/schema",
    "type": "object",
    "properties": {
        "album_type": {
            "type": "string",
            "description": ("The type of the album: one of 'album', 'single', "
                            "or 'compilation'.")
        },
        "artists": {
            "type": "array",
            "description": ("The artists of the album. Each artist object "
                            "includes a link in href to more detailed "
                            "information about the artist."),
            "items": [{
                'popularity': {
                    'type': 'integer',
                    'description': ("The popularity of the artist. The "
                                    "value will be between 0 and 100, "
                                    "with 100 being the most popular. "
                                    "The artist's popularity is "
                                    "calculated from the popularity of "
                                    "all the artist's tracks.")
                },
                'type': {
                    'type': 'string',
                    'description': "The object type: 'artist'"
                },
                'name': {
                    'type': 'string',
                    'description': 'The name of the artist.'
                },
                'uri': {
                    'type': 'string',
                    'description': 'The Spotify URI for the artist.'
                }
            }]
        }
    }
}


# For test_loader.py::test_jsonref_absolute_local_uri_file
json_ref_absolute_jsonfile = os.path.join(JSONREF, "jsonref_example.json")
json_ref_absolute_jsonfile_file = "file://" + json_ref_absolute_jsonfile

json_ref_absolute_jsondump_file = {
    "second_name": "bar",
    "$ref": json_ref_absolute_jsonfile_file
}
