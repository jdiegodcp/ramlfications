# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function


import json
import logging
import os
import re
import sys

try:
    from collections import OrderedDict
except ImportError:  # NOCOV
    from ordereddict import OrderedDict

from six import iterkeys, iteritems
import xmltodict

from .parameters import (
    Body, URIParameter, Header, FormParameter, QueryParameter
)

PYVER = sys.version_info[:3]

if PYVER == (2, 7, 9) or PYVER == (3, 4, 3):  # NOCOV
    import six.moves.urllib.request as urllib
    import six.moves.urllib.error as urllib_error
    URLLIB = True
    SECURE_DOWNLOAD = True
else:
    try:  # NOCOV
        import requests
        URLLIB = False
        SECURE_DOWNLOAD = True
    except ImportError:
        import six.moves.urllib.request as urllib
        import six.moves.urllib.error as urllib_error
        URLLIB = True
        SECURE_DOWNLOAD = False

from .errors import MediaTypeError


IANA_URL = "https://www.iana.org/assignments/media-types/media-types.xml"


def load_schema(data):
    """
    Load Schema/Example data depending on its type (JSON, XML).

    If error in parsing as JSON and XML, just returns unloaded data.

    :param str data: schema/example data
    """
    try:
        return json.loads(data)
    except Exception:  # POKEMON!
        pass

    try:
        return xmltodict.parse(data)
    except Exception:  # GOTTA CATCH THEM ALL
        pass

    return data


def setup_logger(key):
    """General logger"""
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    msg = "{key} - %(levelname)s - %(message)s".format(key=key)
    formatter = logging.Formatter(msg)
    console.setFormatter(formatter)

    log.addHandler(console)
    return log


def _requests_download(url):
    """Download a URL using ``requests`` library"""
    try:
        response = requests.get(url)
        return response.text
    except requests.exceptions.RequestException as e:
        msg = "Error downloading from {0}: {1}".format(url, e)
        raise MediaTypeError(msg)


def _urllib_download(url):
    """Download a URL using ``urllib`` library"""
    try:
        response = urllib.urlopen(url)
    except urllib_error.URLError as e:
        msg = "Error downloading from {0}: {1}".format(url, e)
        raise MediaTypeError(msg)
    return response.read()


def download_url(url):
    """
    General download function, given a URL.

    If running 2.7.8 or earlier, or 3.4.2 or earlier, then use
    ``requests`` if it's installed.  Otherwise, use ``urllib``.
    """
    log = setup_logger("DOWNLOAD")
    if SECURE_DOWNLOAD and not URLLIB:
        return _requests_download(url)
    elif SECURE_DOWNLOAD and URLLIB:
        return _urllib_download(url)
    msg = ("Downloading over HTTPS but can not verify the host's "
           "certificate.  To avoid this in the future, `pip install"
           " \"requests[security]\"`.")
    log.warn(msg)
    return _urllib_download(url)


def _xml_to_dict(response_text):
    """Parse XML response from IANA into a Python ``dict``."""
    try:
        return xmltodict.parse(response_text)
    except xmltodict.expat.ExpatError as e:
        msg = "Error parsing XML: {0}".format(e)
        raise MediaTypeError(msg)


def _extract_mime_types(registry):
    """
    Parse out MIME types from a defined registry (e.g. "application",
    "audio", etc).
    """
    mime_types = []
    records = registry.get("record", {})
    reg_name = registry.get("@id")
    for rec in records:
        mime = rec.get("file", {}).get("#text")
        if mime:
            mime_types.append(mime)
        else:
            mime = rec.get("name")
            if mime:
                hacked_mime = reg_name + "/" + mime
                mime_types.append(hacked_mime)
    return mime_types


def _parse_xml_data(xml_data):
    """Parse the given XML data."""
    registries = xml_data.get("registry", {}).get("registry")
    if not registries:
        msg = "No registries found to parse."
        raise MediaTypeError(msg)
    if len(registries) is not 9:
        msg = ("Expected 9 registries but parsed "
               "{0}".format(len(registries)))
        raise MediaTypeError(msg)
    all_mime_types = []
    for registry in registries:
        mime_types = _extract_mime_types(registry)
        all_mime_types.extend(mime_types)

    return all_mime_types


def _save_updated_mime_types(output_file, mime_types):
    """Save the updated MIME Media types within the package."""
    with open(output_file, "w") as f:
        json.dump(mime_types, f)


def update_mime_types():
    """
    Update MIME Media Types from IANA.  Requires internet connection.
    """
    log = setup_logger("UPDATE")

    log.debug("Getting XML data from IANA")
    raw_data = download_url(IANA_URL)
    log.debug("Data received; parsing...")
    xml_data = _xml_to_dict(raw_data)
    mime_types = _parse_xml_data(xml_data)

    current_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(current_dir, "data")
    output_file = os.path.join(data_dir, "supported_mime_types.json")

    _save_updated_mime_types(output_file, mime_types)

    log.debug("Done! Supported IANA MIME media types have been updated.")


