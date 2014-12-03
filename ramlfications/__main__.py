#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function

import click

from .loader import RAMLLoader
from .tree import ttree
from .validate import validate_raml
from .validate import InvalidRamlFileError


@click.group()
def main():
    """The main routine."""
    # Is this used for anything? Can it be removed and improved somehow?
    # LR: @click.group() collects all below and attributes it to the main()


@main.command(help="Validate a RAML file.")
@click.argument('ramlfile', type=click.Path(exists=True))
def validate(ramlfile):
    """Validate a given RAML file."""
    try:
        # Can the next line throw IOError that is not caught in the
        # except block?

        # LR: the @click.argument checks to see if the RAML file exists
        validate_raml(ramlfile, prod=True)
        click.secho("Success! Valid RAML file: {0}".format(ramlfile),
                    fg="green")

    except InvalidRamlFileError as e:
        msg = "Error validating file {0}: {1}".format(ramlfile, e)
        click.secho(msg, fg="red", err=True)
        raise SystemExit(1)


@main.command(help="Visualize the RAML file as a tree.")
@click.argument('ramlfile', type=click.Path(exists=True))
@click.option("-c", "--color", type=click.Choice(['dark', 'light']),
              default=None,
              help=("Color theme 'light' for dark-screened backgrounds"))
@click.option("-o", "--output", type=click.File('w'),
              help=("Save tree output to file"))
@click.option("-v", "--verbose", default=0, count=True,
              help="Include methods for each endpoint")
def tree(ramlfile, color, output, verbose):
    """Pretty-print a tree of the RAML-defined API."""
    try:
        load_obj = RAMLLoader(ramlfile)
        validate_raml(ramlfile, prod=True)
        ttree(load_obj, color, output, verbose)
    # Same exception conecrns as in the validate function.
    # LR: the @click.argument checks to see if the RAML file exists
    except InvalidRamlFileError as e:
        msg = '"{0}" is not a valid RAML file: {1}'.format(
            click.format_filename(load_obj.raml_file), e)
        click.secho(msg, fg="red", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
