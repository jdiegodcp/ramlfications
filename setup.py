#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
import io
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand  # NOQA


def install_requires():
    install_requires = [
        "attrs", "click", "markdown2", "pyyaml", "six", "termcolor",
        "xmltodict"
    ]
    if sys.version_info[:2] == (2, 6):
        install_requires.append("ordereddict")
    return install_requires


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for fl in filenames:
        with io.open(fl, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.rst', 'docs/changelog.rst')


class PyTest(TestCommand):
    user_options = [("pytest-args=", "a", "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args or [] + ["tests"])
        sys.exit(errno)

setup(
    name="ramlfications",
    version="0.1.0a1",
    description="Python RAML parser",
    long_description=long_description,
    url="https://ramlfications.readthedocs.org/",
    license="Apache License 2.0",
    author="Lynn Root",
    author_email="lynn@spotify.com",
    packages=find_packages(exclude=["tests"]),
    entry_points={
        'console_scripts': [
            'ramlfications = ramlfications.__main__:main'
        ]
    },
    classifiers=[
        "Development Status :: 3 – Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: Apache License 2.0",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=install_requires(),
    tests_require=[
        "pytest",
    ],
    cmdclass={
        "test": PyTest,
    }
)
