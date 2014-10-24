ramlfications: RAML reference implementation in Python
======================================================

.. image:: https://pypip.in/version/ramlfications/badge.svg
   :target: https://pypi.python.org/pypi/ramlfications/
   :alt: Latest Version

.. image:: https://travis-ci.org/econchick/ramlfications.png?branch=master
   :target: https://travis-ci.org/econchick/ramlfications
   :alt: CI status

.. image:: https://coveralls.io/repos/econchick/ramlfications/badge.png?branch=master
   :target: https://coveralls.io/r/econchick/ramlfications?branch=master
   :alt: Current coverage

.. begin


``ramlfications`` is an Apache 2.0-licensed reference implementation of a `RAML`_ parser in Python intended to be used for parsing API definitions (e.g. for documentation-generation).

If you’ve never heard of `RAML`_, you’re missing out:

    RESTful API Modeling Language (RAML) is a simple and succinct way of describing practically-RESTful APIs.
    It encourages reuse, enables discovery and pattern-sharing, and aims for merit-based emergence of best practices.
    The goal is to help our current API ecosystem by solving immediate problems and then encourage ever-better API patterns.
    RAML is built on broadly-used standards such as YAML and JSON and is a non-proprietary, vendor-neutral open spec.

Why ``ramlfications`` and not `pyraml-parser`_?

I chose to write a new library rather than wrestle with `pyraml-parser`_ as it was not developer-friendly to extend and include required `RAML <http://raml.org/spec.html>`_ features (e.g. `uriParameters`_), as well as a lot of meta programming that is just simply over my head. However, I do encourage you to check out `pyraml-parser`_!  You may find it easier to work with than I did.

``ramlfications``\ ’s documentation lives at `Read the Docs`_, the code on GitHub_.
It’s tested on Python 2.6, 2.7, 3.3+, and PyPy.
Both Linux and OS X are supported.


.. _`Documentation Set`: http://raml.org/
.. _`Read the Docs`: https://ramlfications.readthedocs.org/
.. _`GitHub`:  https://github.com/econchick/ramlfications/
.. _`pyraml-parser`: https://github.com/an2deg/pyraml-parser
.. _`uriParameters`: https://github.com/an2deg/pyraml-parser/issues/6