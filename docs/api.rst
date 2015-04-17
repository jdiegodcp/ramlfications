API Definition
==============

.. automodule:: ramlfications

Main functions
--------------

The following three functions are meant for you to use primarily when parsing a
RAML file/string.


.. autofunction:: parse
.. autofunction:: load
.. autofunction:: loads
.. autofunction:: validate


Core
----

.. note::
    The following documentation is meant for understanding the underlying
    ``ramlfications`` API.  No need to interact directly with the modules,
    classes, & functions below.

parser
^^^^^^


.. autofunction:: ramlfications.parser.parse_raml

.. autofunction:: ramlfications.parser.create_root

.. autofunction:: ramlfications.parser.create_traits

.. autofunction:: ramlfications.parser.create_resource_types

.. autofunction:: ramlfications.parser.create_resources

.. autofunction:: ramlfications.parser.create_node


raml
^^^^

.. py:class:: ramlfications.raml.RootNode

    API Root Node

    .. py:attribute:: raw

        Ordered ``dict`` of all raw data from the RAML file/string.

    .. py:attribute:: version

        ``str`` of API version.

    .. py:attribute:: base_uri

        ``str`` of API's base URI.

    .. py:attribute:: base_uri_params

        ``list`` of base :py:class:`.URIParameter` s for the base URI, or
        ``None``.

    .. py:attribute:: uri_params

        ``list`` of :py:class:`.URIParameter` s that can apply to all
        resources, or ``None``.

    .. py:attribute:: protocols

        ``list`` of ``str`` s of API-supported protocols.  If not defined, is
        inferred by protocol from :py:obj:`.RootNode.base_uri`.

    .. py:attribute:: title

        ``str`` of API's title.

    .. py:attribute:: docs

        ``list`` of :py:class:`.Documentation` objects, or ``None``.

    .. py:attribute:: schemas

        ``list`` of ``dict`` s, or ``None``.

    .. py:attribute:: media_type

        ``str`` of default accepted request/response media type, or ``None``.

    .. py:attribute:: resource_types

        ``list`` of :py:class:`.ResourceTypeNode` objects, or ``None``.

    .. py:attribute:: traits

        ``list`` of :py:class:`.TraitNode` objects, or ``None``.

    .. py:attribute:: security_schemas

        ``list`` of :py:class:`.SecurityScheme` objects, or ``None``.

    .. py:attribute:: resources

        ``list`` of :py:class:`.ResourceNode` objects, or ``None``.

    .. py:attribute:: raml_obj

        The :py:class:`.loader.RAMLDict` object.

.. note::

    :py:class:`.TraitNode`, :py:class:`.ResourceTypeNode`, and
    :py:class:`.ResourceNode` all inherit the following :py:class:`.BaseNode`
    attributes:

.. py:class:: ramlfications.raml.BaseNode

    .. py:attribute:: name

        ``str`` name of ``Node``

    .. py:attribute:: raw

        ``dict`` of the raw data of the ``Node`` from the RAML file/string

    .. py:attribute:: root

        Back reference to the ``Node``’s API :py:class:`.RootNode` object.

    .. py:attribute:: headers

        ``list`` of ``Node``’s :py:class:`.Header` objects, or ``None``

    .. py:attribute:: body

        ``list`` of ``Node``’s :py:class:`.Body` objects, or ``None``

    .. py:attribute:: responses

        ``list`` of ``Node``’s :py:class:`.Response` objects, or ``None``

    .. py:attribute:: uri_params

        ``list`` of ``Node``’s :py:class:`.URIParameter` objects, or ``None``

    .. py:attribute:: base_uri_params

        ``list`` of ``Node``’s base :py:class:`.URIParameter` objects, or ``None``

    .. py:attribute:: query_params

        ``list`` of ``Node``’s :py:class:`.QueryParameter` objects, or ``None``

    .. py:attribute:: form_params

        ``list`` of ``Node``’s :py:class:`.FormParameter` objects, or ``None``.

    .. py:attribute:: media_type

        ``str`` of supported request MIME media type. Defaults to \
        :py:class:`.RootNode`’s ``media_type``.

    .. py:attribute:: description

        ``str`` description of ``Node``.

    .. py:attribute:: protocols

        ``list`` of ``str`` s of supported protocols.  Defaults to \
        :py:obj:`.RootNode.protocols`.


.. py:class:: ramlfications.raml.TraitNode

    Object representing a RAML Trait.

    In addition to the :py:class:`.BaseNode`-defined attributes, ``TraitNode``
    also has:

    .. py:attribute:: usage

        Usage of trait


