# ! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function

__all__ = ["APIRoot", "Resource", "RAMLParserError"]

from collections import defaultdict
import json
import re

from six.moves import BaseHTTPServer as httpserver

try:
    from collections import OrderedDict
except ImportError:  # pragma: no cover
    from ordereddict import OrderedDict

from .parameters import (
    FormParameter, URIParameter, QueryParameter,
    Header, Response, Body, SecuritySchemes,
    Documentation, DescriptiveContent
)

HTTP_RESP_CODES = httpserver.BaseHTTPRequestHandler.responses.keys()

HTTP_METHODS = [
    "get", "post", "put", "delete", "patch", "options",
    "head", "trace", "connect", "get?", "post?", "put?", "delete?",
    "patch?", "options?", "head?", "trace?", "connect?"
]


class RAMLParserError(Exception):
    pass


class APIRoot(object):
    """
    The Root of the API object

    :param obj raml_obj: Loaded RAML from ``ramlfications.load(ramlfile)``
    """
    def __init__(self, raml_obj):
        # The line below can throw an exception but that's not documented.
        # I find it awkward too as I don't like it when constructors
        # throw exceptions.
        self.raml = raml_obj.data
        self.raml_file = raml_obj.raml_file

    @property
    def resources(self):
        """
        Returns a dict of RAML resources/endpoints, with keys set to the
        method + resource display name (e.g. ``get-item``) and values set
        to the ``Resource`` object.
        """
        # TODO: Simplify this monstrosity
        resource_stack = ResourceStack(self, self.raml).yield_resources()
        resource = OrderedDict()
        for res in resource_stack:
            key_name = res.method + "-" + res.path
            resource[key_name] = res
        resources = defaultdict(list)
        for k, v in list(resource.items()):
            resources[v.path].append((v.method.upper(), v))
        sorted_dict = OrderedDict(sorted(resources.items(),
                                  key=lambda t: t[0]))
        # sorted_list = sorted(resources.items(), key=lambda t: t[0])
        sorted_list = []
        for item in sorted_dict.values():
            for i in item:
                sorted_list.append(i[1])
        return sorted_list

    @property
    def title(self):
        """
        Returns the title property defined in the root section of the API.
        """
        return self.raml.get('title')

    @property
    def version(self):
        """
        Returns the API version.
        """
        return self.raml.get('version')

    @property
    def protocols(self):
        """
        Returns the supported protocols of the API.  If not set, then
        grabbed from ``base_uri``.
        """
        protocol = re.findall(r"(https|http)", self.base_uri)
        return self.raml.get('protocols', protocol)

    @property
    def base_uri(self):
        """
        Returns the base URI of API.

        **Note:** optional during development, required after implementation.

        :raises RAMLParserError: if no ``version`` is defined but is\
        referenced in the ``baseUri`` parameter.
        """
        base_uri = self.raml.get('baseUri')
        if base_uri:
            if "{version}" in base_uri:
                try:
                    return base_uri.replace("{version}", self.raml['version'])
                # Double-check KeyError behavior
                except KeyError:
                    # Double-check all files for consistency of
                    # double-ticks vs single-ticks for strings
                    raise RAMLParserError(
                        "No API Version defined even though version is "
                        "referred in the baseUri")

        return base_uri

    @property
    def uri_parameters(self):
        """
        Returns URI Parameters available for the baseUri and all
        resources/endpoints.  Returns ``None`` if no URI parameters
        are defined.

        :raises RAMLParserError: if ``version`` is defined (``version``
            can only be used in ``baseUriParameters``).

        """
        uri_params = self.raml.get('uriParameters', {})
        params = []
        for k, v in list(uri_params.items()):
            if k == 'version':
                raise RAMLParserError("'version' can only be defined "
                                      "in baseUriParameters")
            params.append((URIParameter(k, v)))
        return params or None

    @property
    def base_uri_parameters(self):
        """
        Returns URI Parameters for meant specifically for the ``base_uri``.
        Returns ``None`` if no base URI parameters are defined.

        **Note:** optional during development, required after implementation.
        """
        base_uri_params = self.raml.get('baseUriParameters', {})
        uri_params = []
        for k, v in list(base_uri_params.items()):
            uri_params.append((URIParameter(k, v)))
        return uri_params or None

    @property
    def media_type(self):
        # TODO: raise an error if not acceptable media type given
        """
        Returns the supported Media Types of the API.  Returns ``None``
        if no media types are defined.

        Valid media types:

        * ``text/yaml``, ``text/x-yaml``, ``application/yaml``,\
         ``application/x-yaml``
        * Any defined in http://www.iana.org/assignments/media-types
        * A custom type that follows the regex:\
        ``application\/[A-Za-z.-0-1]*+?(json|xml)``

        """
        return self.raml.get('mediaType')

    # TODO: super hacky way to get the union of resourceTypes.
    # perhaps there's a better way
    def _get_union(self, resource, inherited_resource):
        if inherited_resource is {}:
            return resource
        union = {}
        if not resource:
            return inherited_resource
        for k, v in list(inherited_resource.items()):
            if k not in resource.keys():
                union[k] = v
            else:
                resource_values = resource.get(k)
                inherited_values = inherited_resource.get(k, {})
                union[k] = dict(inherited_values.items() +
                                resource_values.items())
        for k, v in list(resource.items()):
            if k not in inherited_resource.keys():
                union[k] = v
        return union

    # Returns data dict of particular resourceType
    def _get_inherited_resource(self, res_name, resource_types):
        for r in resource_types:
            if res_name == r.keys()[0]:
                return dict(r.values()[0].items())

    def _map_inherited_resource_types(self, resource, inherited, types):
        resources = []
        inherited_res = self._get_inherited_resource(inherited, types)
        for k, v in list(resource.items()):
            for i in v.keys():
                if i in HTTP_METHODS:
                    data = self._get_union(v.get(i, {}),
                                           inherited_res.get(i, {}))
                    resources.append(ResourceType(k, data, i, self,
                                                  type=inherited))
        return resources

    @property
    def resource_types(self):
        """
        Returns defined Resource Types.  Returns ``None`` if no resource
        types are defined.
        """
        resource_types = self.raml.get('resourceTypes', [])
        resources = []
        for resource in resource_types:
            for k, v in list(resource.items()):
                # first parse out if it inherits another resourceType
                if 'type' in v.keys():
                    r = self._map_inherited_resource_types(resource,
                                                           v.get('type'),
                                                           resource_types)
                    resources.extend(r)
                # else just create a ResourceType
                else:
                    for i in v.keys():
                        if i in HTTP_METHODS:
                            resources.append(ResourceType(k, v, i, self))

        return resources or None

    @property
    def documentation(self):
        """
        Returns a list of Documentation objects meant for user documentation
        of the for the API, or ``None`` if no documentation is defined.

        :raises RAMLParserError: if can not parse documentation.
        """
        documentation = self.raml.get('documentation', [])
        if not isinstance(documentation, list):
            msg = "Error parsing documentation"
            raise RAMLParserError(msg)
        docs = []
        for doc in documentation:
            doc = Documentation(doc.get('title'), doc.get('content'))
            docs.append(doc)
        return docs or None

    @property
    def security_schemes(self):
        """
        Returns a list of SecurityScheme objects supported by the API,
        or ``None`` if none are defined.

        Valid security schemes are: OAuth 1.0, OAuth 2.0, Basic Authentication,
         Digest Authentication, and API-defined auth with ``x-{other}``.
        """
        return SecuritySchemes(self.raml).security_schemes

    @property
    def traits(self):
        """
        Returns a list of traits, or ``None`` if non are defined.
        """
        # Simplify this method by replacing duplicate code, think
        # def _lookup_parameters
        traits = self.raml.get('traits', [])
        trait_params = []
        for trait in traits:
            trait_params.append(Trait(trait.keys()[0],
                                trait.values()[0],
                                api=self))
        return trait_params or None

    @property
    def schemas(self):
        """
        Returns a dict of user-defined schemas that may be applied anywhere
        in the API definition.

        Current explicit supported types are XML, JSON, YAML. Other schema
        definitions may work at your own risk.

        Returns ``None`` if no schema defined.
        """
        return self.raml.get('schemas')

    def __repr__(self):
        return '<APIRoot(raml_file="{0}")>'.format(self.raml_file)


