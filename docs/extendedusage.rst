Extended Usage
==============

To parse a RAML file, include ramlfications in your project and call the parse function:

.. code-block:: python

   >>> import ramlfications
   >>> RAML_FILE = "/path/to/my-api.raml"
   >>> api = ramlfications.parse(RAML_FILE)


Configuration
-------------

Perhaps your API supports response codes beyond what IETF supports (default for this parser). \
Or maybe you implemented your own authentication scheme that your API uses :superscript:`I hope not!`.

Example configuration file::

    [main]
    validate = True

    [custom]
    append = True
    resp_codes = 420, 421, 422
    auth_schemes = oauth_3_0, oauth_4_0
    media_types = application/vnd.github.v3, foo/bar
    protocols = FTP
    raml_versions = 0.8

Feed the configuration into the parse function like so:

.. code-block:: python

   >>> import ramlfications
   >>> RAML_FILE = "/path/to/my-api.raml"
   >>> CONFIG_FILE = "/path/to/my-config.ini"
   >>> api = ramlfications.parse(RAML_FILE, CONFIG_FILE)

RAML Root Section
-----------------

In following the `RAML Spec's Root Section`_ definition, here is how you can access the following attributes:

The Basics
^^^^^^^^^^

.. code-block:: python

   >>> api.title
   'My Other Foo API'
   >>>
   >>> api.version
   v2
   >>> api.raml_version
   "0.8"
   >>> api.base_uri
   'https://{domainName}.foo.com/v2'
   >>> api.base_uri_parameters
   [<URIParameter(name='domainName')>]
   >>>
   >>> api.protocols
   ['HTTPS']

API Documentation
^^^^^^^^^^^^^^^^^

.. code-block:: python

   >>> api.documentation
   [<Documentation(title='The Foo API Docs')>]
   >>> doc = api.documentation[0]
   >>> doc.title
   'The Foo API Docs'


Docs written in the RAML file `should be written using Markdown <http://raml.org/spec.html#user-documentation>`_.
This also applies to any ``description`` parameter.

With ``ramlfications``, documentation content and descriptions can either be viewed raw, or in parsed HTML.

.. code-block:: python

   >>> doc.content
   'Welcome to the _Foo API_ specification. For more information about\nhow to use the API, check out [developer site](https://developer.foo.com).\n'
   >>>
   >>> doc.content.html
   u'<p>Welcome to the <em>Foo API</em> specification. For more information about\nhow to use the API, check out <a href="https://developer.foo.com">developer site</a>.</p>\n'


Check out :doc:`api` for full definition of ``RootNodeAPI08`` and its associated attributes and objects.


Security Schemes
^^^^^^^^^^^^^^^^

`RAML supports`_ OAuth 1, OAuth 2, Basic & Digest, and any authentication scheme self-defined with an ``x-{other}`` header.

To parse auth schemes:

.. code-block:: python

   >>> api.security_schemes
   [<SecurityScheme(name='oauth_2_0')>]
   >>> oauth2 = api.security_schemes[0]
   >>> oauth2.name
   'oauth_2_0'
   >>> oauth2.type
   'OAuth 2.0'
   >>> oauth2.description
   'Foo supports OAuth 2.0 for authenticating all API requests.\n'
   >>> oauth2.description.html
   u'<p>Foo supports OAuth 2.0 for authenticating all API requests.</p>\n'

And its related Headers and Responses:

.. code-block:: python

   >>> oauth2.described_by
   {'headers': [<Header(name='Authorization')>], 'responses': [<Response(code='401')>, <Response(code='403')>]}
   >>> first_header = oauth2.described_by['headers'][0]
   >>> first_header
   <HeaderParameter(name='Authorization')>
   >>> first_header.name
   'Authorization'
   >>> first_headers.description
   'Used to send a valid OAuth 2 access token.\n'
   >>> first_headers.description.html
   u'<p>Used to send a valid OAuth 2 access token.</p>\n'
   >>> resps = oauth2.described_by['responses']
   >>> resps
   [<Response(code='401')>, <Response(code='403')>]
   >>> resp[0].code
   401
   >>> resp[0].description.raw
   'Bad or expired token. This can happen if the user revoked a token or\nthe access token has expired. You should re-authenticate the user.\n'