.. py:class:: ramlfications.raml.ResourceTypeNode

    Object representing a RAML Resource Type.

    In addition to the :py:class:`.BaseNode`-defined attributes,
    ``ResourceTypeNode`` also has:

    .. py:attribute:: display_name

        ``str`` of user-friendly name of resource type, defaults to :py:attr:`.BaseNode.name`

    .. py:attribute:: type

        ``str`` name of inherited :py:class:`.ResourceTypeNode` object,
        or ``None``.

    .. py:attribute:: method

        ``str`` of supported method.

        Removes the ``?`` if present (see :py:attr:`.optional`).

    .. py:attribute:: usage

        ``str`` usage of resource type, or ``None``

    .. py:attribute:: optional

        ``bool`` resource type attributes inherited if applied resource
        defines method (i.e. there is a ``?`` in resource type method).

    .. py:attribute:: is_

        ``list`` of assigned trait names (``str``), or ``None``

    .. py:attribute:: traits

        ``list`` of assigned :py:class:`.TraitNode` objects, or ``None``

    .. py:attribute:: secured_by

        ``list`` of ``str`` s or ``dict`` s of assigned security scheme,
        or ``None``.

        If ``str``, then the name of the security scheme.

        If ``dict``, the key is the name of the scheme, the values
        are the parameters assigned (e.g. relevant OAuth 2 scopes).

    .. py:attribute:: security_schemes

        ``list`` of assigned :py:class:`parameters.SecurityScheme` objects,
        or ``None``.


.. py:class:: ramlfications.raml.ResourceNode

    .. py:attribute:: parent

         parent :py:class:`.ResourceNode` object if any, or ``None``.

    .. py:attribute:: method

        ``str`` HTTP method for resource, or ``None``.

    .. py:attribute:: display_name

        ``str`` of user-friendly name of resource.  Defaults to ``name``.

    .. py:attribute:: path

        ``str`` of relative path of resource.

    .. py:attribute:: absolute_uri

        ``str`` concatenation of absolute URI of resource:
        :py:obj:`.RootNode.base_uri` + :py:attr:`path`.

    .. py:attribute:: is_

        ``list`` of ``str`` s or ``dict`` s of resource-assigned traits,
        or ``None``.

    .. py:attribute:: traits

        ``list`` of assigned :py:class:`.TraitNode` objects, or ``None``.

    .. py:attribute:: type

        ``str`` of the name of the assigned resource type, or ``None``.

    .. py:attribute:: resource_type

        The assigned :py:class:`.ResourceTypeNode` object from \
        :py:attr:`.ResourceNode.type`, or ``None``

    .. py:attribute:: secured_by

        ``list`` of ``str`` s or ``dict`` s of resource-assigned security
        schemes, or ``None``.

        If a ``str``, the name of the security scheme.

        If a ``dict``, the key is the name of the scheme, the values are
        the parameters assigned (e.g. relevant OAuth 2 scopes).

    .. py:attribute:: security_schemes

Parameters
^^^^^^^^^^

.. note::

    The :py:class:`.URIParameter`, :py:class:`.QueryParameter`,
    :py:class:`.FormParameter`, and :py:class:`.Header` objects all share the
    same attributes.

.. py:class:: ramlfications.parameters.URIParameter

    URI parameter with properties defined by the RAML specification's \
    "Named Parameters" section, e.g.: ``/foo/{id}`` where ``id`` is the \
    name of the URI parameter.

.. py:class:: ramlfications.parameters.QueryParameter

    Query parameter with properties defined by the RAML specification's \
    "Named Parameters" section, e.g. ``/foo/bar?baz=123`` where ``baz`` \
    is the name of the query parameter.

.. py:class:: ramlfications.parameters.FormParameter

    Form parameter with properties defined by the RAML specification's
    "Named Parameters" section. Example:

        ``curl -X POST https://api.com/foo/bar -d baz=123``

    where ``baz`` is the Form Parameter name.

