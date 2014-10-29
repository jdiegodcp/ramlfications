.. _api:

API Definition
==============

.. module:: ramlfications

:mod:`parser` Module
--------------------

.. automodule:: ramlfications.parser
.. autoclass:: APIRoot
   :members: resources, title, version, protocols, base_uri, uri_parameters, base_uri_parameters, media_type, resource_types, documentation, security_schemes, traits, schemas

   .. method:: get_parameters

      Returns any defined parameters denoted by double angle brackets, ``<<parameter>>``, for traits and/or resource_types

.. autoclass:: ResourceStack
   :members:

.. autoclass:: Resource
   :members:

:mod:`parameters` Module
------------------------

.. automodule:: ramlfications.parameters
.. autoclass:: BaseParameter
   :members:
   :undoc-members:

.. autoclass:: URIParameter
   :members:
   :undoc-members:
   :inherited-members:

.. autoclass:: QueryParameter
   :members:
   :undoc-members:
   :inherited-members:

.. autoclass:: FormParameter
   :members:
   :undoc-members:
   :inherited-members:

.. autoclass:: Header
   :members:
   :undoc-members:
   :inherited-members:

.. autoclass:: Body
   :members:
   :undoc-members:

.. autoclass:: Response
   :members:
   :undoc-members:

.. autoclass:: ResourceType
   :members:
   :undoc-members:

.. autoclass:: Documentation
   :members:
   :undoc-members:

.. autoclass:: SecuritySchemes
   :members:
   :undoc-members:

.. autoclass:: SecurityScheme
   :members:
   :undoc-members:

.. autoclass:: Oauth2Scheme
   :members:
   :undoc-members:

.. autoclass:: Oauth1Scheme
   :members:
   :undoc-members:


:mod:`loader` Module
--------------------

.. automodule:: ramlfications.loader
.. autoclass:: RAMLLoader

   Opens and loads a given RAML file.

:mod:`utils` Module
-------------------

.. automodule:: ramlfications.utils
.. autoclass:: EndpointOrder
   :members:

:mod:`validate` Module
----------------------

.. automodule:: ramlfications.validate
.. autoclass:: ValidateRAML
   :members: validate