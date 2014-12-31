API Definition
==============

.. module:: ramlfications

Helper functions
----------------

.. module:: ramlfications

.. method:: parse(raml_file)

    Module helper function to parse a RAML File.  First loads the RAML file
    with :py:class:`.loader.RAMLLoader` then parses with
    :py:func:`.parser.parse_raml` to return a :py:class:`.raml.RAMLRoot`
    object.

    :param str raml_file: String path to RAML file
    :return: parsed API
    :rtype: RAMLRoot
    :raises LoadRamlFileError: If error occurred trying to load the RAML file
        (see :py:class:`.loader.RAMLLoader`)
    :raises RAMLParserError: If error occurred during parsing of RAML file
        (see :py:class:`.raml.RAMLRoot`)


.. method:: load(raml_file)

    Module helper function to load a RAML File using :py:class:`.loader.RAMLLoader`.

    :param str raml_file: String path to RAML file
    :return: loaded RAML file
    :rtype: RAMLDict
    :raises LoadRamlFileError: If error occurred trying to load the RAML file
        (see :py:class:`.loader.RAMLLoader`)

.. method:: validate(raml_file, production=True)

    Module helper function to validate a RAML File.  First loads the RAML file
    with :py:class:`.loader.RAMLLoader` then validates with :py:func:`.validate.validate_raml`.

    :param str raml_file: String path to RAML file
    :param bool production: If the RAML file is meant to be production-ready
    :return: No return value if successful
    :raises LoadRamlFileError: If error occurred trying to load the RAML file
        (see :py:class:`.loader.RAMLLoader`)
    :raises InvalidRamlFileError: If error occurred trying to validate the RAML
        file (see :py:mod:`.validate`)

Modules
-------

parser Module
^^^^^^^^^^^^^

.. automodule:: ramlfications.parser


raml Module
^^^^^^^^^^^

.. automodule:: ramlfications.raml


parameters Module
^^^^^^^^^^^^^^^^^

.. automodule:: ramlfications.parameters
   :exclude-members: String, IntegerNumber, Boolean, Date, File


loader Module
^^^^^^^^^^^^^

.. automodule:: ramlfications.loader

validate Module
^^^^^^^^^^^^^^^

.. automodule:: ramlfications.validate

tree Module
^^^^^^^^^^^

.. automodule:: ramlfications.tree


Primative Types
---------------

Primative types for a parameter’s resolved value, per `RAML Spec <http://raml.org/spec.html#type>`_.

.. automodule:: ramlfications.parameters
    :exclude-members: ContentType, Content, BaseParameter, URIParameter,
        QueryParameter, FormParameter, Header, Body, Response,
        Documentation, SecurityScheme, Oauth2Scheme, Oauth1Scheme,
        CustomAuthScheme