Authentication settings (available for OAuth1, OAuth2, and any x-header that includes "settings" in the RAML definition).

.. code-block:: python

   >>> oauth2.settings.scopes
   ['foo-read-private', 'foo-modify-public',..., 'user-read-email-address']
   >>> oauth2.settings.access_token_uri
   'https://accounts.foo.com/api/token'
   >>> oauth2.settings.authorization_grants
   ['code', 'token']
   >>> oauth2.settings.authorization_uri
   'https://accounts.foo.com/authorize'

Check out :doc:`api` for full definition of ``SecuritySchemes``, ``Header``, ``Response`` and their associated attributes and objects.

Schemas
^^^^^^^

The RAML specification allows the `ability to define schemas`_ that can be used anywhere within the API definition.  One may define a schema within the RAML file itself, or in another, separate file (local or over HTTP/S).  ``ramlfications`` supports ``json`` and ``xsd`` filetimes in addition to parsing RAML.

See :ref:`nonramlparsing` for more information about how ``ramlfications`` handles ``json`` and ``xsd`` formats.


Traits & Resource Types
^^^^^^^^^^^^^^^^^^^^^^^

Traits & resource types help when API definitions get a bit repetitive.  More information
can be found in the RAML spec for `resource types and traits`_.

Resource Types
~~~~~~~~~~~~~~

.. code-block:: python

    >>> api.resource_types
    [<ResourceTypeNode(name='collection')>, <ResourceTypeNode(name='member')>]
    >>> collection = api.resource_types[0]
    >>> collection.name
    'collection'
    >>> collection.description
    'The collection of <<resourcePathName>>'
    >>> collection.usage
    'This resourceType should be used for any collection of items'
    >>> collection.method
    'get'
    >>> get.optional
    False

Traits
~~~~~~

.. code-block:: python

    >>> api.traits
    [<TraitNode(name='filtered')>, <TraitNode(name='paged')>]
    >>> paged = api.traits[1]
    >>> paged.query_params
    [<QueryParameter(name='offset')>, <QueryParameter(name='limit')>]
    >>> paged.query_params[0].name
    'offset'
    >>> paged.query_params[0].description
    'The index of the first track to return'


RAML1.0 Types
~~~~~~~~~~~~~~

.. code-block:: python

    >>> api.types
    {'Person': ObjectType(name='Person', properties={'name': Property(type='string')})}
    >>> person = api.types['Person']
    >>> person.type
    'object'
    >>> person.description
    'a Person is a type describing human beings'
    >>> person.properties
    {'name': Property(type='string')})
    >>> person.validate({'foo': 'bar'})
    ValidationError: 'foo' is not in the set of allowed properties ('name'). Missing required property 'name'

Mapping of Properties and Elements from Traits & Resource Types to Resources
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a resource has a trait and/or type assigned to it, or a resource type has another \
resource type or a trait assigned to it, it inherits its properties.


Also, the `RAML Spec`_ allows for parameters within Traits and ResourceTypes, denoted by \
double brackets within the Trait/ResourceType definition, e.g. ``<<parameter>>``.  After the parsing \
of the API definition, the appropriate parameters are filled in for the respective resource.

For example, a simplified RAML file::

    #%RAML 0.8
    title: Example API - Mapped Traits
    version: v1
    resourceTypes:
      - searchableCollection:
          get:
            queryParameters:
              <<queryParamName>>:
                description: |
                  Return <<resourcePathName>> that have their <<queryParamName>>
                  matching the given value
              <<fallbackParamName>>:
                description: |
                  If no values match the value given for <<queryParamName>>,
                  use <<fallbackParamName>> instead
      - collection:
          usage: This resourceType should be used for any collection of items
          description: The collection of <<resourcePathName>>
          get:
            description: Get all <<resourcePathName>>, optionally filtered
          post:
            description: Create a new <<resourcePathName | !singularize>>
    traits:
      - secured:
          description: A secured method
          queryParameters:
            <<tokenName>>:
              description: A valid <<tokenName>> is required
      - paged:
          queryParameters:
            numPages:
              description: The number of pages to return, not to exceed <<maxPages>>
    /books:
      type: { searchableCollection: { queryParamName: title, fallbackParamName: digest_all_fields } }
      get:
        is: [ secured: { tokenName: access_token }, paged: { maxPages: 10 } ]


