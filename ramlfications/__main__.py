#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB


import click


# TODO: Implement these commands! :D

@click.group()
def main():
    """The main routine."""


@main.command()
@click.argument('ramlfile', type=click.Path(exists=True))
def parse(ramlfile):
    click.echo("Parsing file: {0}".format(ramlfile))
    print 'parse: {0}'.format(ramlfile)
    click.echo("Parsed file: {0}".format(ramlfile))


@main.command()
@click.argument('ramlfile', type=click.Path(exists=True))
def validate(ramlfile):
    click.echo("Validating file: {0}".format(ramlfile))
    print 'validate: {0}'.format(ramlfile)
    click.echo("Validated file: {0}".format(ramlfile))


@main.command()
@click.argument('ramlfile', type=click.Path(exists=True))
def tree(ramlfile):
    click.echo("Producing a node tree based off of {0}".format(ramlfile))
    print 'tree: {0}'.format(ramlfile)
    click.echo("Produced tree.")


if __name__ == "__main__":
    main()
