Usage
=====

You can use ``ramlfications`` to parse and validate a RAML file with Python.
With the command line, you can validate or visualize the RAML-defined API as a tree.

Parse
-----

To parse a RAML file, include ramlfications in your project and call the parse function:

.. code-block:: python

   >>> import ramlfications
   >>> RAML_FILE = "/path/to/my-api.raml"
   >>> loaded_raml = ramlfications.load(RAML_FILE)
   >>> api = ramlfications.parse(loaded_raml)
   >>> api.title
   'Spotify Web API'

.. code-block:: python

   >>> api.security_schemes
   [< Security Scheme: OAuth 2.0 >]
   >>> oauth2 = api.security_schemes[0]
   >>> oauth2.name
   'oauth_2_0'
   >>> oauth2.type
   'OAuth 2.0'
   >>> oauth2.settings.scopes
   ['playlist-read-private', 'playlist-modify-public',..., 'user-read-email']
   >>> oauth2.settings.access_token_uri
   'https://accounts.spotify.com/api/token'

.. code-block:: python

   >>> api.resources
   ['get-several-tracks', 'get-current-user', 'get-users-profile',..., 'delete-playlist-tracks']
   >>> track = api.resources[4]
   >>> track.name
   '/{id}'
   >>> track.display_name
   'track'
   >>> track.absolute_path
   'https://api.spotify.com/v1/tracks/{id}'
   >>> track.uri_params
   [<URIParameter(name='id')>]

.. code-block:: python

   >>> id_param = track.uri_params[0]
   >>> id_param.required
   True
   >>> id_param.type
   'string'
   >>> id_param.example
   '1zHlj4dQ8ZAtrayhuDDmkY'

For more complete understanding of what's available when parsing a RAML file, check the :doc:`extendedusage`!


Validate
--------

Validation is according to the `RAML Specification`_.

.. comment:
   TODO: add a note saying what is not yet supported when validating,
   and add to the wishlist/todo list.

To validate a RAML file via the command line:

.. code-block:: bash

   $ ramlfications validate /path/to/my-api.raml

To validate a RAML file with Python:

.. code-block:: python

   >>> import ramlfications
   >>> RAML_FILE = "/path/to/my-api.raml"
   >>> ramlfications.validate(RAML_FILE)

Tree
----

To visualize a tree output of a RAML file:

.. code-block:: bash

   $ ramlfications tree /path/to/my-api.raml [-c|--color light/dark] [-v|vv|vvv] [-o|--output]

The least verbose option would show something like this:

.. code-block:: bash

   ===============
   Spotify Web API
   ===============
   Base URI: https://api.spotify.com/v1
   |– /search
   |– /tracks
   |  – /tracks/{id}

And the most verbose:

.. code-block:: bash

   ===============
   Spotify Web API
   ===============
   Base URI: https://api.spotify.com/v1
   |– /search
   |  ⌙ GET
   |     Query Params
   |      ⌙ q: Query
   |      ⌙ type: Item Type
   |– /tracks
   |  ⌙ GET
   |     Query Params
   |      ⌙ ids: Spotify Track IDs
   |  – /tracks/{id}
   |    ⌙ GET
   |       URI Params
   |        ⌙ id: Spotify Track ID


Options and Arguments
---------------------

The full usage is:

.. code-block:: bash

   $ ramlfications [OPTIONS] COMMAND RAMLFILE

The ``RAMLFILE`` is a file containing the RAML-defined API you’d like to work with.

Valid ``COMMAND`` s are the following:

.. option:: validate

   Validate the RAML file according to the `RAML Specification`_.

.. option:: tree

   Visualize the RAML file via your console.


Valid ``OPTIONS`` for all commands are the following:

.. option:: --help

   Show a brief usage summary and exit.

Valid ``OPTIONS`` for the ``tree`` command are the following:

.. option:: -c light|dark

   Use a light color scheme for dark terminal backgrounds [DEFAULT], or dark color scheme for light backgrounds.

.. option:: --color light|dark

   Use a light color scheme for dark terminal backgrounds [DEFAULT], or dark color scheme for light backgrounds.

.. option:: -o

   Save tree output desired file

.. option:: --output

   Save tree output desired file

.. option:: -v

   Increase verbose output of the tree one level: adds the HTTP methods

.. option:: -vv

   Increase verbose output of the tree one level: adds the parameter names

.. option:: -vvv

   Increase verbose output of the tree one level: adds the parameter display name




.. _`RAML Specification`: http://raml.org/spec.html
