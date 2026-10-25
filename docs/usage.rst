Usage
=====

You can use ``ramlfications`` to parse and validate a RAML file with Python.
With the command line, you can validate or visualize the RAML-defined API as a tree.

Parse
-----

To parse a RAML file, include ramlfications in your project and call the parse function.
The output below comes from the ``tests/data/raml_08/complete-example.raml`` file in this
repository:

.. code-block:: python

   >>> import ramlfications
   >>> RAML_FILE = "tests/data/raml_08/complete-example.raml"
   >>> api = ramlfications.parse(RAML_FILE)
   >>> api
   RAML08(title='Example Web API')
   >>> api.title
   'Example Web API'
   >>> api.version
   'v1'

.. code-block:: python

   >>> api.security_schemes
   NodeList([SecuritySchemeNode(name='oauth_2_0'), SecuritySchemeNode(name='custom_auth'), SecuritySchemeNode(name='no_desc')])
   >>> oauth2 = api.security_schemes[0]
   >>> oauth2.name
   'oauth_2_0'
   >>> oauth2.type
   'OAuth 2.0'
   >>> oauth2.settings.get("scopes")
   ['user-public-profile', 'user-email', 'user-activity', 'nsa-level-privacy']
   >>> oauth2.settings.get("accessTokenUri")
   'https://accounts.example.com/api/token'

.. code-block:: python

   >>> api.resources
   NodeList([ResourceNode(method='get', path='/widgets'), ResourceNode(method='get', path='/widgets/{id}'), ..., ResourceNode(method='get', path='/no_method_properties/child')])
   >>> widget = api.resources[1]
   >>> widget.name
   '/{id}'
   >>> widget.display_name
   'widget'
   >>> widget.absolute_uri
   'https://{subdomain}.example.com/v1/{communityPath}/widgets/{id}'
   >>> [param.name for param in widget.uri_params]
   ['communityPath', 'id']

.. code-block:: python

   >>> id_param = widget.uri_params[1]
   >>> id_param.required
   True
   >>> id_param.type
   'string'
   >>> id_param.example
   'widget2'

You can pass in an optional config file to add additional values for certain parameters. Find out more \
within the :doc:`extendedusage`:

.. code-block:: python

   >>> CONFIG_FILE = "/path/to/config.ini"
   >>> api = ramlfications.parse(RAML_FILE, CONFIG_FILE)

For more complete understanding of what's available when parsing a RAML file, check the :doc:`extendedusage` \
or the :doc:`api`.


RAML 1.0
--------

The same entry points work for RAML 1.0 documents; the parser detects the
version from the ``#%RAML`` header.  RAML 1.0 features are exposed on the
returned API object:

.. code-block:: python

   >>> api = ramlfications.parse("/path/to/my-1.0-api.raml")
   >>> api.types                        # `types` declarations
   [ObjectDataType(name='Person'), ObjectDataType(name='Employee')]
   >>> api.annotation_types             # `annotationTypes` declarations
   [AnnotationType(name='monitoring')]
   >>> api.resources[0].annotations     # applied `(name): value` annotations
   [Annotation(name='monitoring')]
   >>> api.uses                         # `uses` libraries
   NodeList([Library(name='common')])

Library members are addressable with the dotted ``LibName.member``
notation (e.g. ``type: common.Error``), typed fragment files
(``DataType``, ``Trait``, ``ResourceType``, ``Library``,
``SecurityScheme``, ``DocumentationItem``) can be included from an API
document or parsed standalone, and ``Overlay``/``Extension`` documents
are merged into the API they ``extends`` when parsed.


Validate
--------

Validation is according to the `RAML Specification`_.

To validate a RAML file via the command line:

.. code-block:: bash

   $ ramlfications validate /path/to/my-api.raml
   Success! Valid RAML file: /path/to/my-api.raml

.. code-block:: bash

    $ ramlfications validate /path/to/invalid/no-title.raml
    Error validating file /path/to/invalid/no-title.raml:

        InvalidRootNodeError: RAML File does not define an API title.


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

You may also "turn off" validation when developing via the config file.  To learn more about
``ramlfications`` configuration including turning off validation as well as
default/supported configuration, check out :doc:`config`.

Tree
----

To visualize a tree output of a RAML file:

.. code-block:: bash

   $ ramlfications tree /path/to/my-api.raml [-C|--color light|dark] [-v|vv|vvv] [-o|--output FILENAME] [-V|--validate] [-c|--config PATH]

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

   .. option:: -V, --validate

      Validate the RAML file, even if the config file turns validation off.
      Without this flag, ``tree`` validates unless the config file sets
      ``validate = False``.

   .. option:: -v

      Increase verbose output of the tree one level: adds the HTTP methods

   .. option:: -vv

      Increase verbose output of the tree one level: adds the parameter names

   .. option:: -vvv

      Increase verbose output of the tree one level: adds the parameter display name



.. _`RAML Specification`: http://raml.org/spec.html
.. _GitHub: https://github.com/spotify/ramlfications/blob/master/ramlfications/data/supported_mime_types.json
.. _IANA: https://www.iana.org/assignments/media-types/media-types.xml