When parsed, the Python notation would look like this:

.. code-block:: python

    >>> RAML_FILE = "/path/to/foo-api.raml"
    >>> api = parse(RAML_FILE)

.. code-block:: python

    # accessing API-supported resource types
    >>> api.resource_types
    [<ResourceTypeNode(method='GET', name='searchableCollection')>,
    <ResourceTypeNode(method='POST', name='collection')>,
    <ResourceTypeNode(method='GET', name='collection')>]
    >>> api.resource_types[0].query_params
    [<QueryParameter(name='<<queryParamName>>')>,
    <QueryParameter(name='<<fallbackParamName>>')>]
    >>> api.resource_types[0].query_params[0].description
    Return <<resourcePathName>> that have their <<queryParamName>> matching the given value

.. code-block:: python

    # accessing API-supported traits
    >>> api.traits
    [<TraitNode(name='secured')>, <TraitNode(name='paged')>]
    >>> api.traits[0].query_params
    [<QueryParameter(name='numPages')>]
    >>> api.traits[0].query_params[0].description
    The number of pages to return, not to exceed <<maxPages>>


.. code-block:: python

    # accessing a single resource
    >>> books = api.resources[0]
    >>> books
    <ResourceNode(method='GET', path='/books')>
    >>> books.type
    {'searchableCollection': {'fallbackParamName': 'digest_all_fields', 'queryParamName': 'title'}}
    >>> books.traits
    [<TraitNode(name='secured')>, <TraitNode(name='paged')>]
    >>> books.query_params
    [<QueryParameter(name='title')>, <QueryParameter(name='digest_all_fields')>,
    <QueryParameter(name='access_token')>, <QueryParameter(name='numPages')>]
    >>> books.query_params[0].description
    Return books that have their title matching the given value
    >>> books.query_params[3].description
    The number of pages to return, not to exceed 10



Resource types can also contain optional properties.  Currently, ``ramlfications`` only supports the ``method`` parameter to be optional, but broadening that to all properties within a defined resource type **and** trait is `coming soon`_.

Below are a few examples of applying a resource type that has a require method, and an optional method.

Example 1
^^^^^^^^^

A required method in a resource type with that method not explicitly defined/included in resource::


    #%RAML 0.8
    ---
    title: Example API
    baseUri: http://example.com
    version: v1
    resourceTypes:
      - inheritgetmethod:
          description: get-method resource type example
          usage: Some sort of usage description
          get:
            description: This description should be inherited when applied to resources
            headers:
              X-Inherited-Header:
                description: This header should be inherited
    /a-get-resource:
      description: Resource inherits from inheritedgetmethod
      type: inheritgetmethod


.. code-block:: python

    >>> len(api.resources)
    1
    >>> res = api.resources[0]
    >>> res.name
    '/a-get-resource'
    >>> res.type
    'inheritedgetmethod'
    >>> res.method  # inherits the required method from its resource type
    'get'
    >>> # also inherits all of it's other properties, if defined
    >>> res.description.raw
    'This description should be inherited when applied to resources'
    >>> res.headers
    [Header(display_name='X-Inherited-Header')]


Example 2
^^^^^^^^^

Similar to the example above, a required method in a resource type where not explicitly defined in the resource, and the resource has another method defined (really confusing to explain, just check out the example)::

    #%RAML 0.8
    ---
    title: Example API
    baseUri: http://example.com
    version: v1
    resourceTypes:
      - inheritgetmethod:
          description: get-method resource type example
          usage: Some sort of usage description
          get:
            description: This description should be inherited when applied to resources
            headers:
              X-Inherited-Header:
                description: This header should be inherited
    /a-resource:
      description: Resource inherits from inheritedgetmethod
      type: inheritgetmethod
      post:
        description: Post some foobar


.. code-block:: python

    >>> len(api.resources)
    2
    >>> first = api.resources[0]
    >>> first.name
    '/a-resource'
    >>> first.type
    'inheritedgetmethod'
    >>> first.method  # inherits the required method from its resource type
    'get'
    >>> second = api.resources[1]
    >>> second.name
    '/a-resources'
    >>> second.method
    'post'


