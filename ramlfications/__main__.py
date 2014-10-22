#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from parser import APIRoot
from validate import ValidateRAML, RAMLValidationError

import click


# TODO: Implement these commands! :D

@click.group()
def main():
    """The main routine."""


@main.command(help="Parse a RAML file")
@click.argument('ramlfile', type=click.Path(exists=True))
def parse(ramlfile):
    click.echo("- Parsing file: {0}".format(ramlfile))
    api = APIRoot(ramlfile)
    print '✔︎ Loaded: {0}'.format(api.title)
    nodes = api.nodes
    print "✔︎ Parsed {0} nodes.".format(len(nodes.values()))
    click.echo("✔︎ Parsed file: {0}".format(ramlfile))


@main.command(help="Validate a RAML file.")
@click.argument('ramlfile', type=click.Path(exists=True))
def validate(ramlfile):
    click.echo("- Validating file: {0}".format(ramlfile))

    try:
        ValidateRAML(ramlfile).validate()
        click.echo("✔︎ Validated file: {0}".format(ramlfile))
    except RAMLValidationError as e:
        click.echo("✗ Error validating file {0}: {1}".format(ramlfile, e))

@main.command()
@click.argument('ramlfile', type=click.Path(exists=True))
def tree(ramlfile):
    click.echo("Producing a node tree based off of {0}".format(ramlfile))
    print 'tree: {0}'.format(ramlfile)
    click.echo("Produced tree.")


if __name__ == "__main__":
    main()