def _resource_type_lookup(assigned, root):
    """
    Returns ``ResourceType`` object

    :param str assigned: The string name of the assigned resource type
    :param root: RAML root object
    """
    res_types = root.resource_types
    if res_types:
        res_type_obj = [r for r in res_types if r.name == assigned]
        if res_type_obj:
            return res_type_obj[0]


#####
# Helper methods
#####

# general
def _get(data, item, default=None):
    """
    Helper function to catch empty mappings in RAML. If item is optional
    but not in the data, or data is ``None``, the default value is returned.

    :param data: RAML data
    :param str item: RAML key
    :param default: default value if item is not in dict
    :param bool optional: If RAML item is optional or needs to be defined
    :ret: value for RAML key
    """
    try:
        return data.get(item, default)
    except AttributeError:
        return default


def _create_base_param_obj(attribute_data, param_obj, config, errors, **kw):
    """Helper function to create a BaseParameter object"""
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


# used for traits & resource nodes
def _map_param_unparsed_str_obj(param):
    return {
        "queryParameters": QueryParameter,
        "uriParameters": URIParameter,
        "formParameters": FormParameter,
        "baseUriParameters": URIParameter,
        "headers": Header
    }[param]


# create_resource_types
def _get_union(resource, method, inherited):
    union = {}
    for key, value in list(iteritems(inherited)):
        if resource.get(method) is not None:
            if key not in list(iterkeys(resource.get(method, {}))):
                union[key] = value
            else:
                resource_values = resource.get(method, {}).get(key)
                inherited_values = inherited.get(key, {})
                union[key] = dict(list(iteritems(resource_values)) +
                                  list(iteritems(inherited_values)))
    if resource.get(method) is not None:
        for key, value in list(iteritems(resource.get(method, {}))):
            if key not in list(iterkeys(inherited)):
                union[key] = value
    return union


def __is_scalar(item):
    scalar_props = [
        "type", "enum", "pattern", "minLength", "maxLength",
        "minimum", "maximum", "example", "repeat", "required",
        "default", "description", "usage", "schema", "example",
        "displayName"
    ]
    return item in scalar_props


def __get_sets(child, parent):
    child_keys = []
    parent_keys = []
    if child:
        child_keys = list(iterkeys(child))
    if parent:
        parent_keys = list(iterkeys(parent))
    child_diff = list(set(child_keys) - set(parent_keys))
    parent_diff = list(set(parent_keys) - set(child_keys))
    intersection = list(set(child_keys).intersection(parent_keys))
    opt_inters = [i for i in child_keys if str(i) + "?" in parent_keys]
    intersection = intersection + opt_inters

    return child, parent, child_diff, parent_diff, intersection


def _get_data_union(child, parent):
    # takes child data and parent data and merges them
    # with preference to child data overwriting parent data
    # confession: had to look up set theory!
    # FIXME: should bring this over from config, not hard code
    methods = [
        'get', 'post', 'put', 'delete', 'patch', 'head', 'options',
        'trace', 'connect', 'get?', 'post?', 'put?', 'delete?', 'patch?',
        'head?', 'options?', 'trace?', 'connect?'
    ]
    union = {}
    child, parent, c_diff, p_diff, inters = __get_sets(child, parent)

    for i in c_diff:
        union[i] = child.get(i)
    for i in p_diff:
        if i in methods and not i.endswith("?"):
                union[i] = parent.get(i)
        if i not in methods:
            union[i] = parent.get(i)
    for i in inters:
        if __is_scalar(i):
            union[i] = child.get(i)
        else:
            _child = child.get(i, {})
            _parent = parent.get(i, {})
            union[i] = _get_data_union(_child, _parent)
    return union


def _get_inherited_resource(res_name, resource_types):
    for resource in resource_types:
        if res_name == list(iterkeys(resource))[0]:
            return resource


def _get_res_type_attribute(res_data, method_data, item, default={}):
    method_level = _get(method_data, item, default)
    resource_level = _get(res_data, item, default)
    return method_level, resource_level


def _get_inherited_type_params(data, attribute, params, resource_types):
    inherited = _get_inherited_resource(data.get("type"), resource_types)
    inherited = inherited.get(data.get("type"))
    inherited_params = inherited.get(attribute, {})

    return dict(list(iteritems(params)) +
                list(iteritems(inherited_params)))


def _get_inherited_item(items, item_name, res_types, meth_, _data):
    inherited = _get_inherited_resource(_data.get("type"), res_types)
    resource = inherited.get(_data.get("type"))
    res_level = resource.get(meth_, {}).get(item_name, {})

    method_ = resource.get(meth_, {})
    method_level = method_.get(item_name, {})
    items = dict(
        list(iteritems(items)) +
        list(iteritems(res_level)) +
        list(iteritems(method_level))
    )
    return items


