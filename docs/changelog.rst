Changelog
=========


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
