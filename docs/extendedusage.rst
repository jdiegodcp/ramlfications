Extended Usage
==============

To parse a RAML file, include ramlfications in your project and call the parse function:

.. code-block:: python

   >>> import ramlfications
   >>> RAML_FILE = "/path/to/my-api.raml"
   >>> api = ramlfications.parse(RAML_FILE)


RAML Root Section
-----------------

In following the `RAML Spec's Root Section`_ definition, here is how you can access the following attributes:

The Basics
^^^^^^^^^^

.. code-block:: python

   >>> api.title
   'Spotify Web API'
   >>>
   >>> api.version
   v1
   >>> api.base_uri
   'https://{domainName}.spotify.com/v1'
   >>> api.base_uri_parameters
   [<URIParameter(name='domainName')>]
   >>>
   >>> api.protocols
   ['HTTPS']

API Documentation
^^^^^^^^^^^^^^^^^

.. code-block:: python

   >>> api.documentation
   [<Documentation(title='Spotify Web API Docs')>]
   >>> doc = api.documentation[0]
   >>> doc.title
   'Spotify Web API Docs'


Docs written in the RAML file `should be written using Markdown <http://raml.org/spec.html#user-documentation>`_.
This also applies to any ``description`` parameter.

With ``ramlfications``, documentation content and descriptions can either be viewed raw, or in parsed HTML.

.. code-block:: python

   >>> doc.content
   'Welcome to the _Spotify Web API_ specification. For more information about\nhow to use the API, check out [developer site](https://developer.spotify.com/web-api/).\n'
   >>>
   >>> doc.content.html
   u'<p>Welcome to the <em>Spotify Web API</em> specification. For more information about\nhow to use the API, check out <a href="https://developer.spotify.com/web-api/">developer site</a>.</p>\n'


Check out :doc:`api` for full definition of ``RAMLRoot`` and its associated attributes and objects.


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
   'Spotify supports OAuth 2.0 for authenticating all API requests.\n'
   >>> oauth2.description.html
   u'<p>Spotify supports OAuth 2.0 for authenticating all API requests.</p>\n'

And its related Headers and Responses:

.. code-block:: python

   >>> oauth2.described_by
   {'headers': [<HeaderParameter(name='Authorization')>], 'responses': [<Response(code='401')>, <Response(code='403')>]}
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
   ['playlist-read-private', 'playlist-modify-public',..., 'user-read-email']
   >>> oauth2.settings.access_token_uri
   'https://accounts.spotify.com/api/token'
   >>> oauth2.settings.authorization_grants
   ['code', 'token']
   >>> oauth2.settings.authorization_uri
   'https://accounts.spotify.com/authorize'

Check out :doc:`api` for full definition of ``SecuritySchemes``, ``Header``, ``Response`` and their associated attributes and objects.


Traits & Resource Types
^^^^^^^^^^^^^^^^^^^^^^^

Traits & resource types help when API definitions get a bit repetitive.  More information
can be found in the RAML spec for `resource types and traits`_.

Resource Types
~~~~~~~~~~~~~~

.. code-block:: python

    >>> api.resource_types
    [<ResourceType(name='collection')>, <ResourceType(name='member')>]
    >>> collection = api.resource_types[0]
    >>> collection.name
    'collection'
    >>> collection.description
    'The collection of <<resourcePathName>>'
    >>> collection.usage
    'This resourceType should be used for any collection of items'
    >>> collection.methods
    [<ResourceTypeMethod(name='get')>, <ResourceTypeMethod(name='post')>]
    >>> get = collection.methods[0]
    >>> get.name
    'get'
    >>> get.optional
    False

Traits
~~~~~~

.. code-block:: python

    >>> api.traits
    [<Trait(name='filtered')>, <Trait(name='paged')>]
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
                description: Return <<resourcePathName>> that have their <<queryParamName>> matching the given value
              <<fallbackParamName>>:
                description: If no values match the value given for <<queryParamName>>, use <<fallbackParamName>> instead
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

    >>> RAML_FILE = "/path/to/simplified-api.raml"
    >>> api = parse(RAML_FILE)

.. code-block:: python

    # accessing API-supported resource types
    >>> api.resource_types
    [<ResourceType(method='GET', name='searchableCollection')>,
    <ResourceType(method='POST', name='collection')>,
    <ResourceType(method='GET', name='collection')>]
    >>> api.resource_types[0].query_params
    [<QueryParameter(name='<<queryParamName>>')>,
    <QueryParameter(name='<<fallbackParamName>>')>]
    >>> api.resource_types[0].query_params[0].description
    Return <<resourcePathName>> that have their <<queryParamName>> matching the given value

.. code-block:: python

    # accessing API-supported traits
    >>> api.traits
    [<Trait(name='secured')>, <Trait(name='paged')>]
    >>> api.traits[0].query_params
    [<QueryParameter(name='numPages')>]
    >>> api.traits[0].query_params[0].description
    The number of pages to return, not to exceed <<maxPages>>


.. code-block:: python

    # accessing a single resource
    >>> books = api.resources[0]
    >>> books
    <Resource(method='GET', path='/books')>
    >>> books.type
    {'searchableCollection': {'fallbackParamName': 'digest_all_fields', 'queryParamName': 'title'}}
    >>> books.traits
    [<Trait(name='secured')>, <Trait(name='paged')>]
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

For example, `Spotify's Web API`_ defines ``/tracks`` as a resource (a
"top-level resource" to be exact).  It also defines ``/{id}`` under ``/tracks``,
making ``/{id}`` a nested resource, relative to ``/tracks``.  The relative path
would be ``/tracks/{id}``, and the absolute URI path would be
``https://api.spotify.com/v1/tracks/{id}``.

.. code-block:: python

   >>> api.resources
   [<Resource(method='GET', path='/tracks')>,..., <Resource(method='DELETE', path='/users/{user_id}/playlists/{playlist_id/tracks')>]
   >>>
   >>> track = resources[5]
   >>> track.name
   '/{id}'
   >>> track.description
   '[Get a Track](https://developer.spotify.com/web-api/get-track/)\n'
   >>> track.description.html
   u'<p><a href="https://developer.spotify.com/web-api/get-track/">Get a Track</a></p>\n'
   >>> track.display_name
   'track'
   >>> track.method
   'get'
   >>> track.path
   '/tracks/{id}'
   >>> track.absolute_uri
   'https://api.spotify.com/v1/tracks/{id}'
   >>> track.uri_params
   [<URIParameter(name='id')>]
   >>>
   >>> id_param = track.uri_params[0]
   >>> id_param.required
   True
   >>> id_param.type
   'string'
   >>> id_param.example
   '1zHlj4dQ8ZAtrayhuDDmkY'
   >>> track.parent
   <Resource(method='GET', path='/tracks/')>

Check out :doc:`api` for full definition of what is available for a ``resource`` object, and its associated attributes and objects.



.. _`RAML Spec's Root Section`: http://raml.org/spec.html#root-section
.. _`RAML Spec's Resource Section`: http://raml.org/spec.html#resources-and-nested-resources
.. _`Spotify's Web API`: https://developer.spotify.com/web-api/
.. _`RAML supports`: http://raml.org/spec.html#security
.. _`resource types and traits`: http://raml.org/spec.html#resource-types-and-traits
.. _`RAML spec`: http://raml.org/spec.html#resource-types-and-traits
