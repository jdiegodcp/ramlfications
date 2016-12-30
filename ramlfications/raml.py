# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function

import attr
from six import iteritems, itervalues
from six.moves import BaseHTTPServer as httpserver  # NOQA

from . import _parameter_tags
from .parameters import Content
from .validate import *  # NOQA

HTTP_RESP_CODES = httpserver.BaseHTTPRequestHandler.responses.keys()
AVAILABLE_METHODS = [
    "get", "post", "put", "delete", "patch", "head", "options",
    "trace", "connect"
]

METHOD_PROPERTIES = [
    "headers", "body", "responses", "query_params", "form_params"
]

RESOURCE_PROPERTIES = METHOD_PROPERTIES + ["base_uri_params", "uri_params"]

@attr.s
class RootNode(object):
    """
    API Root Node

    :param dict raw: dict of loaded RAML data
    :param str version: API version
    :param str base_uri: API's base URI
    :param list base_uri_params: parameters for base URI, or ``None``. \
        The order of ``base_uri_params`` will follow the order \
        defined in the :py:obj:`.RootNode.base_uri`.
    :param list uri_params: URI parameters that can apply to all resources, \
        or ``None``. The order of ``uri_params`` will follow the order \
        defined in the :py:obj:`.RootNode.base_uri`.
    :param list protocols: API-supported protocols, defaults to protocol \
        in ``base_uri``
    :param str title: API Title
    :param list docs: list of :py:class:`parameters.Documentation` objects, \
        or ``None``
    :param list schemas: list of dictionaries, or ``None``
    :param str media_type: default accepted request/response media type, \
        or ``None``
    :param list resource_types: list of :py:class:`ResourceTypeNode`, \
        or ``None``
    :param list traits: list of :py:class:`TraitNode`, or ``None``
    :param list security_schemes: list of \
        :py:class:`parameters.SecurityScheme` objects, or ``None``
    :param list resources: list of :py:class:`ResourceNode` objects, \
        or ``None``
    :param raml_obj: loaded :py:class:`raml.RAMLDict` object
    """
    raw              = attr.ib(repr=False)
    version          = attr.ib(repr=False, validator=root_version)
    base_uri         = attr.ib(repr=False, validator=root_base_uri)
    base_uri_params  = attr.ib(repr=False,
                               validator=root_base_uri_params)
    uri_params       = attr.ib(repr=False, validator=root_uri_params)
    protocols        = attr.ib(repr=False, validator=root_protocols)
    title            = attr.ib(validator=root_title)
    documentation    = attr.ib(repr=False, validator=root_docs)
    schemas          = attr.ib(repr=False, validator=root_schemas)
    media_type       = attr.ib(repr=False, validator=root_media_type)
    secured_by       = attr.ib(repr=False, validator=root_secured_by)
    resource_types   = attr.ib(repr=False, init=False)
    traits           = attr.ib(repr=False, init=False)
    security_schemes = attr.ib(repr=False, init=False)
    resources        = attr.ib(repr=False, init=False,
                               validator=root_resources)
    raml_obj         = attr.ib(repr=False)
    config           = attr.ib(repr=False,
                               validator=attr.validators.instance_of(dict))
    errors           = attr.ib(repr=False)