class ResourceStack(object):
    available_methods = ['get', 'post', 'put', 'delete', 'patch', 'head',
                         'options', 'trace', 'connect']

    def __init__(self, api, raml_file):
        self.api = api
        self.raml = raml_file

    def _create_resource_stack(self, items, resource_stack):
        for k, v in list(items.items()):
            if k.startswith("/"):
                keys = items[k].keys()
                methods = [m for m in self.available_methods if m in keys]
                if methods:
                    for m in self.available_methods:
                        if m in items[k].keys():
                            node = Resource(name=k, data=v,
                                            method=m, api=self.api)
                            resource_stack.append(node)
                else:
                    for item in keys:
                        if item.startswith("/"):
                            _item = {}
                            _item[k + item] = items.get(k).get(item)
                            resource_stack.extend(
                                self._create_resource_stack(_item,
                                                            resource_stack)
                            )

        return resource_stack

    def yield_resources(self):
        """
        Yields Resource objects for the API defined in the RAML File.
        """

        resource_stack = self._create_resource_stack(self.raml, [])

        # Akward code, create a helper method for it.
        while resource_stack:
            current = resource_stack.pop(0)
            yield current
            if current.data:
                for child_k, child_v in list(current.data.items()):
                    if child_k.startswith("/"):
                        for method in self.available_methods:
                            if method in current.data[child_k].keys():
                                child = Resource(name=child_k, data=child_v,
                                                 method=method, parent=current,
                                                 api=self.api)
                                resource_stack.append(child)