Example 3
^^^^^^^^^

Inheriting an optional resource type method::


    #%RAML 0.8
    ---
    title: Example API
    baseUri: http://example.com
    version: v1
    resourceTypes:
      - inheritgetoptionalmethod:
          description: optional get-method resource type example
          usage: Some sort of usage description
          get?:
            description: This description should be inherited when applied to resources with get methods
            headers:
              X-Optional-Inherited-Header:
                description: This header should be inherited when resource has get method
    /a-resource:
      description: Resource inherits from inheritoptionalmethod
      type: inheritgetoptionalmethod
      get:
        headers:
          X-Explicit-Header:
            description: This is a header in addition to what is inherited

.. code-block:: python

    >>> len(api.resources)
    1
    >>> res = api.resources[0]
    >>> res.name
    '/a-resource'
    >>> res.method
    'get'
    >>> res.headers
    [Header(display_name='X-Optional-Inherited-Header'), Header(display_name='X-Explicit-Header')]



Example 4
^^^^^^^^^

Let's combine all permutations!::


    #%RAML 0.8
    ---
    title: Example API
    baseUri: http://example.com
    version: v1
    resourceTypes:
      - inheritgetmethod:
          description: get-method resource type example
          usage: Some sort of usage description
          get:
            description: This description should be inherited when applied to resources
            headers:
              X-Inherited-Header:
                description: This header should be inherited
      - inheritgetoptionalmethod:
          description: optional get-method resource type example
          usage: Some sort of usage description
          get?:
            description: This description should be inherited when applied to resources with get methods
            headers:
              X-Optional-Inherited-Header:
                description: This header should be inherited when resource has get method
    /a-resource:
      description: Resource inherits from inheritoptionalmethod
      type: inheritgetoptionalmethod
      get:
        headers:
          X-Explicit-Header:
            description: This is a header in addition to what is inherited
    /another-resource:
      type: inheritgetmethod
      description: This resource should also inherit the Resource Type's get method properties
      post:
        description: post some more foobar

.. code-block:: python

    >>> len(api.resources)
    3
    >>> first = api.resources[0]
    >>> first.name
    '/a-resource'
    >>> first.method
    'get'
    >>> second = api.resources[1]
    >>> second.name
    '/another-resource'
    >>> second.method
    'post'
    >>> third = api.resources[2]
    >>> third.method
    'get'


Example 5
^^^^^^^^^

Last thing to note is that properties from the inherited Resource Type will *not* overwrite properties of the resource if they are explicitly defined under the resource::

    #%RAML 0.8
    ---
    title: Example API
    baseUri: http://example.com
    version: v1
    resourceTypes:
      - inheritgetmethod:
          description: get-method resource type example
          usage: Some sort of usage description
          get:
            description: This description should *NOT* be inherited when applied to resources
            headers:
              X-Inherited-Header:
                description: This header should be inherited
    /a-get-resource:
      description: Resource inherits from inheritedgetmethod
      type: inheritgetmethod
      get:
        description: This description will actually be used


.. code-block:: python

    >>> len(api.resources)
    1
    >>> res = api.resources[0]
    >>> res.name
    '/a-get-resource'
    >>> res.type
    'inheritedgetmethod'
    >>> # inherited types will not overwrite properties if explicitly defined in resource
    >>> res.description.raw
    'This description will actually be used'
    >>> res.headers
    [Header(display_name='X-Inherited-Header')]

Check out :doc:`api` for full definition of ``traits`` and ``resources``, and its associated attributes and objects.


Resources
---------

"Resources" are defined in the `RAML Spec's Resource Section`_ and is a
relative URI (relative to the ``base_uri`` and, if nested, relative to
its parent URI).

For example, `Foo API` defines ``/foo/bar`` as a resource (a
"top-level resource" to be exact).  It also defines ``/{id}`` under ``/foo/bar``,
making ``/{id}`` a nested resource, relative to ``/foo/bar``.  The relative path
would be ``/foo/bar/{id}``, and the absolute URI path would be
``https://api.foo.com/v2/foo/bar/{id}``.

