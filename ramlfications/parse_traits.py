# ! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function

from six import iteritems

from .parameters import (
    QueryParameter, URIParameter, FormParameter, Header, Body, Response
)
from .raml import Trait
from .validate import validate_property


#####
# TRAITS
#####

# Logic for parsing of traits into Trait objects
def _parse_traits(raml, root):
    raw_traits = raml.get('traits')
    if raw_traits:
        traits = [Trait(list(t.keys())[0], list(t.values())[0],
                        root) for t in raw_traits]
        return __add_properties_to_traits(traits)
    return None


def __add_properties_to_traits(traits):
    for t in traits:
        t.usage = __set_usage(t)
        t.query_params = __set_trait_properties(t, 'queryParameters')
        t.uri_params = __set_trait_properties(t, 'uriParameters')
        t.form_params = __set_trait_properties(t, 'formParameters')
        t.headers = __set_trait_properties(t, 'headers')
        t.body = __set_trait_properties(t, 'body')
        t.responses = __set_trait_properties(t, 'responses')
        t.description = __set_simple_property(t, 'description')
        t.media_types = __set_simple_property(t, 'body')
    return traits


def __set_usage(resource):
    return resource.data.get('usage')


def __set_simple_property(r, property):
    return r.data.get(property)


@validate_property
def __set_trait_properties(r, property, inherit=False):
    properties = []

    resource = r.data.get(property, {})
    for k, v in iteritems(resource):
        obj = __map_obj(property)
        properties.append(obj(k, v, r))

    if inherit:
        item = __map_item_type(property)
        if hasattr(r.parent, item):
            if getattr(r.parent, item) is not None:
                properties.extend(getattr(r.parent, item))

    return properties or None


#####
# Util functions
#####

def __map_obj(property):
    return {
        'headers': Header,
        'body': Body,
        'responses': Response,
        'queryParameters': QueryParameter,
        'uriParameters': URIParameter,
        'formParameters': FormParameter,
        'baseUriParameters': URIParameter,
    }[property]


def __map_item_type(item):
    return {
        'headers': 'headers',
        'body': 'body',
        'responses': 'responses',
        'queryParameters': 'query_params',
        'uriParameters': 'uri_params',
        'formParameters': 'form_params',
        'baseUriParameters': 'base_uri_params',
    }[item]