@attr.s
class BaseNode(object):
    """
    :param dict raw: The raw data parsed from the RAML file
    :param RootNode root: Back reference to the node's API root
    :param list headers: List of node's :py:class:`parameters.Header` \
        objects, or ``None``
    :param list body: List of node's :py:class:`parameters.Body` objects, \
        or ``None``
    :param list responses: List of node's :py:class:`parameters.Response`\
        objects, or ``None``
    :param list uri_params: List of node's :py:class:`parameters.URIParameter`\
        objects, or ``None``. The order of ``uri_params`` will follow the \
        order defined in the \
        :py:obj:`.ResourceNode.absolute_uri`.
    :param list base_uri_params: List of node's base \
        :py:obj:`parameters.URIParameter` objects, or ``None``. The order of \
        ``base_uri_params`` will follow the order defined in the \
        :py:attribute:`.ResourceNode.absolute_uri`.
    :param list query_params: List of node's \
        :py:obj:`parameters.QueryParameter` objects, or ``None``
    :param list form_params: List of node's \
        :py:class:`parameters.FormParameter` objects, or ``None``
    :param str media_type: Supported request MIME media type. Defaults to \
        :py:class:`RootNode`'s ``media_type``.
    :param str description: Description of node.
    :param list protocols: List of ``str`` 's of supported protocols. \
        Defaults to :py:class:`RootNode`'s ``protocols``.
    """
    root            = attr.ib(repr=False)
    headers         = attr.ib(repr=False)
    body            = attr.ib(repr=False)
    responses       = attr.ib(repr=False)
    uri_params      = attr.ib(repr=False)
    base_uri_params = attr.ib(repr=False)
    query_params    = attr.ib(repr=False)
    form_params     = attr.ib(repr=False)
    media_type      = attr.ib(repr=False)
    desc            = attr.ib(repr=False)
    protocols       = attr.ib(repr=False)
    errors          = attr.ib(repr=False)

    @property
    def description(self):
        return Content(self.desc)


@attr.s
class TraitNode(BaseNode):
    """
    RAML Trait object

    :param str name: Name of trait
    :param str usage: Usage of trait
    """
    name  = attr.ib()
    raw   = attr.ib(repr=False, validator=defined_trait)
    usage = attr.ib(repr=False)


@attr.s
class ResourceTypeNode(BaseNode):
    """
    RAML Resource Type object

    :param str name: Name of resource type
    :param str type: Name of inherited :py:class:`ResourceTypeNode` object,
        or ``None``.
    :param str method: Supported method. If ends in ``?``, parameters will \
        only be applied to assigned resource if resource implements this \
        method. Else, resource must implement the method.
    :param str usage: Usage of resource type, or ``None``
    :param bool optional: Inherited if resource defines method.
    :param list is\_: List of assigned trait names, or ``None``
    :param list traits: List of assigned :py:class:`TraitNode` objects, \
        or ``None``
    :param str secured_by: List of ``str`` s or ``dict`` s of assigned \
        security scheme, or ``None``. If a ``str``, the name of the security \
        scheme.  If a ``dict``, the key is the name of the scheme, the values \
        are the parameters assigned (e.g. relevant OAuth 2 scopes).
    :param list security_schemes: A list of assigned \
        :py:class:`parameters.SecurityScheme` objects, or ``None``.
    :param str display_name: User-friendly name of resource; \
        defaults to ``name``

    """
    name             = attr.ib()
    raw              = attr.ib(repr=False, validator=defined_resource_type)
    type             = attr.ib(repr=False, validator=assigned_res_type)
    method           = attr.ib(repr=False)
    usage            = attr.ib(repr=False)
    optional         = attr.ib(repr=False)
    is_              = attr.ib(repr=False, validator=assigned_traits)
    traits           = attr.ib(repr=False)
    secured_by       = attr.ib(repr=False)
    security_schemes = attr.ib(repr=False)
    display_name     = attr.ib(repr=False)


