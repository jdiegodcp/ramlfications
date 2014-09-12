#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB


class ContentType(object):
    def __init__(self, name, schema, example):
        self.name = name
        self.schema = schema
        self.example = example


class JSONFormParameter(object):
    def __init__(self, param, data, example):
        self.param = param
        self.data = data
        self.example = example

    @property
    def name(self):
        return self.param

    @property
    def display_name(self):
        return self.param

    @property
    def type(self):
        return self.data.get('type')

    @property
    def description(self):
        return self.data.get('description')

    @property
    def items(self):
        if self.type == 'array':
            return [item for item in self.data.get('items').get('properties').items()]
        return None

    @property
    def enum(self):
        return None

    @property
    def required(self):
        return self.data.get('required')


class URIParameter(object):
    def __init__(self, param, data):
        self.param = param
        self.data = data
        # Pretty sure it will always be true - need this set for form creation
        self.required = True

    @property
    def name(self):
        """Name of URI Parameter"""
        return self.param

    @property
    def display_name(self):
        """Display Name of URI Parameter"""
        return self.data.get('displayName')

    @property
    def type(self):
        """Type of URI Parameter"""
        return self.data.get('type')

    @property
    def description(self):
        """Description of URI Parameter"""
        return self.data.get('description')

    @property
    def example(self):
        """Example of URI Parameter"""
        return self.data.get('example', '')

    @property
    def enum(self):
        return self.data.get('enum')


class QueryParameter(object):
    def __init__(self, param, data):
        self.param = param
        self.data = data

    @property
    def name(self):
        return self.param

    @property
    def display_name(self):
        return self.data.get('displayName')

    @property
    def type(self):
        # TODO: check to see if one of valid RAML types
        return self.data.get('type')

    @property
    def example(self):
        return self.data.get('example', '')

    @property
    def default(self):
        return self.data.get('default')

    @property
    def description(self):
        return self.data.get('description')

    @property
    def required(self):
        return self.data.get('required')

    @property
    def enum(self):
        # NOTE: gives choices
        return self.data.get('enum')

    @property
    def pattern(self):
        # TODO: what does pattern give me?
        return self.data.get('pattern')

    @property
    def min_length(self):
        # TODO: set for only "string" types
        return self.data.get('minLength')

    @property
    def max_length(self):
        # TODO: set for only "string" types
        return self.data.get('maxLength')

    @property
    def minimum(self):
        # TODO: set for only integer/number types
        return self.data.get('minimum')

    @property
    def maximum(self):
        # TODO: set for only integer/number types
        return self.data.get('maximum')

    @property
    def repeat(self):
        return self.data.get('repeat')


class FormParameter(object):
    def __init__(self, param, data):
        self.param = param
        self.data = data

    @property
    def name(self):
        return self.param

    @property
    def display_name(self):
        return self.data.get('displayName')

    @property
    def type(self):
        # TODO: check to see if one of valid RAML types
        return self.data.get('type')

    @property
    def example(self):
        return self.data.get('example', '')

    @property
    def default(self):
        return self.data.get('default')

    @property
    def description(self):
        return self.data.get('description')

    @property
    def required(self):
        return self.data.get('required')

    @property
    def enum(self):
        # NOTE: gives "choices" for select field
        return self.data.get('enum')

    @property
    def pattern(self):
        # TODO: what does pattern give me?
        return self.data.get('pattern')

    @property
    def min_length(self):
        # TODO: set for only "string" types
        return self.data.get('minLength')

    @property
    def max_length(self):
        # TODO: set for only "string" types
        return self.data.get('maxLength')

    @property
    def minimum(self):
        # TODO: set for only integer/number types
        return self.data.get('minimum')

    @property
    def maximum(self):
        # TODO: set for only integer/number types
        return self.data.get('maximum')

    @property
    def repeat(self):
        return self.data.get('repeat')
