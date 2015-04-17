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


Check out :doc:`api` for full definition of ``RootNode`` and its associated attributes and objects.


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

Check out :doc:`api` for full definition of what is available for a ``resource`` object, and its associated attributes and objects.



.. _`RAML Spec's Root Section`: http://raml.org/spec.html#root-section
.. _`RAML Spec's Resource Section`: http://raml.org/spec.html#resources-and-nested-resources
.. _`Spotify's Web API`: https://developer.spotify.com/web-api/
.. _`RAML supports`: http://raml.org/spec.html#security
.. _`resource types and traits`: http://raml.org/spec.html#resource-types-and-traits
.. _`RAML spec`: http://raml.org/spec.html#resource-types-and-traits