def _get_attribute_dict(data, item, v):
    resource_level = _get(v, item, {})
    method_level = _get(data, item, {})
    return dict(list(iteritems(resource_level)) +
                list(iteritems(method_level)))


def _map_attr(attribute):
    return {
        "mediaType": "media_type",
        "protocols": "protocols",
        "headers": "headers",
        "body": "body",
        "responses": "responses",
        "uriParameters": "uri_params",
        "baseUriParameters": "base_uri_params",
        "queryParameters": "query_params",
        "formParameters": "form_params",
        "description": "description"
    }[attribute]


# create_node
def _get_method(attribute, method, raw_data):
    """Returns ``attribute`` defined at the method level, or ``None``."""
    # if method is not None:  # must explicitly say `not None`
    #     get_attribute = raw_data.get(method, {})
    #     if get_attribute is not None:
    #         return get_attribute.get(attribute, {})
    # return {}
    # if method is not None:
    ret = _get(raw_data, method, {})
    ret = _get(ret, attribute, {})
    return ret


def _get_resource(attribute, raw_data):
    """Returns ``attribute`` defined at the resource level, or ``None``."""
    return raw_data.get(attribute, {})


def _get_parent(attribute, parent):
    if parent:
        return getattr(parent, attribute, {})
    return {}


# needs/uses parsed raml data
def _get_resource_type(attribute, root, type_, method):
    """Returns ``attribute`` defined in the resource type, or ``None``."""
    if type_ and root.resource_types:
        types = root.resource_types
        r_type = [r for r in types if r.name == type_]
        r_type = [r for r in r_type if r.method == method]
        if r_type:
            if hasattr(r_type[0], attribute):
                if getattr(r_type[0], attribute) is not None:
                    return getattr(r_type[0], attribute)
    return []


def _get_trait(attribute, root, is_):
    """Returns ``attribute`` defined in a trait, or ``None``."""

    if is_:
        traits = root.traits
        if traits:
            trait_objs = []
            for i in is_:
                trait = [t for t in traits if t.name == i]
                if trait:
                    if hasattr(trait[0], attribute):
                        if getattr(trait[0], attribute) is not None:
                            trait_objs.extend(getattr(trait[0], attribute))
            return trait_objs
    return []


def _get_scheme(item, root):
    schemes = root.raw.get("securitySchemes", [])
    for s in schemes:
        if isinstance(item, str):
            if item == list(iterkeys(s))[0]:
                return s
        elif isinstance(item, dict):
            if list(iterkeys(item))[0] == list(iterkeys(s))[0]:
                return s


def _get_attribute(attribute, method, raw_data):
    method_level = _get_method(attribute, method, raw_data)
    resource_level = _get_resource(attribute, raw_data)
    return OrderedDict(list(iteritems(method_level)) +
                       list(iteritems(resource_level)))


def _get_inherited_attribute(attribute, root, type_, method, is_):
    type_objects = _get_resource_type(attribute, root, type_, method)
    trait_objects = _get_trait(attribute, root, is_)
    return type_objects + trait_objects


# TODO: refactor - this ain't pretty
def _remove_duplicates(inherit_params, resource_params):
    ret = []
    if isinstance(resource_params[0], Body):
        _params = [p.mime_type for p in resource_params]
    else:
        _params = [p.name for p in resource_params]

    for p in inherit_params:
        if isinstance(p, Body):
            if p.mime_type not in _params:
                ret.append(p)
        else:
            if p.name not in _params:
                ret.append(p)
    ret.extend(resource_params)
    return ret or None


def _map_inheritance(nodetype):
    return {
        "traits": __trait,
        "types": __resource_type,
        "method": __method,
        "resource": __resource,
        "parent": __parent,
        "root": __root
    }[nodetype]


def __trait(item, **kwargs):
    root = kwargs.get("root")
    is_ = kwargs.get("is_")
    return _get_trait(item, root, is_)


def __resource_type(item, **kwargs):
    root = kwargs.get("root")
    type_ = kwargs.get("type_")
    method = kwargs.get("method")
    item = _map_attr(item)
    return _get_resource_type(item, root, type_, method)


def __method(item, **kwargs):
    method = kwargs.get("method")
    data = kwargs.get("data")
    return _get_method(item, method, data)


def __resource(item, **kwargs):
    data = kwargs.get("data")
    return _get_resource(item, data)


def __parent(item, **kwargs):
    parent = kwargs.get("parent")
    return _get_parent(item, parent)


def __root(item, **kwargs):
    root = kwargs.get("root")
    item = _map_attr(item)
    return getattr(root, item, None)


def get_inherited(item, inherit_from=[], **kwargs):
    ret = {}
    for nodetype in inherit_from:
        inherit_func = _map_inheritance(nodetype)
        inherited = inherit_func(item, **kwargs)
        ret[nodetype] = inherited
    return ret


#####
# set uri, form, query, header objects for traits
#####

def set_param_object(param_data, param_str, root):
    params = _get(param_data, param_str, {})
    param_obj = _map_param_unparsed_str_obj(param_str)
    return _create_base_param_obj(params,
                                  param_obj,
                                  root.config,
                                  root.errors)


#####
# set query, form, uri params for resource nodes
#####

# <--[uri]-->
def __create_params(unparsed, parsed, method, raw_data, root, cls, type_, is_):
    _params = _get_attribute(unparsed, method, raw_data)
    param_objs = _get_inherited_attribute(parsed, root, type_,
                                          method, is_)
    params = _create_base_param_obj(_params, cls, root.config, root.errors)
    return params, param_objs


def _create_uri_params(unparsed, parsed, root_params, root, type_, is_,
                       method, raw_data, parent):
    params, param_objs = __create_params(unparsed, parsed, method, raw_data,
                                         root, URIParameter, type_, is_)

    if params:
        param_objs.extend(params)
    if parent and parent.uri_params:
        param_objs.extend(parent.uri_params)
    if root_params:
        param_names = [p.name for p in param_objs]
        _params = [p for p in root_params if p.name not in param_names]
        param_objs.extend(_params)
    return param_objs or None
# <--[uri]-->


# <--[query, base uri, form]-->
def _check_already_exists(param, ret_list):
    if isinstance(param, Body):
        param_name_list = [p.mime_type for p in ret_list]
        if param.mime_type not in param_name_list:
            ret_list.append(param)
            param_name_list.append(param.mime_type)

    else:
        param_name_list = [p.name for p in ret_list]
        if param.name not in param_name_list:
            ret_list.append(param)
            param_name_list.append(param.name)
    return ret_list


# TODO: refactor - this ain't pretty
def __remove_duplicates(to_clean):
    # order: resource, inherited, parent, root
    ret = []

    for param_set in to_clean:
        if param_set:
            for p in param_set:
                ret = _check_already_exists(p, ret)
    return ret or None


def _map_parsed_str(parsed):
    name = parsed.split("_")[:-1]
    name.append("parameters")
    name = [n.capitalize() for n in name]
    name = "".join(name)
    return name[0].lower() + name[1:]


def set_params(data, param_str, root, method, inherit=False, **kw):
    params, param_objs, parent_params, root_params = [], [], [], []

    unparsed = _map_parsed_str(param_str)
    param_obj = _map_param_unparsed_str_obj(unparsed)
    _params = _get_attribute(unparsed, method, data)

    params = _create_base_param_obj(_params, param_obj,
                                    root.config, root.errors)
    if params is None:
        params = []

    # inherited objects
    if inherit:
        type_ = kw.get("type_")
        is_ = kw.get("is_")
        param_objs = _get_inherited_attribute(param_str, root, type_,
                                              method, is_)

    # parent objects
    parent = kw.get("parent")
    if parent:
        parent_params = getattr(parent, param_str, [])

    # root objects
    root = kw.get("root_params")
    if root:
        param_names = [p.name for p in param_objs]
        root_params = [p for p in root if p.name not in param_names]

    to_clean = (params, param_objs, parent_params, root_params)

    return __remove_duplicates(to_clean)
# <--[query, base uri, form]-->


# preserve order of URI and Base URI parameters
# used for RootNode, ResourceNode
def _preserve_uri_order(path, param_objs, config, errors, declared=[]):
    # if this is hit, RAML shouldn't be valid anyways.
    if isinstance(path, list):
        path = path[0]

    sorted_params = []
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
        for m in missing:
            # no need to create a URI param for version
            if m == "version":
                continue
            data = {"type": "string"}
            _param = URIParameter(name=m,
                                  raw={m: data},
                                  required=True,
                                  display_name=m,
                                  desc=_get(data, "description"),
                                  min_length=_get(data, "minLength"),
                                  max_length=_get(data, "maxLength"),
                                  minimum=_get(data, "minimum"),
                                  maximum=_get(data, "maximum"),
                                  default=_get(data, "default"),
                                  enum=_get(data, "enum"),
                                  example=_get(data, "example"),
                                  repeat=_get(data, "repeat", False),
                                  pattern=_get(data, "pattern"),
                                  type=_get(data, "type", "string"),
                                  config=config,
                                  errors=errors)
            param_objs.append(_param)
    for p in params:
        _param = [i for i in param_objs if i.name == p]
        if _param:
            sorted_params.append(_param[0])
    return sorted_params or None
