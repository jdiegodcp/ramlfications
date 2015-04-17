:orphan:

Introduction
============

.. begin

``ramlfications`` is an Apache 2.0-licensed reference implementation of a
`RAML`_ parser in Python intended to be used for parsing API definitions
(e.g. for static documentation-generation).

If you’ve never heard of `RAML`_, you’re missing out:

    RESTful API Modeling Language (RAML) is a simple and succinct way of describing practically-RESTful APIs.
    It encourages reuse, enables discovery and pattern-sharing, and aims for merit-based emergence of best practices.
    The goal is to help our current API ecosystem by solving immediate problems and then encourage ever-better API patterns.
    RAML is built on broadly-used standards such as YAML and JSON and is a non-proprietary, vendor-neutral open spec.

Why ``ramlfications`` and not `pyraml-parser`_?
-----------------------------------------------

I chose to write a new library rather than wrestle with `pyraml-parser`_ as it
was not developer-friendly to extend (in my PoV, others may have more success)
and did not include required `RAML <http://raml.org/spec.html>`_ features
(e.g. `uriParameters`_, parsing of security schemes, etc), as well as a lot
of meta programming that is just simply over my head.  However, I do
encourage you to check out `pyraml-parser`_! You may find it easier to work with than I did.

About
-----
``ramlfications``\ ’s documentation lives at `Read the Docs`_, the code on GitHub_.
It’s tested on Python 2.6, 2.7, 3.3+, and PyPy. Both Linux and OS X are supported.


.. _`Documentation Set`: http://raml.org/
.. _`Read the Docs`: https://ramlfications.readthedocs.org/
.. _`GitHub`:  https://github.com/spotify/ramlfications/
.. _`pyraml-parser`: https://github.com/an2deg/pyraml-parser
.. _`uriParameters`: https://github.com/an2deg/pyraml-parser/issues/6
