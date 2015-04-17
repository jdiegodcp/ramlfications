Usage
=====

You can use ``ramlfications`` to parse and validate a RAML file with Python.
With the command line, you can validate or visualize the RAML-defined API as a tree.

Parse
-----

To parse a RAML file, include ramlfications in your project and call the parse function:

.. doctest::

   >>> import ramlfications
   >>> RAML_FILE = "/path/to/my-api.raml"
   >>> api = ramlfications.parse(RAML_FILE)
   >>> api
   <RootNode(raml_file="path/to/my-api.raml")>
   >>> api.title
   'My Foo API'
   >>> api.version
   'v1'

.. code-block:: python

   >>> api.security_schemes
   [<SecurityScheme(name="oauth_2_0")>]
   >>> oauth2 = api.security_schemes[0]
   >>> oauth2.name
   'oauth_2_0'
   >>> oauth2.type
   'OAuth 2.0'
   >>> oauth2.settings.scopes
   ['playlist-read-private', 'playlist-modify-public',..., 'user-read-email']
   >>> oauth2.settings.access_token_uri
   'https://accounts.foo.com/api/token'

.. code-block:: python

   >>> api.resources
   [<ResourceNode(method='GET', path='/foo')>, <ResourceNode(method='PUT', path='/foo')>, ..., <ResourceNode(method='GET', path='/foo/bar/{id}')>]
   >>> foo_bar = api.resources[-1]
   >>> foo_bar.name
   '/{id}'
   >>> foo_bar.display_name
   'fooBarID'
   >>> foo_bar.absolute_path
   'https://api.foo.com/v1/foo/bar/{id}'
   >>> foo_bar.uri_params
   [<URIParameter(name='id')>]

.. code-block:: python

   >>> uri_param = foo_bar.uri_params[0]
   >>> uri_param.required
   True
   >>> uri_param.type
   'string'
   >>> id_param.example
   'f00b@r1D'

You can pass in an optional config file to add additional values for certain parameters. Find out more \
within the :doc:`extendedusage`:

.. code-block:: python

   >>> CONFIG_FILE = "/path/to/config.ini"
   >>> api = ramlfications.parse(RAML_FILE, CONFIG_FILE)

For more complete understanding of what's available when parsing a RAML file, check the :doc:`extendedusage` \
or the :doc:`api`.


Validate
--------

Validation is according to the `RAML Specification`_.

To validate a RAML file via the command line:

.. code-block:: bash

   $ ramlfications validate /path/to/my-api.raml
   Success! Valid RAML file: tests/data/examples/simple-tree.raml

.. code-block:: bash

    $ ramlfications validate /path/to/invalid/no-title.raml
    Error validating file /path/to/invalid/no-title.raml: RAML File does not define an API title.


To validate a RAML file with Python:

.. code-block:: python

   >>> from ramlfications import validate
   >>> RAML_FILE = "/path/to/my-api.raml"
   >>> validate(RAML_FILE)
   >>>

.. code-block:: python

   >>> from ramlfications import validate
   >>> RAML_FILE = "/path/to/invalid/no-title.raml"
   >>> validate(RAML_FILE)
   InvalidRootNodeError: RAML File does not define an API title.

.. note::
    When using ``validate`` within Python (versus the command line utility), if the RAML \
    file is valid, then nothing is returned.  Only invalid files will return an exception.


Tree
----

To visualize a tree output of a RAML file:

.. code-block:: bash

   $ ramlfications tree /path/to/my-api.raml [-c|--color light/dark] [-v|vv|vvv] [-o|--output]

The least verbose option would show something like this:

.. code-block:: bash

   $ ramlfications tree /path/to/my-api.raml
   ==========
   My Foo API
   ==========
   Base URI: https://api.foo.com/v1
   |– /foo
   |  – /bar
   |  – /bar/{id}

And the most verbose:

.. code-block:: bash

   $ ramlfications tree /path/to/my-api.raml -vvv
   ==========
   My Foo API
   ==========
   Base URI: https://api.foo.com/v1
   |– /foo
   |  ⌙ GET
   |     Query Params
   |      ⌙ q: Foo Query
   |      ⌙ type: Item Type
   |  – /bar
   |    ⌙ GET
   |       Query Params
   |        ⌙ q: Bar Query
   |        ⌙ type: item type
   |  – /bar/{id}
   |    ⌙ GET
   |       URI Params
   |        ⌙ id: ID of foo

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