.. code-block:: python

   >>> api.resources
   [<Resource(method='GET', path='/foo')>,..., <Resource(method='DELETE', path='/foo/bar/{id}')>]
   >>>
   >>> foo_bar = resources[-1]
   >>> foo_bar.name
   '/{id}'
   >>> foo_bar.description
   '[Delete a foo bar](https://developer.foo.com/api/delete-foo-bar/)\n'
   >>> foo_bar.description.html
   u'<p><a href="https://developer.foo.com/api/delete-foo-bar/">Delete a foo bar</a></p>\n'
   >>> foo_bar.display_name
   'foo bar'
   >>> foo_bar.method
   'delete'
   >>> foo_bar.path
   '/foo/bar/{id}'
   >>> foo_bar.absolute_uri
   'https://api.foo.com/v2/foo/bar/{id}'
   >>> foo_bar.uri_params
   [<URIParameter(name='id')>]
   >>>
   >>> uri_param = foo_bar.uri_params[0]
   >>> uri_param.required
   True
   >>> uri_param.type
   'string'
   >>> uri_param.example
   'f0ob@r1D'
   >>> foo_bar.parent
   <Resource(method='GET', path='/foo/bar/')>

.. note::

  The ``uri_params`` and ``base_uri_params`` on the ``api`` object (``RootNodeAPI08``) and a resource object (``ResourceNode``) will **always** preserve order according to the absolute URI.


Check out :doc:`api` for full definition of what is available for a ``resource`` object, and its associated attributes and objects.


.. _nonramlparsing:

Non-RAML Parsing
----------------

JSON
^^^^

For ``json`` filetypes, ``ramlfications`` will also parse ``$ref`` keywords and bring in the referenced objects according to both `Draft 3`_ and `Draft 4`_ JSON Schema definition.

The following ``$ref`` values are supported:

* :ref:`internalfrag`
* :ref:`localfile`
* :ref:`remotefile`

.. _internalfrag:

Internal fragments
~~~~~~~~~~~~~~~~~~

RAML File:

.. code-block:: yaml

    #%RAML 0.8
    title: Sample API Demo - JSON Includes
    version: v1
    schemas:
        - json: !include includes/ref_internal_fragment.json
    baseUri: http://json.example.com
    /foo:
      displayName: foo resource

``includes/ref_internal_fragment.json`` file:

.. code-block:: json

    {
      "references": {
        "internal": "yes"
      },
      "name": "foo",
      "is_this_internal?": [{"$ref": "#/references/internal"}]
    }


``ramlfications`` would produce the following:

.. code-block:: pycon

    >>> RAML_FILE = "api.raml"
    >>> api = parse(RAML_FILE)
    >>> api.schemas
    [{'json': {u'is_this_internal?': [u'yes'],
    u'name': u'foo',
    u'references': {u'internal': u'yes'}}}]

.. _localfile:

Local file with & without fragments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Parsing references to local files via relative or absolute filepaths work fine, as well as prepending the URI with ``file:``, e.g. ``file:local.schema.json``.


RAML File that includes a JSON file under ``schemas``:

.. code-block:: yaml

    #%RAML 0.8
    title: Sample API Demo - JSON Includes
    version: v1
    schemas:
        - jsonexample: !include local.schema.json
    baseUri: http://json.example.com
    /foo:
      displayName: foo resource


The included ``local.schema.json`` file that refers to another JSON file via a relative filepath and a fragment:

.. code-block:: json

    {
      "$schema":"http://json-schema.org/draft-03/schema",
      "type": "object",
      "properties": {
        "album_type": {
          "type": "string",
          "description": "The type of the album: one of 'album', 'single', or 'compilation'."
        },
        "artists": {
            "type": "array",
            "description": "The artists of the album. Each artist object includes a link in href to more detailed information about the artist.",
            "items": [{ "$ref": "artist.schema.json#properties" }]
        }
      }
    }

The referred ``artist.schema.json`` file:

.. code-block:: json

    {
      "$schema": "http://json-schema.org/draft-03/schema",
      "type": "object",
      "properties": {
        "name": {
          "type": "string",
          "description": "The name of the artist."
        },
        "popularity": {
          "type": "integer",
          "description": "The popularity of the artist. The value will be between 0 and 100, with 100 being the most popular. The artist's popularity is calculated from the popularity of all the artist's tracks."
        },
        "type": {
          "type": "string",
          "description": "The object type: 'artist'"
        },
        "uri": {
          "type": "string",
          "description": "The Spotify URI for the artist."
        }
      }
    }


