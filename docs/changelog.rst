Changelog
=========

0.3.0 (2026-10-26)
------------------

Added:

- RAML 1.0 support, dispatched automatically from the ``#%RAML`` header
  at the existing ``parse()``/``load()``/``validate()`` entry points:

    * data types with inheritance, facets, and type expressions
      (named types, arrays ``T[]``, unions ``A | B``)
    * ``annotationTypes`` declarations and annotations applied on
      resources and methods
    * ``uses`` libraries with dotted ``LibName.member`` references,
      including libraries used by other libraries
    * typed fragments (DataType, Trait, ResourceType, Library,
      SecurityScheme, DocumentationItem), parsed standalone or included
    * Overlay and Extension documents with RAML 1.0 merge semantics;
      overlays may not change behavioral aspects of their target
    * security scheme updates (RAML 1.0 OAuth 2.0 grants and ``null``
      ``securedBy`` for optional security)

- Version-routed validation: RAML 1.0-only constructs are rejected in
  0.8 documents and vice versa, and RAML 1.0 rules (unresolvable type
  references, annotation value conformance) report located errors that
  are collected rather than failing at the first one.

Changed:

- Python 3.10+ is now the minimum supported version; Python 2 era
  compatibility shims have been removed.
- Dependencies modernized (PyYAML 6.x, current attrs).
- A RAML 0.8 resource assigned a resource type with ``type:`` now gets
  that type's required (non-``?``) methods, including those of the
  type's own ``type:``, as resource nodes. A resource that only declared
  ``type:`` used to produce a single node with ``method=None``; it now
  produces one node per inherited method, so ``len(api.resources)``
  grows for such APIs. Methods the resource declares itself keep their
  order and come first.
- Validation follows the RAML specification where it was stricter:
  RAML 1.0 documents without ``baseUri`` validate (the spec makes it
  OPTIONAL); RAML 0.8 documents without ``baseUri`` validate when the
  config sets ``production = False`` (a missing ``production`` still
  requires it); APIs without resources validate; ``baseUriParameters``
  accept any named-parameter type, not only ``string``.

Fixed:

- RAML 0.8 resource type/trait inheritance edge cases, including
  optional (``?``) properties.
- ``!include`` resolution (nested includes, relative paths, and
  missing-file errors).
- ``<<resourcePathName>>`` is the rightmost path segment for nested
  resources (``widget`` for ``/root/widget``, previously ``root/widget``)
  and is now also substituted when ``type:`` is a plain name.
- Resource type and trait parameters (e.g. ``<<resourceType>>``) are
  substituted in inherited scalar values such as ``description``.
- Inheriting a scalar value through a resource type that has its own
  ``type:`` no longer raises ``TypeError``, and cyclic ``type:`` chains
  no longer raise ``RecursionError``.
- ``ramlfications tree -vv``/``-vvv`` lists form parameters declared
  under a form ``body`` (``ResourceNode.form_params`` is unchanged).
- A resource declared with no value (``/empty:``) parses as a resource
  without properties instead of raising ``AttributeError``.
- RAML 1.0 ``<<resourcePathName>>`` skips path segments that contain a
  URI parameter (``users`` for ``/users/{id}``), as the RAML 1.0 spec
  defines; RAML 0.8 keeps the rightmost segment (``{id}``).
- Parameters a resource type passes to its own ``type:`` (e.g.
  ``type: {base: {thing: <<item>>}}``) are substituted in what it
  inherits from that type.
- A ``documentation`` value that is not a list, and unknown facets in a
  RAML 1.0 type declaration, raise ``InvalidRAMLStructureError`` instead
  of ``AssertionError`` / ``TypeError``.
- ``absolute_uri`` is a string (the resource path) when the API has no
  ``baseUri``; it used to be a one-element list.
- URI/base URI parameter handling (implicit template parameters and
  explicit overrides).
- Passing a config file without a ``[main] validate`` option to
  ``parse()`` or ``ramlfications tree -c`` no longer turns validation
  off; such files now validate, as documented.  To turn validation off,
  set ``validate = False`` (the older spelling ``validation`` is still
  accepted when ``validate`` is not set).
- ``ramlfications tree -V``/``--validate`` now validates the file even
  when the config file turns validation off; the flag used to be
  ignored.

0.1.9 (2015-12-24)
------------------

Happy holidays!

- Fix resource type inheritance (`Issue 23`_ & `Issue 47`_)
- Preserve order of ``baseUriParameters`` and ``uriParameters`` in API root and resource nodes (`Issue 37`_)
- Fix missing URI parameters if not defined/declared inline (`Issue 56`_)
- Fix how arguments are passed into pytest in ``setup.py`` (`PR 55`_ - thank you `matiasb`_!)


