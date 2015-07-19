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
   RootNode(title='Example Web API')
   >>> api.title
   'My Foo API'
   >>> api.version
   'v1'

.. code-block:: python

   >>> api.security_schemes
   [SecurityScheme(name='oauth_2_0')]
   >>> oauth2 = api.security_schemes[0]
   >>> oauth2.name
   'oauth_2_0'
   >>> oauth2.type
   'OAuth 2.0'
   >>> oauth2.settings.get("scopes")
   ['playlist-read-private', 'playlist-modify-public',..., 'user-read-email']
   >>> oauth2.settings.get("accessTokenUri")
   'https://accounts.foo.com/api/token'

.. code-block:: python

   >>> api.resources
   [ResourceNode(method='get', path='/foo'), ResourceNode(method='put', path='/foo'), ..., ResourceNode(method='get', path='/foo/bar/{id}')]
   >>> foo_bar = api.resources[-1]
   >>> foo_bar.name
   '/{id}'
   >>> foo_bar.display_name
   'fooBarID'
   >>> foo_bar.absolute_uri
   'https://api.foo.com/v1/foo/bar/{id}'
   >>> foo_bar.uri_params
   [URIParameter(name='id')]

.. code-block:: python

   >>> id_param = foo_bar.uri_params[0]
   >>> id_param.required
   True
   >>> id_param.type
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
   >>> RAML_FILE = "/path/to/invalid/no-base-uri-no-title.raml"
   >>> validate(RAML_FILE)
   InvalidRAMLError:
       InvalidRootNodeError: RAML File does not define the baseUri.
       InvalidRootNodeError: RAML File does not define an API title.

.. note::
    When using ``validate`` within Python (versus the command line utility), \
    if the RAML file is valid, then nothing is returned; only invalid files \
    will return an exception.  You can access the individual errors \
    via the ``errors`` attribute on the exception.

If you have additionally supported items beyond the standard (e.g. protocols beyond HTTP/S), you
can still validate your code by passing in your config file.

.. code-block:: bash

   $ cat api.ini
   [custom]
   protocols = FTP

.. code-block:: python

   >>> from ramlfications import validate
   >>> RAML_FILE = "/path/to/support-ftp-protocol.raml"
   >>> CONFIG_FILE = "/path/to/api.ini"
   >>> validate(RAML_FILE, CONFIG_FILE)
   >>>

To learn more about ``ramlfications`` configuration including default/supported configuration,
check out :doc:`config`.

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


Update
------

At the time of this release (|today|), the MIME media types that ``ramlfications`` supports can be found
on `GitHub`_.

However, you do have the ability to update your own setup with the latest-supported MIME media types as
defined by the `IANA`_.  To do so:

.. code-block:: bash

   $ ramlfications update

.. note::
   If you are running Python version 2.7.8 or earlier, or Python version 3.4.2 or earlier, it is
   encouraged to have ``requests[all]`` installed in your environment.
   The command will still work without the package using the standard lib's ``urllib2``, but does
   not perform SSL certificate verification.  Please see `PEP 467`_ for more details.

Options and Arguments
---------------------

The full usage is:

.. code-block:: bash

   $ ramlfications [OPTIONS] COMMAND [ARGS]

The ``RAMLFILE`` is a file containing the RAML-defined API you’d like to work with.

Valid ``COMMAND`` s are the following:

.. option:: validate RAMLFILE

   Validate the RAML file according to the `RAML Specification`_.

   .. program:: validate
   .. option:: -c PATH, --config PATH

      Additionally supported items beyond RAML spec.


.. option:: update

   Update RAMLfications' supported MIME types from IANA.


.. option:: tree RAMLFILE

   Visualize the RAML file as a tree.

   .. program:: tree
   .. option:: -c PATH, --config PATH

      Additionally supported items beyond RAML spec.

   .. option:: -C <light|dark>, --color <light|dark>

      Use a light color scheme for dark terminal backgrounds [DEFAULT], or dark color scheme for light backgrounds.

   .. option:: -o FILENAME, --output FILENAME

      Save tree output to desired file

   .. option:: -v

      Increase verbose output of the tree one level: adds the HTTP methods

   .. option:: -vv

      Increase verbose output of the tree one level: adds the parameter names

   .. option:: -vvv

      Increase verbose output of the tree one level: adds the parameter display name



.. _`RAML Specification`: http://raml.org/spec.html
.. _GitHub: https://github.com/spotify/ramlfications/blob/master/ramlfications/data/supported_mime_types.json
.. _IANA: https://www.iana.org/assignments/media-types/media-types.xml
.. _`PEP 467`: https://www.python.org/dev/peps/pep-0476/