@attr.s
class ResourceNode(BaseNode):
    """
    Supported API-endpoint (“resource”)

    :param str name: Resource name
    :param ResourceNode parent: parent node object if any, or ``None``
    :param str method: HTTP method for resource, or ``None``
    :param str display_name: User-friendly name of resource; \
        defaults to ``name``
    :param str path: relative path of resource
    :param str absolute_uri: Absolute URI of resource: \
        :py:class:`RootNode`'s ``base_uri`` + ``path``
    :param list is\_: A list of ``str`` s or ``dict`` s of resource-assigned \
        traits, or ``None``
    :param list traits: A list of assigned :py:class:`TraitNode` objects, \
        or ``None``
    :param str type: The name of the assigned resource type, or ``None``
    :param ResourceTypeNode resource_type: The assigned \
        :py:class:`ResourceTypeNode` object
    :param list secured_by: A list of ``str`` s or ``dict`` s of resource-\
        assigned security schemes, or ``None``. If a ``str``, the name of the \
        security scheme.  If a ``dict``, the key is the name of the scheme, \
        the values are the parameters assigned (e.g. relevant OAuth 2 scopes).
    :param list security_schemes: A list of assigned \
        :py:class:`parameters.SecurityScheme` objects, or ``None``.
    """
    name             = attr.ib(repr=False)
    raw              = attr.ib(repr=False)
    parent           = attr.ib(repr=False)
    method           = attr.ib()
    display_name     = attr.ib(repr=False)
    path             = attr.ib()
    absolute_uri     = attr.ib(repr=False)
    is_              = attr.ib(repr=False, validator=assigned_traits)
    traits           = attr.ib(repr=False)
    type             = attr.ib(repr=False, validator=assigned_res_type)
    resource_type    = attr.ib(repr=False)
    secured_by       = attr.ib(repr=False)
    security_schemes = attr.ib(repr=False)

    def _inherit_type(self):
        for p in METHOD_PROPERTIES:
            try:
                inherited_prop = getattr(self.resource_type, p)
                resource_prop = getattr(self, p)
            except AttributeError:
                # this won't be valid when validating
                return
            if resource_prop and inherited_prop:
                for r in resource_prop:
                    r._inherit_type_properties(inherited_prop)

    def _parse_trait_parameters(self):
        to_parse = []
        for t in self.is_:
            if isinstance(t, dict):
                for trait, param in list(iteritems(t)):
                    # get trait object
                    trait_obj = [t for t in self.traits if t.name == trait][0]
                    # get parameter name & value
                    for k, v in list(iteritems(param)):
                        to_parse.append(dict(name=k, value=v, obj=trait_obj))
                    to_parse.append(dict(name="methodName",
                                         value=self.method,
                                         obj=trait_obj))
                    to_parse.append(dict(name="resourcePath",
                                         value=self.name,
                                         obj=trait_obj))
                    to_parse.append(dict(name="resourcePathName",
                                         value = self.name[1:],
                                         obj=trait_obj))
        self._update_parameters(to_parse, RESOURCE_PROPERTIES)

    def _parse_resource_type_parameters(self):
        to_parse = []
        if not self.resource_type:
            return
        if isinstance(self.type, dict):
            for key, value in list(iteritems(self.type)):
                # note: not sure what else 'value' could be...
                # but just being safe...
                if isinstance(value, dict):
                    for param, v in list(iteritems(value)):
                        to_parse.append(dict(name=param, value=v, obj=self.resource_type))

        to_parse.append(dict(name="resourcePath",
                             value=self.name,
                             obj=self.resource_type))
        to_parse.append(dict(name="resourcePathName",
                             value = self.name[1:],
                             obj=self.resource_type))
        self._update_parameters(to_parse, RESOURCE_PROPERTIES)

    def __replace_str_attr(self, param, new_value, current_str):
        pattern = r'(<<\s*)(?P<pname>{0}\b[^\s|]*)(\s*\|?\s*(?P<tag>!\S*))?(\s*>>)'
        p = re.compile(pattern.format(param))
        ret = re.findall(p, current_str)
        if not ret:
            return current_str
        for item in ret:
            to_replace = "".join(item[0:3]) + item[-1]
            tag_func = item[3]
            if tag_func:
                tag_func = tag_func.strip("!")
                tag_func = tag_func.strip()
                func = getattr(_parameter_tags, tag_func)
                if func:
                    new_value = func(new_value)
            current_str = current_str.replace(to_replace, str(new_value), 1)

        return current_str

    def _update_parameters(self, to_parse, properties):
        for item in to_parse:
            obj = item.get("obj")
            name = item.get("name")
            value = item.get("value")

            for p in properties:
                props = getattr(obj, p)
                if props:
                    for i in props:
                        i._substitute_parameters(i, name, value)
            desc = getattr(obj, "desc")
            if desc:
                if "resourcePath" in desc or "resourcePathName" in desc:
                    self.desc = self.__replace_str_attr(name, value, desc)