0.1.8 (2015-10-07)
------------------

- Fix incorrect/incomplete behavior optional properties of Resource Types (`Issue 44`_).
- Fix ``protocols`` inheritance (`Issue 44`_).
- Partial fix for `Issue 23`_ - incorrect resource type inheritance

    * When a resource type is defined with one method that is optional and is applied to a resource that does *not* have that method defined, the resource’s method should not inherit from the optional method
    * When a resource inherits a resource type but explicitly defines named parameters, the named parameters in the resource should overwrite those that are inherited

0.1.7 (2015-08-20)
------------------

Added:

- Support for parsing ``$ref`` s in included JSON schemas (`Issue 4`_).  Thank you `benhamill`_, `nvillalva`_, and `jhl2343`_!
- Collect all validation errors (rather than just erroring out on the first one) (`Issue 21`_).  Thank you `cerivera`_!


0.1.6 (2015-08-03)
------------------

Added:

- `waffle.io`_ page to documentation for project management overview

Fixed:

- Parse errors when RAML file would have empty mappings (`Issue 30`_)
- Switch ``yaml.Loader`` to ``yaml.SafeLoader`` (`Issue 26`_)
- Update documentation to reflect rearrangement of errors (`Issue 27`_)
- Remove ``default`` parameter from being required for ``baseURIParameters`` (`Issue 29`_)
- Pin mock library for tox tests (`Issue 22`_)
- Experimenting with speeding up pypy tests within tox on Travis

0.1.5 (2015-06-05)
------------------

Fixed:

- Configuration parsing for validation/production.  Thanks `vrajmohan`_!
- Parsing of response bodies (fixes `Issue 12`_).  Thanks `Igor`_!

0.1.4 (2015-05-27)
------------------

Added:

- Support for recursive ``!includes`` in RAML files (0.1.3 would handle the error, now actually supports it. Thanks `Ben`_ for your `PR`_!).

0.1.3 (2015-05-14)
------------------

Added:

- New ``#ramlfications`` channel on `freenode`_ (web chat link)! Come chat, I'm lonely.
- Documentation for configuration and the ``update`` command.

Fixed:

- Handle recursive/cyclical ``!includes`` in RAML files for now (`PR`_)
- Encoding issues from upgrading to tox 2.0
- ``tests/test_utils.py`` would create ``ramlfications/data/supported_mime_types.json``; now mocked out.

0.1.2 (2015-04-21)
------------------

Fixed:

- pypy 2.5.x would fail a parser test because order of list was not expected

0.1.1 (2015-04-21)
------------------

New:

- Added ability to parse IANA-supported MIME media types
- Added ``update`` command for user to update IANA-supported MIME types if/when needed

0.1.0a1 (2015-04-18)
--------------------
Initial alpha release of ``ramlfications``\!


.. _`PR`: https://github.com/spotify/ramlfications/pull/8
.. _`freenode`: http://webchat.freenode.net?channels=%23ramlfications&uio=ND10cnVlJjk9dHJ1ZQb4
.. _`Ben`: https://github.com/benhamill
.. _`vrajmohan`: https://github.com/spotify/ramlfications/pull/16
.. _`Issue 12`: https://github.com/spotify/ramlfications/issues/12
.. _`Igor`: https://github.com/spotify/ramlfications/pull/13
.. _`Issue 30`: https://github.com/spotify/ramlfications/issues/30
.. _`Issue 26`: https://github.com/spotify/ramlfications/issues/26
.. _`Issue 27`: https://github.com/spotify/ramlfications/issues/27
.. _`Issue 29`: https://github.com/spotify/ramlfications/issues/29
.. _`Issue 22`: https://github.com/spotify/ramlfications/issues/22
.. _`waffle.io`: https://waffle.io/spotify/ramlfications
.. _`Issue 4`: https://github.com/spotify/ramlfications/issues/4
.. _`benhamill`: https://github.com/benhamill
.. _`nvillalva`: https://github.com/nvillalva
.. _`jhl2343`: https://github.com/jhl2343
.. _`Issue 21`: https://github.com/spotify/ramlfications/issues/21
.. _`cerivera`: https://github.com/cerivera
.. _`Issue 44`: https://github.com/spotify/ramlfications/issues/44
.. _`Issue 23`: https://github.com/spotify/ramlfications/issues/23
.. _`matiasb`: https://github.com/matiasb
.. _`PR 55`: https://github.com/spotify/ramlfications/pull/55
.. _`Issue 47`: https://github.com/spotify/ramlfications/issues/47
.. _`Issue 37`: https://github.com/spotify/ramlfications/issues/37
.. _`Issue 56`: https://github.com/spotify/ramlfications/issues/56
