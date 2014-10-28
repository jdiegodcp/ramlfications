:orphan:

Wishlist, TODOs, and Contribution Inspiration
=============================================

Ideally, this should mirror the `issues`_ listed on the ``ramlfications`` `github`_ page.  Ideally.

* Features:
    * ``[x]`` Parsing of Markdown in Documentation
    * ``[x]`` Tests for parsing of Markdown in Descriptions
    * ``[ ]`` Parse `mediaTypeExtension` as a reserved URI parameter
    * ``[ ]`` baseUriParameters may overwrite those in the Root
    * ``[x]`` Parsing of non-JSON/RAML/YAML schemas in Body (e.g. xml)
    * ``[ ]`` Add ability to "pluralize" and "singularize" parameters in resourceTypes and traits
    * ``[ ]`` Map resourceTypes and traits defined in Root to Nodes
    * ``[ ]`` Parse `$ref` in JSON schemas
    * RAML Validation functionality:
        - ``[ ]`` validate `media_type`
        - ``[ ]`` validate each Node's `secured_by`

    * ``[-]`` Add repr/str overrides to all Classes
    * ``[x]`` RAML Visualization/tree functionality
    * API Documentation/Resource description parsing:
        - ``[ ]`` RTF output
        - ``[ ]`` other output type?

* Documentation (ramlfications.readthedocs.org):
    - ``[-]`` User docs
    - ``[-]`` docstrings with ``params``, ``returns``, and ``raises`` defined
    - ``[ ]`` perhaps doctests
    - ``[ ]`` colorize the "tree" documentation within usage to show ``--light`` and ``--dark``
    - ``[ ]`` colorize bash/terminal commands

* Other:
    * ``[ ]`` Travis Setup (depends on releasing to github)
    * ``[ ]`` Coveralls Setup (depends on releasing to github)

.. note::
    * ``[x]`` - completed recently (task item will be removed entirely at some point).
    * ``[-]`` - started task.
    * ``[ ]`` - the task is up for grabs.

.. _`github`: https://github.com/econchick/ramlfications
.. _`issues`: https://github.com/econchick/ramlfications/issues