class _BaseResourceProperties(object):
    """
    Base class from which Trait, Resource, and ResourceType to inherit.
    """
    def __init__(self, name, data, api):
        self.name = name
        self.data = data
        self.api = api

    @property
    def headers(self):
        """
        Returns a list of accepted Header objects.

        Returns ``None`` if no headers defined.
        """
        resource_headers = self.data.get('headers', {})
        headers = []
        for k, v in list(resource_headers.items()):
            headers.append(Header(k, v))
        return headers or None

    @property
    def body(self):
        """
        Returns a list of Body objects of a request or
        ``None`` if none defined.
        """
        bodies = []
        resource_body = self.data.get('body', {})
        for k, v in list(resource_body.items()):
            bodies.append(Body(k, v))
        return bodies or None

    @property
    def responses(self):
        """
        Returns a list of ``Response`` objects of a Trait, or ``None``
        if none are defined.

        :raises RAMLParserError: Unsupported HTTP Response code
        """
        resps = []
        resource_responses = self.data.get('responses', {})
        for k, v in list(resource_responses.items()):
            if int(k) in HTTP_RESP_CODES:
                resps.append(Response(k, v, self.method))
            else:
                msg = "{0} not a supported HTTP Response code".format(k)
                raise RAMLParserError(msg)

        return resps or None

    @property
    def uri_params(self):
        """
        Returns a list of ``URIParameter`` objects of a Trait, or
        ``None`` if none are defined.
        """
        uri_params = []
        for k, v in list(self.data.get('uriParameters', {}).items()):
            uri_params.append((URIParameter(k, v)))

        return uri_params or None

    @property
    def base_uri_params(self):
        """
        Returns a list of ``URIParameter`` objects of a Trait for
        ``base_uri``, or ``None`` if none are defined.
        """
        base_uri_params = []
        for k, v in list(self.data.get('baseUriParameters', {}).items()):
            base_uri_params.append((URIParameter(k, v)))
        return base_uri_params or None

    @property
    def query_params(self):
        """
        Returns a list of ``QueryParameter`` objects of a Trait,
        or ``None`` if no query parameters are defined.
        """
        resource_params = self.data.get('queryParameters', {})

        query_params = []
        for k, v in list(resource_params.items()):
            query_params.append((QueryParameter(k, v)))
        return query_params or None

    @property
    def form_params(self):
        """
        Returns a list of FormParameter objects, or ``None`` if no form
        parameters are defined.
        """
        form_params = []
        for k, v in list(self.data.get('formParameters', {}).items()):
            form_params.append((FormParameter(k, v)))
        return form_params or None

    @property
    def req_mime_types(self):
        """
        Returns a list of strings referring to MIME types that the
        Trait supports, or ``None`` if none defined.
        """
        mime_types = self.data.get('body', {}).keys()

        return mime_types or None

    @property
    def description(self):
        """
        Returns ``DescriptiveContent`` object with ``raw`` and ``html``
        attributes, or ``None`` if not defined.

        Assumes raw content is written in plain text or Markdown in RAML
        per specification. (Optional)
        """
        resource_desc = self.data.get('description')
        if resource_desc:
            return DescriptiveContent(resource_desc)
        return None


class Trait(_BaseResourceProperties):
    """
    Method-level properties to apply to a Resource or ResourceType.
    """
    @property
    def usage(self):
        """
        Returns a string detailing how to use this trait.
        """
        return self.data.get('usage')

    def __repr__(self):
        return "<Trait(name='{0}')>".format(self.name)


