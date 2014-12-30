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

User Documentation
^^^^^^^^^^^^^^^^^^

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


.. note::
  When accessing ``traits`` or ``resource_types`` from a ``Resource`` object, the <<parameters>>
  are mapped/replaced with their appropriate value as defined in the RAML file.

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
