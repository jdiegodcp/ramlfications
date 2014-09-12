#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class NoseTest(TestCommand):
    user_options = [('nosetest-args=', 'a', "Arguments to pass to nose")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.nosetest_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import nose
        errno = nose.nosetests.main(self.nosetests_args or [] +
                                    ["test_ramlfications.py"])
        sys.exit(errno)


setup(
    name="ramlfications",
    version="v0.1.0",
    description="Python RAML parser",
    long_description=("TODO"),
    url="https://ramlfications.readthedocs.org/",
    license="Apache License 2.0",
    author="Lynn Root",
    author_email="lynn@spotify.com",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
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
    install_requires=[
        "pyyaml"
    ],
    tests_require=[
        "nose"
    ],
    cmdclass={
        "test": NoseTest,
    },
)