Finally, ``ramlfications`` would produce the following (pretty printed for readability):

.. code-block:: pycon

    >>> RAML_FILE = "api.raml"
    >>> api = parse(RAML_FILE)
    >>> api.schemas
    [{'jsonexample': {
      u'$schema': u'http://json-schema.org/draft-03/schema',
      u'properties': {
        u'album_type': {
          u'description': u"The type of the album: one of 'album', 'single', or 'compilation'.",
          u'type': u'string'
        },
        u'artists': {
          u'description': u'The artists of the album. Each artist object includes a link in href to more detailed information about the artist.',
          u'items': [{
            u'popularity': {
              u'type': u'integer',
              u'description': u"The popularity of the artist. The value will be between 0 and 100, with 100 being the most popular. The artist's popularity is calculated from the popularity of all the artist's tracks."
            },
            u'type': {
              u'type': u'string',
              u'description': u"The object type: 'artist'"
            },
            u'name': {
              u'type': u'string',
              u'description': u'The name of the artist.'
            },
            u'uri': {
              u'type': u'string',
              u'description': u'The Spotify URI for the artist.'
            }
          }],
        u'type': u'array'
        }
      },
      u'type': u'object'
      }
    }]


.. _remotefile:

Remote file with & without fragments (over HTTP or HTTPS only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

RAML file:

.. code-block:: yaml

    #%RAML 0.8
    title: Sample API Demo - JSON Includes
    version: v1
    schemas:
        - json: !include local.schema.json
    baseUri: http://json.example.com
    /foo:
      displayName: foo resource


The included ``local.schema.json`` file (that's local) that refers to another JSON file remotely:

.. code-block:: json

    {
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
                "items": [{"$ref": "https://example.com/data#properties"}]
            }
        }
    }

The remote file found on ``https://example.com/data#properties``:

.. code-block:: json

    {
      "$schema": "http://json-schema.org/draft-03/schema",
      "type": "object",
      "properties": {
        "height": {
          "type": "integer",
          "description": "The image height in pixels. If unknown: null or not returned."
        },
        "url": {
          "type": "string",
          "description": "The source URL of the image."
        },
        "width": {
          "type": "integer",
          "description": "The image width in pixels. If unknown: null or not returned."
        }
      }
    }


Finally, ``ramlfications`` would produce the following (pretty printed for readability):

.. code-block:: pycon

    >>> RAML_FILE = "api.raml"
    >>> api = parse(RAML_FILE)
    >>> api.schemas
    [{'jsonexample': {
      u'$schema': u'http://json-schema.org/draft-03/schema',
      u'properties': {
        u'name': {
          u'type': u'string',
          u'description': u'The name of the artist.'
        },
        u'images': {
          u'type': 'array',
          u'description': 'Images associated with artist',
          u'items': [{
            u'height': {
              u'type': u'integer',
              u'description': u'The image height in pixels. If unknown: null or not returned.'
            },
            u'url': {
              u'type': u'string',
              u'description': u'The source URL of the image.'
            },
            u'width': {
              u'type': u'integer',
              u'description': u'The image width in pixels. If unknown: null or not returned.'
            }
          }]
        }
      }
    }}]


XML
^^^

Documentation (and improved functionality) coming soon!

.. _`RAML Spec's Root Section`: http://raml.org/spec.html#root-section
.. _`RAML Spec's Resource Section`: http://raml.org/spec.html#resources-and-nested-resources
.. _`Spotify's Web API`: https://developer.spotify.com/web-api/
.. _`RAML supports`: http://raml.org/spec.html#security
.. _`resource types and traits`: http://raml.org/spec.html#resource-types-and-traits
.. _`RAML spec`: http://raml.org/spec.html#resource-types-and-traits
.. _`ability to define schemas`: http://raml.org/spec.html#schemas
.. _`Draft 3`: https://tools.ietf.org/html/draft-zyp-json-schema-03
.. _`Draft 4`: https://tools.ietf.org/html/draft-zyp-json-schema-04
.. _`coming soon`: https://github.com/spotify/ramlfications/issues/43
