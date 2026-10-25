#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB
import io
import os
import re
from setuptools import setup, find_packages


NAME = "ramlfications"
META_PATH = os.path.join("ramlfications", "__init__.py")


HERE = os.path.abspath(os.path.dirname(__file__))


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for fl in filenames:
        with io.open(fl, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


META_FILE = read(META_PATH)


def find_meta(meta):
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = re.search(
        r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))


def install_requires():
    return [
        "attrs", "click", "jsonref", "markdown2", "pyyaml",
        "termcolor", "xmltodict", "inflect"
    ]


long_description = read('README.rst', 'docs/changelog.rst')


setup(
    name=NAME,
    version=find_meta("version"),
    description=find_meta("description"),
    long_description=long_description,
    url=find_meta("uri"),
    license_expression="Apache-2.0",
    license_files=["LICENSE"],
    author=find_meta("author"),
    author_email=find_meta("email"),
    keywords=["raml", "rest"],
    packages=find_packages(exclude=["tests*"]),
    entry_points={
        'console_scripts': [
            'ramlfications = ramlfications.__main__:main'
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    package_data={"": ["data/supported_mime_types.json"]},
    python_requires=">=3.10",
    install_requires=install_requires(),
    extras_require={
        "all": ["requests[security]"]
    },
)