class _BaseResource(_BaseResourceProperties):
    def __init__(self, name, data, method, api):
        _BaseResourceProperties.__init__(self, name, data, api)
        self.method = method

    @property
    def is_(self):
        """
        Returns a list of strings denoting traits assign to Resource or
        Resource Type, or ``None`` if not defined.

        Use ``resource.traits`` to get the actual ``Trait`` object.
        """
        method_traits = self.data.get(self.method, {}).get('is', [])
        resource_traits = self.data.get('is', [])
        return method_traits + resource_traits or None

    def _fill_params(self, string, key, value):
        if key in string:
            string = string.replace("<<" + key + ">>", str(value))
        string = self._fill_reserved_params(string)
        return string

    def _get_traits_str(self, trait):
        api_traits = self.api.traits

        api_traits_names = [a.name for a in api_traits]
        if trait not in api_traits_names:
            msg = "'{0}' is not defined in API Root's resourceTypes."
            raise RAMLParserError(msg)

        for t in api_traits:
            if t.name == trait:
                return t
        return None

    def _get_traits_dict(self, trait):
        api_traits = self.api.traits or []

        _trait = list(trait.keys())[0]
        api_trait_names = [a.name for a in api_traits]
        if _trait not in api_trait_names:
            msg = "'{0}' is not defined in API Root's traits."
            raise RAMLParserError(msg)

        for t in api_traits:
            if t.name == _trait:
                _values = list(trait.values())[0]
                data = json.dumps(t.data)
                for k, v in list(_values.items()):
                    data = self._fill_params(data, k, v)
                data = json.loads(data)
                return Trait(t.name, data, self.api)
        return None

    def _get_traits(self):
        if not self.is_:
            return None

        if not self.api.traits:
            msg = "No traits are defined in RAML file."
            raise RAMLParserError(msg)

        trait_objects = []
        for trait in self.is_:
            trait_names = [t.name for t in self.api.traits]
            if isinstance(trait, str):
                if trait not in trait_names:
                    msg = "'{0}' not defined under traits in RAML.".format(
                        trait)
                    raise RAMLParserError(msg)
                str_trait = self._get_traits_str(trait)
                trait_objects.append(str_trait)
            elif isinstance(trait, dict):
                if trait.keys()[0] not in trait_names:
                    msg = "'{0}' not defined under traits in RAML.".format(
                        trait)
                    raise RAMLParserError(msg)
                dict_trait = self._get_traits_dict(trait)
                trait_objects.append(dict_trait)

        return trait_objects or None

    @property
    def traits(self):
        """
        Returns a list of ``Trait`` objects assigned to the Resource or
        ResourceType, if any.

        Use ``resource.is_`` to get a simple list of strings denoting the
        names of applicable traits.
        """
        return self._get_traits()

    @property
    def protocols(self):
        """
        Returns a list of supported protocols for the particular Resource or
        ResourceType.

        Overrides the root API's protocols.  Returns ``None`` if not defined.
        """
        method_protocols = self.data.get(self.method).get('protocols', [])
        resource_protocols = self.data.get('protocols', [])
        return list(set(method_protocols + resource_protocols)) or None

    #####
    # Following properties extend those from _BaseResourceProperies
    #####

    @property
    def headers(self):
        """
        Returns a list of accepted Header objects for Resource or
        ResourceTypes, or  ``None`` if no headers defined.
        """
        method_headers = self.data.get(self.method, {}).get('headers', {})

        headers = super(_BaseResource, self).headers or []

        for k, v in list(method_headers.items()):
            headers.append(Header(k, v, self.method))
        return headers or None

    @property
    def body(self):
        """
        Returns a list of Body objects of a request for Resource or
        ResourceTypes, or ``None`` if none defined.
        """
        bodies = super(_BaseResource, self).body or []
        method_body = self.data.get(self.method, {}).get('body', {})
        for k, v in list(method_body.items()):
            bodies.append(Body(k, v))
        return bodies or None

    @property
    def responses(self):
        """
        Returns a list of Response objects of a Resource or ResourceType,
        or ``None`` if none defined.

        :raises RAMLParserError: Unsupported HTTP Response code
        """
        resps = super(_BaseResource, self).responses or []
        method_responses = self.data.get(self.method, {}).get('responses', {})
        for k, v in list(method_responses.items()):
            if int(k) in HTTP_RESP_CODES:
                resps.append(Response(k, v, self.method))
            else:
                msg = "{0} not a supported HTTP Response code".format(k)
                raise RAMLParserError(msg)

        return resps

    @property
    def uri_params(self):
        """
        Returns a list of ``URIParameter`` objects of a Resource or
        ResourceType, or ``None`` if none are defined.
        """
        uri_params = super(_BaseResource, self).uri_params or []
        method_params = self.data.get(self.method, {}).get('uriParameters', {})
        for k, v in list(method_params.items()):
            uri_params.append((URIParameter(k, v)))

        return uri_params or None

    @property
    def base_uri_params(self):
        """
        Returns a list of base ``URIParameter`` objects of a Resource or
        ResourceType, or ``None`` if none are defined.
        """
        base_params = super(_BaseResource, self).base_uri_params or []
        method_params = self.data.get(self.method, {}).get(
            'baseUriParameters', {})
        for k, v in list(method_params.items()):
            base_params.append((URIParameter(k, v)))

        return base_params or None

    @property
    def query_params(self):
        """
        Returns a list of ``QueryParameter`` objects of a Resource or
        ResourceType, or ``None`` if no query parameters are defined.
        """
        query_params = super(_BaseResource, self).query_params or []
        method_params = self.data.get(self.method, {}).get(
            'queryParameters', {})
        for k, v in list(method_params.items()):
            query_params.append(QueryParameter(k, v))

        return query_params or None

    @property
    def form_params(self):
        """
        Returns a list of FormParameter objects of a Resource or
        ResourceType, or ``None`` if no form parameters are defined.
        """

        form_params = super(_BaseResource, self).form_params or []

        method_params = {}
        url_form = {}
        multipart = {}

        if self.method in ['post', 'delete', 'put', 'patch']:
            method_params = self.data.get(self.method, {}).get(
                'formParameters', {})
            # TODO: will these show up outside of a method?
            url_form = self.data.get(self.method, {}).get('body').get(
                'application/x-www-form-urlencoded', {}).get(
                'formParameters', {})
            multipart = self.data.get(self.method, {}).get('body').get(
                'multipart/form-data', {}).get('formParameters', {})

        items = dict(method_params.items() +
                     url_form.items() +
                     multipart.items())

        for k, v in list(items.items()):
            form_params.append((FormParameter(k, v)))
        return form_params or None

    @property
    def req_mime_types(self):
        """
        Returns a list of strings referring to MIME types that the
        Resource or ResourceType supports, or ``None`` if none defined.
        """
        method_mime = []
        if self.method in ["post", "put", "delete", "patch"]:
            method_mime = self.data.get(self.method, {}).get('body', {}).keys()
        mime_types = self.data.get('body', {}).keys() + method_mime

        return mime_types or None

    @property
    def description(self):
        """
        Returns ``DescriptiveContent`` object with ``raw`` and ``html``
        attributes, or ``None`` if not defined.

        Assumes raw content is written in plain text or Markdown in RAML
        per specification.
        """
        method_desc = self.data.get(self.method, {}).get('description')
        if method_desc:
            return DescriptiveContent(method_desc)
        return super(_BaseResource, self).description


