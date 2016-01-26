# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function

from six import iteritems, itervalues, iterkeys, string_types

from ramlfications.config import MEDIA_TYPES
from ramlfications.parameters import Response, Header, Body, URIParameter
from ramlfications.utils import load_schema
from ramlfications.utils.common import _get, substitute_parameters
from ramlfications.utils.parameter import map_object, resolve_scalar_data


#####
# Public functions
#####
def create_param_objs(param_type, resolve=[], **kwargs):
    """
    General function to create :py:module:`.parameters` objects. Returns
    a list of ``.parameters`` objects or ``None``.

    :param str param_type: string name of object
    :param list resolve: list of what to inherit from, e.g. "traits", "parent"
    :param dict kwargs: relevant data to parse
    """
    method = _get(kwargs, "method", None)

    # collect all relevant data
    if not resolve:
        resolve = ["method", "resource"]  # default

    resolved = resolve_scalar_data(param_type, resolve, **kwargs)
    resolved = _substitute_params(resolved, **kwargs)

    # create parameter objects based off of the resolved data
    object_name = map_object(param_type)
    if param_type == "body":
        return create_bodies(resolved, kwargs)
    if param_type == "responses":
        return create_responses(resolved, kwargs)
    conf = _get(kwargs, "conf", None)
    errs = _get(kwargs, "errs", None)
    params = __create_base_param_obj(resolved, object_name, conf, errs,
                                     method=method)

    # TODO: if param type is URI/Base Uri, then preserve order according
    # to how they are represented in absolute_uri, as well as create any
    # undeclared uri params that are in the path
    return params or None


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
    headers = __create_response_headers(data, method, root)
    body = __create_response_body(data, root, method)
    desc = _get(data, "description", None)

    # when substituting `<<parameters>>`, everything gets turned into
    # a string/unicode. Try to make it an int, and if not, validate.py
    # will certainly catch it.
    if isinstance(code, string_types):
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


def _substitute_params(resolved, **kwargs):
    """
    Returns dict of param data with relevant ``<<parameter>>`` substituted.
    """
    # this logic ain't too pretty...
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
                    resolved = substitute_parameters(resolved, param_data)

    type_ = _get(kwargs, "type_", None)
    if type_:
        if isinstance(type_, dict):
            param_type = type_
            param_data = list(itervalues(param_type))[0]
            param_data["resourcePath"] = _path
            param_data["resourcePathName"] = _path_name
            resolved = substitute_parameters(resolved, param_data)
    return resolved


############################
#
# Private, helper functions
#
############################
def __create_response_headers(data, method, root):
    """
    Create :py:class:`.parameters.Header` objects for a
    :py:class:`.parameters.Response` object.
    """
    headers = _get(data, "headers", default={})

    header_objects = __create_base_param_obj(headers, Header, root.config,
                                             root.errors, method=method)
    return header_objects or None


def __create_response_body(data, root, method):
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
