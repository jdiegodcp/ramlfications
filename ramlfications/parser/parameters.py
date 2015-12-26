# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function

import re

from six import iteritems, itervalues, iterkeys

from ramlfications.config import MEDIA_TYPES
from ramlfications.parameters import (
    Response, Header, Body, URIParameter, SecurityScheme
)
from ramlfications.utils import load_schema
from ramlfications.utils.common import _get, _substitute_parameters
from ramlfications.utils.parameter import _map_object, resolve_scalar_data


#####
# Public functions
#####
def create_param_objs(param_type, resolve=[], **kwargs):
    """
    General function to create :py:module:`.parameters` objects. Returns
    a list of ``.parameters`` objects or ``None``.

    :param dict data: data to create object
    :param str method: method associated with object, if necessary
    :param root: RootNode of the API
    :param str param_type: string name of object
    :param types: a list of ``.raml.ResourceTypeNode`` to inherit \
        from, if any.
    :param str uri: URI of the node, to preserve order of URI params
    :param base: base UriParameter objects to preserve order of URI \
        parameters and to create any that are not explicitly declared
    :param root: RootNode object to preserve order of URI parameters and \
        to create any that are not explicitly declared
    :param raml: raw RAML data to preserve order of URI parameters and \
        to create any that are not explicitly declared
    """
    data = _get(kwargs, "data", None)
    method = _get(kwargs, "method", None)

    # collect all relevant data
    if not resolve:
        resolve = ["method", "resource"]  # default

    resolved = resolve_scalar_data(param_type, resolve, **kwargs)
    resolved = create_resource_objects(resolved, **kwargs)

    # create parameter objects based off of the resolved data
    conf = _get(kwargs, "conf", None)
    errs = _get(kwargs, "errs", None)
    object_name = _map_object(param_type)
    if param_type == "body":
        return create_bodies(resolved, kwargs)
    if param_type == "responses":
        return create_responses(resolved, kwargs)
    params = __create_base_param_obj(resolved, object_name, conf, errs,
                                     method=method)

    uri = _get(kwargs, "uri", None)

    # if it's not a uri-type parameter, return, otherwise create uri-specific
    # parameter objects
    if not uri:
        return params or None
    base = _get(kwargs, "base", None)
    root = _get(kwargs, "root", None)
    return _create_uri_params(uri, params, param_type, conf, errs, base=base,
                              root=root, raml=data)


def create_body(mime_type, data, root, method):
    """
    Create a :py:class:`.parameters.Body` object.
    """
    raw = {mime_type: data}
    kwargs = dict(
        data=data,
        method=method,
        root=root,
        errs=root.errors,
        conf=root.config
    )
    form_params = create_param_objs("formParameters", **kwargs)
    return Body(
        mime_type=mime_type,
        raw=raw,
        schema=load_schema(_get(data, "schema")),
        example=load_schema(_get(data, "example")),
        # TODO: should create form param objects?
        form_params=form_params,
        config=root.config,
        errors=root.errors
    )


def create_bodies(resolve, kwargs):
    """
    Returns a list of :py:class:`.parameters.Body` objects.
    """
    # bodies = resolve_scalar_data("body", resolve, **kwargs)
    root = _get(kwargs, "root")
    method = _get(kwargs, "method")
    body_objects = []
    for k, v in list(iteritems(resolve)):
        if v is None:
            continue
        body = create_body(k, v, root, method)
        body_objects.append(body)
    return body_objects or None


def create_response(code, data, root, method):
    """Returns a :py:class:`.parameters.Response` object"""
    headers = _create_response_headers(data, method, root)
    body = _create_response_body(data, root, method)
    desc = _get(data, "description", None)

    # when substituting `<<parameters>>`, everything gets turned into
    # a string/unicode. Try to make it an int, and if not, validate.py
    # will certainly catch it.
    if isinstance(code, basestring):
        try:
            code = int(code)
        except ValueError:
            pass

    return Response(
        code=code,
        raw={code: data},
        method=method,
        desc=desc,
        headers=headers,
        body=body,
        config=root.config,
        errors=root.errors
    )


def create_responses(resolve, kwargs):
    """
    Returns a list of :py:class:`.parameters.Response` objects.
    """
    root = _get(kwargs, "root")
    method = _get(kwargs, "method")
    response_objects = []

    for key, value in list(iteritems(resolve)):
        response = create_response(key, value, root, method)
        response_objects.append(response)
    return sorted(response_objects, key=lambda x: x.code) or None


def create_resource_objects(resolved, **kwargs):
    """
    Returns a list of :py:class:`.parameter` objects as designated by
    ``param`` from the given ``data``. Will parse data the object
    inherits if assigned another resource type and/or trait(s).

    :param str param: RAML-specified paramter, e.g. "resources", \
        "queryParameters"
    :param dict data: method-level ``param`` data
    :param dict v: resource-type-level ``param`` data
    :param str method: designated method
    :param root: ``.raml.RootNode`` object
    :param list is_: list of assigned traits, either ``str`` or
        ``dict`` mapping key: value pairs to ``<<parameter>>`` values
    """
    _path = _get(kwargs, "resource_path")
    if _path:
        _path_name = _path.lstrip("/")
    else:
        _path = "<<resourcePath>>"
        _path_name = "<<resourcePathName>>"
    is_ = _get(kwargs, "is_", None)
    if is_:
        if not isinstance(is_, list):
            # I think validate.py would error out so
            # I don't think anything is needed here...
            pass
        else:
            for i in is_:
                if isinstance(i, dict):
                    param_type = list(iterkeys(i))[0]
                    param_data = list(itervalues(i))[0]
                    param_data["resourcePath"] = _path
                    param_data["resourcePathName"] = _path_name
                    resolved = _substitute_parameters(resolved, param_data)

    type_ = _get(kwargs, "type_", None)
    if type_:
        if isinstance(type_, dict):
            param_type = type_
            param_data = list(itervalues(param_type))[0]
            param_data["resourcePath"] = _path
            param_data["resourcePathName"] = _path_name
            resolved = _substitute_parameters(resolved, param_data)
    return resolved