.. py:class:: ramlfications.parameters.Header

    Header with properties defined by the RAML spec's 'Named Parameters'
    section, e.g.:

        ``curl -H 'X-Some-Header: foobar' ...``

    where ``X-Some-Header`` is the Header name.


    .. py:attribute:: name

        ``str`` of the name of parameter.

    .. py:attribute:: raw

        ``dict`` of all raw data associated with the parameter from
        the RAML file/string.

    .. py:attribute:: description

        ``str`` parameter description, or ``None``.


    .. py:attribute:: display_name

        ``str`` of a user-friendly name for display or documentation purposes.

        If ``displayName`` is not specified in RAML data, defaults to ``name``.

    .. py:attribute:: min_length

        ``int`` of the parameter's minimum number of characters, or
        ``None``.

        .. note:: Only applies when the parameter's primative ``type`` is ``string``.

    .. py:attribute:: max_length

        ``int`` of the parameter's maximum number of characters, or ``None``.

        .. note:: Only applies when the parameter's primative ``type`` is ``string``.

    .. py:attribute:: minimum

        ``int`` of the parameter's minimum value, or ``None``.

        .. note::

            Only applies when the parameter's primative ``type`` is
            ``integer`` or ``number``.

    .. py:attribute:: maximum

        ``int`` of the parmeter's maximum value, or ``None``.

        .. note::

            Only applies when the parameter's primative ``type`` is
            ``integer`` or ``number``.

    .. py:attribute:: example

        Example value for parameter, or ``None``.

        .. note:: Attribute type of  ``example`` will match that of ``type``.

    .. py:attribute:: default

        Default value for parameter, or ``None``.

        .. note:: Attribute type of ``default`` will match that of ``type``.

    .. py:attribute:: repeat

        ``bool`` if parameter can be repeated.  Defaults to ``False``.

    .. py:attribute:: pattern

        ``str`` of a regular expression that parameter of type ``string``
        must match, or ``None`` if not set.

    .. py:attribute:: enum

        ``list`` of valid parameter values, or ``None``.

        .. note:: Only applies when parameter's primative ``type`` is ``string``.

    .. py:attribute:: type

        ``str`` representation of the primative type of parameter. Defaults
        to ``string`` if not set.

    .. py:attribute:: required

        ``bool`` if parameter is required.

        .. note::

            Defaults to ``True`` if :py:class:`.URIParameter`, else defaults to ``False``.


.. py:class:: ramlfications.parameters.Body

    Body of the request/response.

    .. py:attribute:: mime_type

        ``str`` of the accepted MIME media types for the body of the
        request/response.

    .. py:attribute:: raw

        ``dict`` of all raw data associated with the ``Body`` from
        the RAML file/string

    .. py:attribute:: schema

        ``dict`` of body schema definition, or ``None`` if not set.

        .. note::
            Can not be set if ``mime_type`` is ``multipart/form-data`` or \
            ``application/x-www-form-urlencoded``

    .. py:attribute:: example

        ``dict`` of example of schema, or ``None`` if not set.

        .. note::
            Can not be set if ``mime_type`` is ``multipart/form-data`` or \
            ``application/x-www-form-urlencoded``

    .. py:attribute:: form_params

        ``list`` of :py:class:`.FormParameter` objects accepted in the
        request body.

        .. note::
            Must be set if ``mime_type`` is ``multipart/form-data`` or \
            ``application/x-www-form-urlencoded``.  Can not be used when \
            schema and/or example is defined.

.. py:class:: ramlfications.parameters.Response

    Expected response parameters.

    .. py:attribute:: code

        ``int`` of HTTP response code.

    .. py:attribute:: raw

        ``dict`` of all raw data associated with the ``Response`` from
        the RAML file/string

    .. py:attribute:: description

        ``str`` of the response description, or ``None``.

    .. py:attribute:: headers

        ``list`` of :py:class:`.Header` objects, or ``None``.

    .. py:attribute:: body

        ``list`` of :py:class:`.Body` objects, or ``None``.

    .. py:attribute:: method

        ``str`` of HTTP request method associated with response.

.. py:class:: ramlfications.parameters.Documentation

    User documentation for the API.

    .. py:attribute:: title

        ``str`` title of documentation

    .. py:attribute:: content

        ``str`` content of documentation

.. py:class:: ramlfications.parameters.SecurityScheme

    Security scheme definition.

    .. py:attribute:: name

        ``str`` name of security scheme.

    .. py:attribute:: raw

        ``dict`` of all raw data associated with the ``SecurityScheme`` from
        the RAML file/string

    .. py:attribute:: type

        ``str`` of type of authentication

    .. py:attribute:: described_by

        :py:class:`.Header` s, :py:class:`.Response` s,
        :py:class:`.QueryParameter` s, etc. that is needed/can be expected
        when using security scheme.

    .. py:attribute:: description

        ``str`` description of security scheme.

    .. py:attribute:: settings

        ``dict`` of security schema-specific information


.. autoclass:: ramlfications.parameters.Content
    :members:


Loader
^^^^^^

.. automodule:: ramlfications.loader

.. autoclass:: ramlfications.loader.RAMLLoader
    :members:

Validate
^^^^^^^^

Functions are used when instantiating the classes from ``ramlfications.raml``.

.. automodule:: ramlfications.validate
    :members:

Tree
^^^^

.. automodule:: ramlfications.tree
    :members:
