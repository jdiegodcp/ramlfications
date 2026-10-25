# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB


import attr

from ramlfications.config import MEDIA_TYPES
from ramlfications.models.base import (
    BaseParameterRaml08, BaseParameterRaml10
)
from ramlfications.models.parameters import (
    Body, Header, Response, URIParameter
)
from ramlfications.utils import load_schema, NodeList
from ramlfications.utils.common import (
    _get, resource_path_name, substitute_parameters
)
from ramlfications.utils.parameter import (
    map_object, resolve_scalar_data, add_missing_uri_data
)
from ramlfications.utils.parser import get_data_type_obj_by_name
from ramlfications.utils.examples import parse_examples


def default_media_types(root):
    """
    Return the root-level default media type(s) as a list, for bodies
    declared without an explicit media type.
    """
    media_type = root.media_type if root else None
    if not media_type:
        return [None]
    if isinstance(media_type, list):
        return media_type
    return [media_type]


class BaseParameterParser(object):

    # We keep a cache of concrete classes created when we mix in the
    # RAML-version-specific specialization below so general equality
    # support provided by the attr package remains useful.
    #
    # Creating a new class every time through breaks that.
    #
    _classes = {}

    def create_base_param_obj(self, attribute_data, param_obj,
                              config, errors, root, **kw):
        """
        Helper function to create a child of a
        :py:class:`.parameters.BaseParameter` object
        """
        objects = NodeList()

        for key, value in list(attribute_data.items()):
            if param_obj is URIParameter:
                required = _get(value, "required", default=True)
            else:
                required = _get(value, "required", default=False)
            data_type_name = _get(value, "type")
            data_type = get_data_type_obj_by_name(data_type_name, root)
            kwargs = dict(
                name=key,
                raw={key: value},
                data_type=data_type,
                display_name=_get(value, "displayName", key),
                min_length=_get(value, "minLength"),
                max_length=_get(value, "maxLength"),
                minimum=_get(value, "minimum"),
                maximum=_get(value, "maximum"),
                default=_get(value, "default"),
                enum=_get(value, "enum"),
                example=_get(value, "example"),
                required=required,
                pattern=_get(value, "pattern"),
                type=_get(value, "type", "string"),
                config=config,
                errors=errors
            )
            if param_obj is Header:
                kwargs["method"] = _get(kw, "method")
            if param_obj is not Body:
                kwargs["desc"] = _get(value, "description")

            # Getting the RAML version we're working with is a little
            # tricky since we may have a root node, which always allows
            # us to get it, but sometimes we don't (while processing
            # parameters directly associated with the RAML root).
            #
            if root is None:
                raml_version = self.kwargs['data']._raml_version
            else:
                raml_version = root.raml_version

            if raml_version == "0.8":
                kwargs["repeat"] = _get(value, "repeat", False)

            if raml_version == "0.8" and isinstance(value, list):
                # This is a sneaky union; need to handle this differently.
                # Applies only to RAML 0.8; see:
                #
                # https://github.com/raml-org/raml-spec/blob/master/versions/
                # raml-08/raml-08.md#named-parameters-with-multiple-types
                #
                # TODO: Complete once union types are implemented.
                pass
            else:
                kwargs.update(parse_examples(raml_version, value))

            # build object class based off of raml version
            ParamObj = param_obj
            mixin = BaseParameterRaml10
            suffix = "10"
            if raml_version == "0.8":
                mixin = BaseParameterRaml08
                suffix = "08"

            key = param_obj, mixin

            if key in self._classes:
                ParamObj = self._classes[key]
            else:
                @attr.s
                class ParamObj(mixin, param_obj):
                    pass

                ParamObj.__name__ = param_obj.__name__ + suffix
                self._classes[key] = ParamObj

            item = ParamObj(**kwargs)
            objects.append(item)

        return objects or None


class BodyParserMixin(object):
    def parse_body(self, mime_type, data, root, method):
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
        form_param_parser = ParameterParser("formParameters", kwargs)
        form_params = form_param_parser.parse()
        data_type_name = _get(data, "type")
        data_type = get_data_type_obj_by_name(data_type_name, root)
        return Body(
            mime_type=mime_type,
            raw=raw,
            schema=load_schema(_get(data, "schema")),
            example=load_schema(_get(data, "example")),
            form_params=form_params,
            data_type=data_type,
            type=_get(data, "type"),
            config=root.config,
            errors=root.errors
        )


class ParameterParser(BaseParameterParser, BodyParserMixin):
    """
    Base parser for Named Parameters.
    """
    def __init__(self, param, kwargs, resolve_from=[]):
        self.param = param
        self.resolve_from = resolve_from
        self.kwargs = kwargs
        self.method = _get(kwargs, "method", None)
        self.path = _get(kwargs, "resource_path")
        self.is_ = _get(kwargs, "is_", None)
        self.type_ = _get(kwargs, "type_", None)
        self.data_type = _get(kwargs, "data_type", None)
        self.root = _get(kwargs, "root")

    def _set_param_data(self, param_data, path, path_name):
        # copy so the assignment in the raw RAML data is left untouched
        param_data = dict(param_data or {})
        param_data["resourcePath"] = path
        param_data["resourcePathName"] = path_name
        return param_data

    def _substitute_params(self, resolved):
        """
        Returns dict of param data with relevant ``<<parameter>>`` substituted.
        """
        # this logic ain't too pretty...
        raml_version = getattr(self.root, "raml_version", None)
        if self.path:
            _path = self.path
            _path_name = resource_path_name(_path, raml_version)
        else:
            _path = "<<resourcePath>>"
            _path_name = "<<resourcePathName>>"

        if self.is_:
            if isinstance(self.is_, list):
                # I think validate.py would error out if this is not a list
                for i in self.is_:
                    if isinstance(i, dict):
                        param_data = list(i.values())[0]
                        param_data = self._set_param_data(param_data, _path,
                                                          _path_name)
                        resolved = substitute_parameters(
                            resolved, param_data, raml_version)

        if self.type_:
            if isinstance(self.type_, dict):
                param_type = self.type_
                param_data = list(param_type.values())[0]
                param_data = self._set_param_data(param_data, _path,
                                                  _path_name)
                resolved = substitute_parameters(
                    resolved, param_data, raml_version)

        # also needed for string (``type: name``) or no assignments
        if self.path:
            resolved = substitute_parameters(
                resolved, self._set_param_data({}, _path, _path_name),
                raml_version)
        return resolved

    def resolve(self):
        resolved = resolve_scalar_data(self.param, self.resolve_from,
                                       **self.kwargs)
        resolved = self._substitute_params(resolved)

        if self.param == "uriParameters":
            if self.path:
                resolved = add_missing_uri_data(self.path, resolved)
        return resolved

    def parse_bodies(self, resolved):
        """
        Returns a list of :py:class:`.parameters.Body` objects.
        """
        root = _get(self.kwargs, "root")
        method = _get(self.kwargs, "method")
        body_objects = []
        no_mime_body_data = {}
        for k, v in list(resolved.items()):
            if v is None:
                continue
            if k in ("type", "schema", "example", "examples", "properties"):
                # body declared without an explicit media type; the
                # root-level default mediaType applies
                no_mime_body_data[k] = v
                continue
            body = self.parse_body(k, v, root, method)
            body_objects.append(body)
        if no_mime_body_data:
            for mime_type in default_media_types(root):
                body = self.parse_body(
                    mime_type, no_mime_body_data, root, method)
                body_objects.append(body)
        return body_objects or None

    def parse_responses(self, resolved):
        """
        Returns a list of :py:class:`.parameters.Response` objects.
        """
        # root = _get(self.kwargs, "root")
        method = _get(self.kwargs, "method")
        response_objects = []

        for key, value in list(resolved.items()):
            response_parser = ResponseParser(key, value, method, self.root)
            response = response_parser.parse()
            response_objects.append(response)
        return sorted(response_objects, key=lambda x: x.code) or None

    def parse(self):
        if not self.resolve_from:
            self.resolve_from = ["method", "resource"]  # set default

        resolved = self.resolve()
        if self.param == "body":
            return self.parse_bodies(resolved)
        if self.param == "responses":
            return self.parse_responses(resolved)

        conf = _get(self.kwargs, "conf", None)
        errs = _get(self.kwargs, "errs", None)
        if self.root:
            conf = self.root.config
            errs = self.root.errors

        object_name = map_object(self.param)

        params = self.create_base_param_obj(resolved, object_name, conf,
                                            errs, method=self.method,
                                            root=self.root)
        return params or None


class ResponseParser(BaseParameterParser, BodyParserMixin):
    def __init__(self, code, data, method, root):
        self.code = code
        self.data = data
        self.method = method
        self.root = root

    def parse_response_headers(self):
        headers = _get(self.data, "headers", default={})

        header_objects = self.create_base_param_obj(headers, Header,
                                                    self.root.config,
                                                    self.root.errors,
                                                    method=self.method,
                                                    root=self.root)
        return header_objects or None

    def parse_response_body(self):
        """
        Create :py:class:`.parameters.Body` objects for a
        :py:class:`.parameters.Response` object.
        """
        body = _get(self.data, "body", default={})
        body_list = []
        no_mime_body_data = {}
        for key, spec in list(body.items()):
            if key not in MEDIA_TYPES:
                # if a root mediaType was defined, the response body
                # may omit the mime_type definition
                if key in ('schema', 'example'):
                    no_mime_body_data[key] = load_schema(spec) if spec else {}
                elif key in ('type', 'examples', 'properties'):
                    no_mime_body_data[key] = spec
            else:
                # spec might be '!!null'
                raw = spec or body
                _body = self.parse_body(key, raw, self.root, self.method)
                body_list.append(_body)
        if no_mime_body_data:
            for mime_type in default_media_types(self.root):
                _body = self.parse_body(mime_type,
                                        no_mime_body_data, self.root,
                                        self.method)
                body_list.append(_body)

        return body_list or None

    def parse(self):
        headers = self.parse_response_headers()
        body = self.parse_response_body()
        desc = _get(self.data, "description", None)

        if isinstance(self.code, str):
            try:
                self.code = int(self.code)
            except ValueError:
                # this should be caught by validate.py
                pass

        return Response(
            code=self.code,
            raw={self.code: self.data},
            method=self.method,
            desc=desc,
            headers=headers,
            body=body,
            config=self.root.config,
            errors=self.root.errors
        )