############################
#
# Private, helper functions
#
############################
# TODO: clean me! i'm ugly!
def _create_uri_params(uri, params, param_type, conf, errs, base=None,
                       root=None, raml=None):
    declared = []
    param_names = []
    to_ignore = []
    if params:
        param_names = [p.name for p in params]
        declared.extend(params)
    if base:
        base_params = [p for p in base if p.name not in param_names]
        base_param_names = [p.name for p in base_params]
        param_names.extend(base_param_names)

        if param_type == "uriParameters":
            to_ignore.extend(base_param_names)
    if raml:
        if param_type == "uriParameters":
            _to_ignore = list(iterkeys(_get(raml, "baseUriParameters", {})))
            to_ignore.extend(_to_ignore)
        if param_type == "baseUriParameters":
            _to_ignore = list(iterkeys(_get(raml, "uriParameters", {})))
            to_ignore.extend(_to_ignore)
    if root:
        if root.uri_params:
            _params = root.uri_params
            root_uri = [p for p in _params if p.name not in param_names]
            declared.extend(root_uri)
            root_uri_names = [p.name for p in root_uri]
            param_names.extend(root_uri_names)
            if param_type == "baseUriParameters":
                to_ignore.extend(root_uri_names)
        if root.base_uri_params:
            _params = root.base_uri_params
            root_base_uri = [p for p in _params if p.name not in param_names]
            root_base_uri_names = [p.name for p in root_base_uri]
            param_names.extend(root_base_uri_names)
            if param_type == "uriParameters":
                to_ignore.extend(root_base_uri_names)
    return __preserve_uri_order(uri, params, conf, errs, declared, to_ignore)


def _create_response_headers(data, method, root):
    """
    Create :py:class:`.parameters.Header` objects for a
    :py:class:`.parameters.Response` object.
    """
    headers = _get(data, "headers", default={})

    header_objects = __create_base_param_obj(headers, Header, root.config,
                                             root.errors, method=method)
    return header_objects or None


def _create_response_body(data, root, method):
    """
    Create :py:class:`.parameters.Body` objects for a
    :py:class:`.parameters.Response` object.
    """
    body = _get(data, "body", default={})
    body_list = []
    no_mime_body_data = {}
    for key, spec in list(iteritems(body)):
        if key not in MEDIA_TYPES:
            # if a root mediaType was defined, the response body
            # may omit the mime_type definition
            if key in ('schema', 'example'):
                no_mime_body_data[key] = load_schema(spec) if spec else {}
        else:
            # spec might be '!!null'
            raw = spec or body
            _body = create_body(key, raw, root, method)
            body_list.append(_body)
    if no_mime_body_data:
        _body = create_body(root.media_type, no_mime_body_data, root, method)
        body_list.append(_body)

    return body_list or None


def __create_base_param_obj(attribute_data, param_obj, config, errors, **kw):
    """
    Helper function to create a child of a
    :py:class:`.parameters.BaseParameter` object
    """
    objects = []

    for key, value in list(iteritems(attribute_data)):
        if param_obj is URIParameter:
            required = _get(value, "required", default=True)
        else:
            required = _get(value, "required", default=False)
        kwargs = dict(
            name=key,
            raw={key: value},
            desc=_get(value, "description"),
            display_name=_get(value, "displayName", key),
            min_length=_get(value, "minLength"),
            max_length=_get(value, "maxLength"),
            minimum=_get(value, "minimum"),
            maximum=_get(value, "maximum"),
            default=_get(value, "default"),
            enum=_get(value, "enum"),
            example=_get(value, "example"),
            required=required,
            repeat=_get(value, "repeat", False),
            pattern=_get(value, "pattern"),
            type=_get(value, "type", "string"),
            config=config,
            errors=errors
        )
        if param_obj is Header:
            kwargs["method"] = _get(kw, "method")

        item = param_obj(**kwargs)
        objects.append(item)

    return objects or None


def __add_missing_uri_params(missing, param_objs, config, errors, to_ignore):
    for m in missing:
        # no need to create a URI param for version
        # or should we?
        if m in to_ignore:
            continue
        if m == "version":
            continue
        data = {m: {"type", "string"}}
        _param = __create_base_param_obj(data, URIParameter, config, errors)
        param_objs.append(_param[0])
    return param_objs


# preserve order of URI and Base URI parameters
# used for RootNode, ResourceNode
def __preserve_uri_order(path, param_objs, config, errors, declared=[],
                         to_ignore=[]):
    # if this is hit, RAML shouldn't be valid anyways.
    if isinstance(path, list):
        path = path[0]

    pattern = "\{(.*?)\}"
    params = re.findall(pattern, path)
    if not param_objs:
        param_objs = []
    # if there are URI parameters in the path but were not declared
    # inline, we should create them.
    # TODO: Probably shouldn't do it in this function, though...
    if len(params) > len(param_objs):
        if len(param_objs) > 0:
            param_names = [p.name for p in param_objs]
            missing = [p for p in params if p not in param_names]
        else:
            missing = params[::]
        # exclude any (base)uri params if already declared
        missing = [p for p in missing if p not in declared]
        param_objs = __add_missing_uri_params(missing, param_objs,
                                              config, errors, to_ignore)

    sorted_params = []
    for p in params:
        _param = [i for i in param_objs if i.name == p]
        if _param:
            sorted_params.append(_param[0])
    return sorted_params or None
