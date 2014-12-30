.. _api:

API Definition
==============

.. module:: ramlfications

Helper functions
----------------

.. automodule:: ramlfications.__init__
.. autofunction:: parse
.. autofunction:: load
.. autofunction:: validate


:mod:`parser` Module
--------------------

.. automodule:: ramlfications.parser
.. autofunction:: parse_raml

:mod:`raml` Module
------------------

.. automodule:: ramlfications.raml
.. autoclass:: RAMLRoot
   :members:

.. autoclass:: Resource
   :members:

.. autoclass:: ResourceType
   :members:

.. autoclass:: Trait

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

.. autoclass:: ContentType
   :members:
   :undoc-members:
   :inherited-members:

.. autoclass:: Body
   :members:
   :undoc-members:

.. autoclass:: Response
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


:mod:`validate` Module
----------------------

.. automodule:: ramlfications.validate
   :members:

:mod:`tree` Module
------------------

.. automodule:: ramlfications.tree
   :members: ttree
