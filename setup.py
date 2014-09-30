#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from setuptools import setup, find_packages

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
    entry_points={
        'console_scripts': [
            'ramlfications = ramlfications.__main__:main'
        ]
    },
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
    setup_requires=[
        "nose"
    ],
    install_requires=[
        "pyyaml", "ordereddict", "click"
    ],
    tests_require=[
        "nose",
    ],
    test_suite="nose.collector",
)
