#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from tree import tree as ttree
from validate import ValidateRAML, RAMLValidationError

import click


# TODO: Implement these commands! :D

@click.group()
def main():
    """The main routine."""


@main.command(help="Validate a RAML file.")
@click.argument('ramlfile', type=click.Path(exists=True))
def validate(ramlfile):
    click.echo("- Validating file: {0}".format(ramlfile))

    try:
        ValidateRAML(ramlfile).validate()
        click.echo("✔︎ Validated file: {0}".format(ramlfile))
    except RAMLValidationError as e:
        click.echo("✗ Error validating file {0}: {1}".format(ramlfile, e))


@main.command(help="Visualize the RAML with a tree.")
@click.argument('ramlfile', type=click.Path(exists=True))
@click.option("--light/--dark", default=True,
              help=("""Color theme of text printout.\n
                       Use '--light' for dark-screen backgrounds (DEFAULT),\n
                       and '--dark' for light-screen backgrounds.\n"""))
@click.option("-v", default=False, is_flag=True,
              help="Include methods for each endpoint")
@click.option("-vv", default=False, is_flag=True,
              help="Include parameters for each endpoint")
@click.option("-vvv", default=False, is_flag=True,
              help="Include display name for each parameter for each endpoint")
def tree(light, v, vv, vvv, ramlfile):
    if v:
        verbosity = 1
    elif vv:
        verbosity = 2
    elif vvv:
        verbosity = 3
    else:
        verbosity = 0
    ttree(ramlfile, light, verbosity)


if __name__ == "__main__":
    main()
