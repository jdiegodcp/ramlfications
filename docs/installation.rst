Requirements and Installation
=============================

The latest stable version can be found on PyPI_, and you can install via pip_::

   $ pip install ramlfications

``ramlfications`` runs on Python 2.6, 2.7, and 3.3+, and PyPy.

Both Linux and OS X are supported.


Developer Setup
---------------

If you'd like to contribute or develop upon ``ramlfications``, be sure to read :doc:`contributing`
first.

System requirements:
^^^^^^^^^^^^^^^^^^^^

- Python 2.6, 2.7, 3.3+ or PyPy
- virtualenv_

Here's how to set your machine up::

    $ git clone git@github.com:spotify/ramlfications
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

To run a specific test setup (options include: ``py26``, ``py27``, ``py33``, ``py34``, ``pypy``,
``flake8``, ``verbose``, ``manifest``, ``docs``, ``setup``, ``setupcov``)::

    (env) $ tox -e py26

To run tests without tox::

    (env) $ nosetests
    (env) $ nosetests --with-coverage --cover-package=ramlfications


Build Docs
^^^^^^^^^^

Documentation is build with Sphinx_, written in rST, uses the `Read the Docs`_ theme with
a slightly customized CSS, and is hosted on `Read the Docs site`_.

To rebuild docs locally, within the parent ``ramlfications`` directory::

    (env) $ sphinx-build -b docs/ docs/_build

Then within ``ramlfications/docs/_build`` you can open the index.html page in your browser.



.. _pip: https://pip.pypa.io/en/latest/installing.html#install-pip
.. _PyPI: https://pypi.python.org/project/ramlfications/
.. _virtualenv: https://virtualenv.pypa.io/en/latest/
.. _pyenv: https://github.com/yyuu/pyenv
.. _Sphinx: http://sphinx-doc.org/
.. _`Read the Docs`: https://github.com/snide/sphinx_rtd_theme
.. _`Read the Docs site`: https://ramlfications.readthedocs.org