class ResourceType(_BaseResource):
    """
    Resource-level properties to apply to a Resource.
    """
    def __init__(self, name, data, method, api, type=None):
        _BaseResource.__init__(self, name, data, method, api)
        self.orig_method = method
        self.method = self._clean_method(method)
        self.type = type

    def _clean_method(self, method):
        if method.endswith("?"):
            return method[:-1]
        return method

    @property
    def usage(self):
        """
        Returns a string detailing how to use this ResourceType.
        """
        return self.data.get('usage')

    @property
    def optional(self):
        """
        Returns ``True`` if ``?`` in method, denoting that it is optional.
        """
        return "?" in self.orig_method

    def __repr__(self):
        return "<ResourceType(method='{0}', name='{1}')>".format(
            self.method.upper(), self.name)

    #####
    # Following properties extend those from _BaseResourceProperies
    #####
    @property
    def protocols(self):
        """
        Returns a list of supported protocols for the particular ResourceType.

        Overrides the root API's protocols.  Returns ``None`` if not defined.
        """
        protocols = super(ResourceType, self).protocols or []
        opt_method_protocols = self.data.get(self.orig_method).get(
            'protocols', [])
        return list(set(opt_method_protocols + protocols)) or None

    @property
    def headers(self):
        """
        Returns a list of accepted Header objects for ResourceType,
        or  ``None`` if no headers defined.
        """
        opt_method_headers = self.data.get(self.orig_method, {}).get(
            'headers', {})

        headers = super(ResourceType, self).headers or []
        for k, v in list(opt_method_headers.items()):
            headers.append(Header(k, v, self.method))
        return headers or None

    @property
    def body(self):
        """
        Returns a list of Body objects of a request for ResourceType,
        or ``None`` if none defined.
        """
        bodies = super(ResourceType, self).body or []
        opt_method_body = self.data.get(self.orig_method, {}).get('body', {})
        for k, v in list(opt_method_body.items()):
            bodies.append(Body(k, v))
        return bodies or None

    @property
    def responses(self):
        """
        Returns a list of Response objects of a ResourceType, or ``None``
        if none are defined.

        :raises RAMLParserError: Unsupported HTTP Response code
        """
        resps = super(ResourceType, self).responses or []
        opt_method_resps = self.data.get(self.orig_method, {}).get(
            'responses', {})

        for k, v in list(opt_method_resps.items()):
            if int(k) in HTTP_RESP_CODES:
                resps.append(Response(k, v, self.method))
            else:
                msg = "{0} not a supported HTTP Response code".format(k)
                raise RAMLParserError(msg)

        return resps

    @property
    def uri_params(self):
        """
        Returns a list of ``URIParameter`` objects of a ResourceType, or
        ``None`` if none are defined.
        """
        uri_params = super(ResourceType, self).uri_params or []
        orig_method_params = self.data.get(self.orig_method, {}).get(
            'uriParameters', {})
        for k, v in list(orig_method_params.items()):
            uri_params.append((URIParameter(k, v)))

        return uri_params or None

    @property
    def base_uri_params(self):
        """
        Returns a list of base ``URIParameter`` objects of a ResourceType,
        or ``None`` if none are defined.
        """
        base_params = super(ResourceType, self).base_uri_params or []
        opt_method_params = self.data.get(self.orig_method, {}).get(
            'baseUriParameters', {})
        for k, v in list(opt_method_params.items()):
            base_params.append((URIParameter(k, v)))

        return base_params or None

    @property
    def query_params(self):
        """
        Returns a list of ``QueryParameter`` objects of a ResourceType,
        or ``None`` if no query parameters are defined.
        """
        query_params = super(ResourceType, self).query_params or []
        opt_method_params = self.data.get(self.orig_method, {}).get(
            'queryParameters', {})
        for k, v in list(opt_method_params.items()):
            query_params.append(QueryParameter(k, v))

        return query_params or None

    @property
    def form_params(self):
        """
        Returns a list of FormParameter objects of a ResourceType,
        or ``None`` if no form parameters are defined.
        """
        form_params = super(ResourceType, self).form_params or []

        if self.orig_method in ['post?', 'delete?', 'put?', 'patch?']:
            method_params = self.data.get(self.orig_method, {}).get(
                'formParameters', {})
            # TODO: will these show up outside of a method?
            url_form = self.data.get(self.orig_method, {}).get('body').get(
                'application/x-www-form-urlencoded', {}).get(
                'formParameters', {})
            multipart = self.data.get(self.orig_method, {}).get('body').get(
                'multipart/form-data', {}).get('formParameters', {})

        items = dict(method_params.items() +
                     url_form.items() +
                     multipart.items())

        for k, v in list(items.items()):
            form_params.append((FormParameter(k, v)))
        return form_params or None

    @property
    def req_mime_types(self):
        """
        Returns a list of strings referring to MIME types that the
        ResourceType supports, or ``None`` if none defined.
        """
        mime_types = super(ResourceType, self).req_mime_types or []
        opt_method_mime = []
        if self.orig_method in ["post?", "put?", "delete?", "patch?"]:
            opt_method_mime = self.data.get(self.orig_method, {}).get(
                'body', {}).keys()

        return mime_types + opt_method_mime or None

    @property
    def description(self):
        """
        Returns ``DescriptiveContent`` object with ``raw`` and ``html``
        attributes, or ``None`` if not defined.

        Assumes raw content is written in plain text or Markdown in RAML
        per specification.
        """
        opt_method_desc = self.data.get(self.orig_method, {}).get(
            'description')
        if opt_method_desc:
            return DescriptiveContent(opt_method_desc)
        return super(ResourceType, self).description


