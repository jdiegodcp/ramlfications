#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function

import click

from .tree import tree as ttree
from .errors import InvalidRAMLError
from .utils import update_mime_types as umt
from .utils import load_file

from ramlfications import validate as vvalidate


@click.group()
def main():
    """Yet Another RAML Parser"""
    # Needed to collect the validate & tree commands


@main.command(help="Validate a RAML file.")
@click.argument("ramlfile", type=click.Path(exists=True))
@click.option("--config", "-c", type=click.Path(exists=True),
              help="Additionally supported items beyond RAML spec.")
def validate(ramlfile, config):
    """Validate a given RAML file."""
    try:
        vvalidate(ramlfile, config)
        click.secho("Success! Valid RAML file: {0}".format(ramlfile),
                    fg="green")

    except InvalidRAMLError as e:
        msg = "Error validating file {0}: \n{1}".format(ramlfile, e)
        click.secho(msg, fg="red", err=True)
        raise SystemExit(1)


@main.command(help="Visualize the RAML file as a tree.")
@click.argument('ramlfile', type=click.Path(exists=True))
@click.option("-C", "--color", type=click.Choice(['dark', 'light']),
              default=None,
              help=("Color theme 'light' for dark-screened backgrounds"))
@click.option("-o", "--output", type=click.File('w'),
              help=("Save tree output to file"))
@click.option("-v", "--verbose", default=0, count=True,
              help="Include methods for each endpoint")
@click.option("-V", "--validate", default=False, is_flag=True,
              help="Validate RAML file")
@click.option("-c", "--config", type=click.Path(exists=True),
              help="Additionally supported items beyond RAML spec.")
def tree(ramlfile, color, output, verbose, validate, config):
    """Pretty-print a tree of the RAML-defined API."""
    try:
        load_obj = load_file(ramlfile)
        ttree(load_obj, color, output, verbose, validate, config)
    except InvalidRAMLError as e:
        msg = '"{0}" is not a valid RAML file: {1}'.format(
            click.format_filename(ramlfile), e)
        click.secho(msg, fg="red", err=True)
        raise SystemExit(1)


@main.command(help="Update RAMLfications' supported MIME types from IANA.")
def update():
    umt()


if __name__ == "__main__":
    main()
