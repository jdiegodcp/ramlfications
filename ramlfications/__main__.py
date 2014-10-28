#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

import click

from .tree import ttree
from .validate import validate as vvalidate
from .validate import RAMLValidationError


@click.group()
def main():
    """The main routine."""


@main.command(help="Validate a RAML file.")
@click.argument('ramlfile', type=click.Path(exists=True))
def validate(ramlfile):
    """Validate a given RAML file."""
    try:
        vvalidate(ramlfile)
        click.secho("Success! Valid RAML file: {0}".format(ramlfile),
                    fg="green")
    except RAMLValidationError as e:
        click.secho("Error validating file {0}: {1}".format(ramlfile, e),
                    fg="red", err=True)


@main.command(help="Visualize the RAML with a tree.")
@click.argument('ramlfile', type=click.Path(exists=True))
@click.option("-c", "--color", type=click.Choice(['dark', 'light']),
              help=("Color theme 'light' for dark-screened backgrounds"))
@click.option("-v", "--verbose", default=0, count=True,
              help="Include methods for each endpoint")
def tree(ramlfile, color, verbose):
    """Pretty-print a tree of the RAML-defined API."""
    try:
        vvalidate(ramlfile)
        ttree(ramlfile, color, verbose)
    except RAMLValidationError as e:
        click.secho('"{0}" is not a valid RAML File: {1}'
                    .format(click.format_filename(ramlfile), e), fg="red",
                    err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
