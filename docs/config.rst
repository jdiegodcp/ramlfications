Configuration
=============

In support of the `RAML spec`_, ``ramlfications`` will automatically support
the following:

RAML Versions
^^^^^^^^^^^^^

| **Config variable**: ``raml_versions``
| **Config type**: list of strings
| **Supported**: ``0.8``
|


HTTP Methods
^^^^^^^^^^^^
| **Config variable**: ``http_method``
| **Config type**: list of strings
| **Supported**: ``GET``, ``POST``, ``PUT``, ``DELETE``, ``PATCH``, ``HEAD``, ``OPTIONS``, ``TRACE``, ``CONNECT``
|

Authentication Schemes
^^^^^^^^^^^^^^^^^^^^^^

| **Config variable**: ``auth_schemes``
| **Config type**: list of strings
| **Supported**: OAuth 1.0, OAuth 2.0, Basic Authentication, Digest Authentication
|

HTTP Response Codes
^^^^^^^^^^^^^^^^^^^

| **Config variable**: ``resp_codes``
| **Config type**: list of integers
| **Supported**: From Python stdlib ``BaseHTTPServer``
|  ``100``, ``101``,
|  ``200``, ``201``, ``202``, ``203``, ``204``, ``205``, ``206``,
|  ``300``, ``301``, ``302``, ``303``, ``304``, ``305``, ``307``,
|  ``400``, ``401``, ``402``, ``403``, ``404``, ``405``, ``406``, ``407``, ``408``, ``409``, ``410``, ``411``, ``412``, ``413``, ``414``, ``415``, ``416``, ``417``,
|  ``500``, ``501``, ``502``, ``503``, ``504``, ``505``
|

Protocols
^^^^^^^^^

| **Config variable**: ``protocols``
| **Config type**: list of strings
| **Supported**: ``HTTP``, ``HTTPS``
|

MIME Media Types
^^^^^^^^^^^^^^^^

| **Config variable**: ``media_types``
| **Config type**: list of strings that fit the regex defined under `default media type`_: ``application\/[A-Za-z.-0-1]*+?(json|xml)``
| **Supported**: MIME media types that the package supports can be found on `GitHub`_ and is up to date as of the time of this release (|today|).
|

.. note::
    If you would like to update your own setup with the latest `IANA`_ supported MIME media types, refer to :doc:`usage`.

.. _`RAML spec`: http://raml.org/spec.html
.. _`default media type`: http://raml.org/spec.html#default-media-type
.. _IANA: https://www.iana.org/assignments/media-types/media-types.xml
.. _GitHub: https://github.com/spotify/ramlfications/blob/master/ramlfications/data/supported_mime_types.json
