ramlfications: RAML reference implementation in Python
======================================================

.. image:: https://img.shields.io/pypi/v/ramlfications.svg?style=flat-square
   :target: https://pypi.python.org/pypi/ramlfications/
   :alt: Latest Version

.. image:: https://img.shields.io/pypi/status/ramlfications.svg?style=flat-square
    :target: https://pypi.python.org/pypi/ramlfications/
    :alt: Development Status

.. image:: https://img.shields.io/pypi/l/ramlfications.svg?style=flat-square
   :target: https://github.com/spotify/ramlfications/blob/master/LICENSE
   :alt: License

.. image:: https://codecov.io/github/spotify/ramlfications/coverage.svg?branch=master
   :target: https://codecov.io/github/spotify/ramlfications?branch=master
   :alt: Current coverage

.. image:: https://img.shields.io/pypi/pyversions/ramlfications.svg?style=flat-square
    :target: https://pypi.python.org/pypi/ramlfications/
    :alt: Supported Python versions


.. begin

Note: this project has been discontinued at Spotify and will be transferred to a new maintainer, we are currently finishing the transfer of this repository and the associated pypi package. 


Requirements and Installation
=============================

User Setup
----------

The latest stable version can be found on PyPI_, and you can install via pip_::

   $ pip install ramlfications

``ramlfications`` runs on Python 3.10+, and PyPy. Linux , OS X and Windows are supported. Currently, only RAML 0.8 is supported, but there are plans_ to support 1.0.

Continue onto `usage`_ to get started on using ``ramlfications``.


Developer Setup
---------------

If you'd like to contribute or develop upon ``ramlfications``, be sure to read `How to Contribute`_
first.

You can see the progress of ``ramlfications`` on our public `project management`_ page.

System requirements:
^^^^^^^^^^^^^^^^^^^^

- C Compiler (gcc/clang/etc.)
- If on Linux - you'll need to install Python headers (e.g. ``apt-get install python-dev``)
- Python 3.10+, or PyPy
- virtualenv_

Here's how to set your machine up::

    $ git clone git@github.com:jdiegodcp/ramlfications
    $ cd ramlfications
    $ virtualenv env
    $ source env/bin/activate
    (env) $ pip install -r dev-requirements.txt


Run Tests
^^^^^^^^^

If you'd like to run tests for all supported Python versions, you must have all Python versions
installed on your system.  I suggest pyenv_ to help with that.

To run all tests::

    (env) $ tox

To run a specific test setup (options include: ``py310``, ``py311``, ``py312``, ``pypy``,
``flake8``, ``verbose``, ``manifest``, ``docs``, ``setup``, ``setupcov``)::

    (env) $ tox -e py310

To run tests without tox::

    (env) $ py.test
    (env) $ py.test --cov ramlfications --cov-report term-missing


Build Docs
^^^^^^^^^^

Documentation is build with Sphinx_, written in rST, uses the `Read the Docs`_ theme with
a slightly customized CSS, and is hosted on `Read the Docs site`_.

To rebuild docs locally, within the parent ``ramlfications`` directory::

    (env) $ tox -e docs

or::

    (env) $ sphinx-build -b docs/ docs/_build

Then within ``ramlfications/docs/_build`` you can open the index.html page in your browser.


Project History
^^^^^^^^^^^^^^^

Ramlfications was originally created by Spotify engineer github.com/econchick, but is currently not in use at Spotify. The project was discontinued 
in April 2022 and transferred to an external maintainer. 


Still have issues?
^^^^^^^^^^^^^^^^^^

Feel free to drop by ``#ramlfications`` on Freenode (`webchat`_) or ping via `Twitter[X]`_.
"jdiegodcp" is the maintainer, a.k.a `jdiegodcp`_ on GitHub.


.. _pip: https://pip.pypa.io/en/latest/installing.html#install-pip
.. _PyPI: https://pypi.python.org/project/ramlfications/
.. _virtualenv: https://virtualenv.pypa.io/en/latest/
.. _pyenv: https://github.com/yyuu/pyenv
.. _Sphinx: http://sphinx-doc.org/
.. _`Read the Docs`: https://github.com/snide/sphinx_rtd_theme
.. _`Read the Docs site`: https://ramlfications.readthedocs.io
.. _`usage`: https://ramlfications.readthedocs.io/en/latest/usage.html
.. _`How to Contribute`: https://ramlfications.readthedocs.io/en/latest/contributing.html
.. _`webchat`: http://webchat.freenode.net?channels=%23ramlfications&uio=ND10cnVlJjk9dHJ1ZQb4
.. _`jdiegodcp`: https://github.com/jdiegodcp
.. _`Twitter[X]`: https://twitter.com/jdiegodcp
.. _`project management`: https://github.com/jdiegodcp/ramlfications/projects/1
.. _plans: https://github.com/spotify/ramlfications/issues/54