class Resource(_BaseResource):
    """
    An object representing an endpoint defined in RAML, identified by a leading
    slash, ``/``.
    """
    def __init__(self, name, data, method, api, parent=None):
        _BaseResource.__init__(self, name, data, method, api)
        self.parent = parent

    @property
    def display_name(self):
        """
        Returns the Resource's display name.

        A friendly name used only for display or documentation purposes.

        If ``displayName`` is not specified in RAML, it defaults to ``name``.
        """
        return self.data.get('displayName', self.name)

    def _get_path_to(self, node):
        parent_path = ''
        if node.parent:
            parent_path = self._get_path_to(node.parent)
        return parent_path + node.name

    @property
    def path(self):
        """
        Returns a string of the URI path of Resource relative to
        ``api.base_uri``.

        Not explicitly defined in RAML but inferred based off of
        the Resource ``name``.
        """
        return self._get_path_to(self)

    @property
    def absolute_path(self):
        """
        Returns a string of the absolute URI path of Resource.

        Not explicitly defined in RAML but inferred based off of
        ``path`` and the API root's ``base_uri``.
        """
        return self.api.base_uri + self.path

    def _get_secured_by(self):
        # TODO: put a validator in to check if schemes here are not in
        # list of secured schemes
        # I'd create a helper method for the if-statement below.
        if self.data.get('securedBy'):
            secured_by = self.data.get('securedBy')
        elif self.data.get(self.method).get('securedBy'):
            secured_by = self.data.get(self.method).get('securedBy')
        else:
            return None

        _secured_by = []
        for secured in secured_by:
            if isinstance(secured, dict):
                scheme = list(secured.keys())[0]
                if 'scopes' in list(secured.values())[0]:
                    scopes = list(secured.values())[0].get('scopes')
            else:
                # What's the expected type here? Can you make sure
                # that "secured" has a valid format?
                scheme = secured
                scopes = None

            _scheme = {}
            for s in self.api.security_schemes:
                if s.name == scheme:
                    _scheme['name'] = s.name
                    _scheme['type'] = s.type
                    _scheme['scheme'] = s
                if scopes:
                    _scheme['scopes'] = scopes

                if _scheme not in _secured_by:
                    _secured_by.append(_scheme)
        return _secured_by

    @property
    def secured_by(self):
        """
        Returns authentication protocol information if Resource is secured
        """
        # TODO: can ResourceTypes be secured?
        return self._get_secured_by()

    def _fill_reserved_params(self, string):
        if "<<resourcePathName>>" in string:
            name = self.name[1:]  # assumes all path names start with '/'
            string = string.replace("<<resourcePathName>>", name)
        if "<<resourcePath>>" in string:
            string = string.replace("<<resourcePath>>", self.name)

        return string

    def _fill_params(self, string, key, value):
        if key in string:
            string = string.replace("<<" + key + ">>", str(value))
        string = self._fill_reserved_params(string)
        return string

    def _map_resource_string(self, res_type):
        api_resources = self.api.resource_types

        api_resources_names = [a.name for a in api_resources]
        if res_type not in api_resources_names:
            msg = "'{0}' is not defined in API Root's resourceTypes."
            raise RAMLParserError(msg)

        for r in api_resources:
            if r.name == res_type and r.method == self.method:
                return r
        return None

    def _map_resource_dict(self, res_type):
        api_resources = self.api.resource_types or []

        _type = list(res_type.keys())[0]
        api_resources_names = [a.name for a in api_resources]
        if _type not in api_resources_names:
            msg = "'{0}' is not defined in API Root's resourceTypes."
            raise RAMLParserError(msg)

        for r in api_resources:
            if r.name == _type and r.method == self.method:
                _values = list(res_type.values())[0]
                data = json.dumps(r.data)
                for k, v in list(_values.items()):
                    data = self._fill_params(data, k, v)
                data = json.loads(data)
                return ResourceType(r.name, data, self.method,
                                    self.api, self.type)
        return None

    def _get_resource_type(self):
        res_type = self.data.get('type')
        if res_type:
            if isinstance(res_type, str):
                mapped_res_type = self._map_resource_string(res_type)

            elif isinstance(res_type, dict):
                if len(res_type.keys()) > 1:
                    msg = "Too many resource types applied to one resource."
                    raise RAMLParserError(msg)
                mapped_res_type = self._map_resource_dict(res_type)

            elif isinstance(res_type, list):
                if len(res_type) > 1:
                    msg = "Too many resource types applied to one resource."
                    raise RAMLParserError(msg)
                mapped_res_type = self._map_resource_string(res_type[0])

            else:
                msg = "Error applying resource type '{0}'' to '{1}'.".format(
                    res_type, self.name)
                raise RAMLParserError(msg)
            return mapped_res_type

        return None

    @property
    def resource_type(self):
        """
        Returns a list of ResourceType objects assigned to the Resource.

        Use ``resource.type`` to get the string name representation of the
        ResourceType applied.

        :raises RAMLParserError: Too many resource types applied to one
            resource.
        :raises RAMLParserError: Resource not defined in the API Root.
        :raises RAMLParserError: If resource type is something other
            than a ``str`` or ``dict``.
        """
        return self._get_resource_type()

    @property
    def type(self):
        """
        Returns a string of the ``type`` associated with the corresponding
        ResourceTypes, or a dictionary where the (single) key is the name
        of the mapped ResourceType, and the values are the parameters
        associated with it.

        Use ``resource.resource_type`` to get the actual ResourceType object.
        """
        resource_type = self.data.get('type')
        if not resource_type and self.parent:
            return self.parent.type
        return resource_type

    @property
    def scopes(self):
        """
        Returns a list of OAuth2 scopes assigned to the Resource, or
        ``None`` if none are defined, or is not secured by OAuth 2.
        """
        if self.secured_by:
            for item in self.secured_by:
                if 'oauth_2_0' == item.get('name'):
                    return item.get('scopes')
        return None

    @property
    def headers(self):
        """
        Returns a list of accepted Header objects for Resource,
        or  ``None`` if no headers defined.
        """
        # TODO: does resource inherit headers from its parent?
        headers = []
        if self.resource_type:
            headers.extend(self.resource_type.headers or [])
        if self.traits:
            for t in self.traits:
                headers.extend(t.headers or [])
        _headers = super(Resource, self).headers or []
        return headers + _headers or None

    @property
    def responses(self):
        """
        Returns a list of Response objects of a Resource, or ``None``
        if none are defined.

        :raises RAMLParserError: Unsupported HTTP Response code
        """
        # TODO: does resource inherit responses from its parent?
        resp = []
        if self.resource_type:
            resp.extend(self.resource_type.responses or [])
        if self.traits:
            for t in self.traits:
                resp.extend(t.responses or [])
        _resp = super(Resource, self).responses or []
        return resp + _resp or None

    @property
    def body(self):
        """
        Returns a list of Body objects of a request for Resource,
        or ``None`` if none defined.
        """
        # TODO: does resource inherit body from its parent?
        body = []
        if self.resource_type:
            body.extend(self.resource_type.body or [])
        if self.traits:
            for t in self.traits:
                body.extend(t.body or [])
        _body = super(Resource, self).body or []
        return body + _body or None

    @property
    def query_params(self):
        """
        Returns a list of ``QueryParameter`` objects of a Resource,
        or ``None`` if no query parameters are defined.
        """
        params = []
        if self.resource_type:
            params.extend(self.resource_type.query_params or [])
        if self.traits:
            for t in self.traits:
                params.extend(t.query_params or [])
        _params = super(Resource, self).query_params or []
        return params + _params or None

    @property
    def uri_params(self):
        """
        Returns a list of ``URIParameter`` objects of a Resource, or
        ``None`` if none are defined.
        """
        params = []
        if self.resource_type:
            params.extend(self.resource_type.uri_params or [])
        if self.traits:
            for t in self.traits:
                params.extend(t.uri_params or [])
        if self.parent:
            params.extend(self.parent.uri_params or [])
        _params = super(Resource, self).uri_params or []
        return params + _params or None

    @property
    def base_uri_params(self):
        """
        Returns a list of base ``URIParameter`` objects of a Resource,
        or ``None`` if none are defined.
        """
        params = []
        if self.resource_type:
            params.extend(self.resource_type.base_uri_params or [])
        if self.traits:
            for t in self.traits:
                params.extend(t.base_uri_params or [])
        if self.parent:
            params.extend(self.parent.base_uri_params or [])
        _params = super(Resource, self).base_uri_params or []
        return params + _params or None

    @property
    def form_params(self):
        """
        Returns a list of FormParameter objects of a Resource,
        or ``None`` if no form parameters are defined.
        """
        params = []
        if self.resource_type:
            params.extend(self.resource_type.form_params or [])
        if self.traits:
            for t in self.traits:
                params.extend(t.form_params or [])
        _params = super(Resource, self).form_params or []
        return params + _params or None

    @property
    def traits(self):
        traits = []
        if self.resource_type:
            traits.extend(self.resource_type.traits or [])
        if self.parent:
            traits.extend(self.parent.traits or [])
        _traits = super(Resource, self).traits or []
        return traits + _traits or None

    @property
    def description(self):
        """
        Returns ``DescriptiveContent`` object with ``raw`` and ``html``
        attributes, or ``None`` if not defined.

        Assumes raw content is written in plain text or Markdown in RAML
        per specification.
        """
        if super(Resource, self).description is not None:
            return super(Resource, self).description
        elif self.resource_type and self.resource_type.description:
            desc = self._fill_reserved_params(
                self.resource_type.description.raw)
            return DescriptiveContent(desc)
        elif self.parent:
            return self.parent.description
        return None

    def __repr__(self):
        return "<Resource(method='{0}', path='{1}')>".format(
            self.method.upper(), self.path)
