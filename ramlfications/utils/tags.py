# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB


import re

import inflect

__all__ = [
    "pluralize", "singularize", "uppercase", "lowercase", "lowercamelcase",
    "uppercamelcase", "lowerunderscorecase", "upperunderscorecase",
    "lowerhyphencase", "upperhyphencase",
]

#####
# Tag functions to manipulate <<parameters>> from
# traits & resource types
#
# Add your function here, and add to the __all__ statement above^
#####

p = inflect.engine()


def _is_plural(input_str):
    # ``singular_noun`` alone misreads words such as ``bass`` (as the plural
    # of ``bas``), so a word counts as plural only when its singular form
    # pluralizes back to the same word
    singular = p.singular_noun(input_str)
    return bool(singular) and p.plural(singular) == input_str


def pluralize(input_str):
    if _is_plural(input_str):
        return input_str
    return p.plural(input_str)


def singularize(input_str):
    if _is_plural(input_str):
        return p.singular_noun(input_str)
    return input_str


# words of a compound value: ``_``, ``-`` and whitespace separate words, as
# does a case change (``userId``, ``HTTPServer`` -> ``HTTP``, ``Server``)
WORDS = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z0-9]+|[A-Z]+|[0-9]+")


def _words(input_str):
    return WORDS.findall(input_str)


def uppercase(input_str):
    return input_str.upper()


def lowercase(input_str):
    return input_str.lower()


def lowercamelcase(input_str):
    words = _words(input_str)
    return "".join(
        [w.lower() for w in words[:1]] + [w.capitalize() for w in words[1:]])


def uppercamelcase(input_str):
    return "".join(w.capitalize() for w in _words(input_str))


def lowerunderscorecase(input_str):
    return "_".join(w.lower() for w in _words(input_str))


def upperunderscorecase(input_str):
    return "_".join(w.upper() for w in _words(input_str))


def lowerhyphencase(input_str):
    return "-".join(w.lower() for w in _words(input_str))


def upperhyphencase(input_str):
    return "-".join(w.upper() for w in _words(input_str))


# parameter functions each RAML version defines, in the specs' order;
# only these can be applied with ``<<name | !function>>``
RAML08_FUNCTIONS = {
    "singularize": singularize,
    "pluralize": pluralize,
}
RAML10_FUNCTIONS = dict(RAML08_FUNCTIONS, **{
    "uppercase": uppercase,
    "lowercase": lowercase,
    "lowercamelcase": lowercamelcase,
    "uppercamelcase": uppercamelcase,
    "lowerunderscorecase": lowerunderscorecase,
    "upperunderscorecase": upperunderscorecase,
    "lowerhyphencase": lowerhyphencase,
    "upperhyphencase": upperhyphencase,
})
