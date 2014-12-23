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
from .utils import find_params


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
            key_name = res.method + "-" + res.display_name
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
                union[k] = dict(inherited_values.items() + resource_values.items())
        for k, v in list(resource.items()):
            if k not in inherited_resource.keys():
                union[k] = v
        return union

    # Returns data dict of particular resourceType
    def _get_inherited_resource(self, res_name, resource_types):
        for r in resource_types:
            if res_name == r.keys()[0]:
                return dict(r.values()[0].items())

    def _map_inherited_resource_types(self, resource, inherited, resource_types):
        resources = []
        inherited_res = self._get_inherited_resource(inherited, resource_types)
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

    def _map_inherited(self, name, resources, inherited):
        res = {}
        for key, value in list(resources.items()):
            if key in HTTP_METHODS:
                if key in inherited.keys():
                    if not value:
                        res[key] = inherited.get(key)
                    else:
                        inherited_v = inherited.get(key)
                        for k, v in list(value.items()):
                            if k in inherited_v.keys():
                                updated_v = v + inherited_v.get(k)
                                res[key] = updated_v

        ret = {name: res}
        return ret

    def _get_resource_types(self):
        """
        Returns a dictionary where keys are resourceType names, and values
        are ``ResourceType`` objects.
        """
        resource_types = self.raml.get('resourceTypes', [])
        resources = {}
        for r in resource_types:
            for key, value in list(r.items()):
                if 'type' in value.keys():
                    continue
                else:
                    resources[key] = {}
                    for k, v in list(value.items()):
                        if k in HTTP_METHODS:
                            res = ResourceType(key, v, k, self)
                            resources[key][k] = res
        for r in resource_types:
            for key, value in list(r.items()):
                for k, v in list(value.items()):
                    if k == 'type':
                        res = resources.get[v]

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
        trait_params = {}
        for trait in traits:
            for key, value in list(trait.items()):
                trait_params[key] = {}
                items = value.get('queryParameters')
                if items:
                    q_params = []
                    for k, v in list(items.items()):
                        q_params.append(QueryParameter(k, v))
                    trait_params[key]['query_parameters'] = q_params
                # not sure if traits will ever have URI params, but CMA'ing
                items = value.get('uriParameters')
                if items:
                    u_params = []
                    for k, v in list(items.items()):
                        u_params.append(URIParameter(k, v))
                    trait_params[key]['uri_parameters'] = u_params
                items = value.get('formParameters')
                if items:
                    f_params = []
                    for k, v in list(items.items()):
                        f_params.append(FormParameter(k, v))
                    trait_params[key]['form_parameters'] = f_params
                for k, v in list(value.items()):
                    if k not in ['formParameters',
                                 'queryParameters',
                                 'uriParameters']:
                        trait_params[key][k] = v
        return trait_params or None

    def _parse_parameters(self):
        """
        If traits or resourceTypes contain <<parameter>> in definition
        """
        _resources_params = []
        # Default self._resource_types to empty list to get rid of this
        # if-statement.
        # LR: returns None if none define, so will need the if-statement
        if self.resource_types:
            for r in self.resource_types:
                data = json.dumps(r.data)
                match = find_params(data)
                # Not sure about the += here, I would prefer "append".
                _resources_params.extend(match)

        _traits_params = []
        # Same concern as above.
        # LR: returns None if none define, so will need the if-statement
        if self.traits:
            for k, v in list(self.traits.items()):
                data = json.dumps(k)
                match = find_params(data)
                _traits_params.extend(match)

                data = json.dumps(str(v))
                match = find_params(data)
                _traits_params.extend(match)

        # Instead of the list(set) combo just make _traits_params and
        # _resource_params a set initially.
        return dict(resource_types=list(set(_resources_params)),
                    traits=list(set(_traits_params)))

    def get_parameters(self):
        """
        Returns <<parameters>> used in traits and/or resource_types.
        """
        return self._parse_parameters()

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
    def __init__(self, api, raml_file):
        self.api = api
        self.raml = raml_file

    def yield_resources(self):
        """
        Yields Resource objects for the API defined in the RAML File.
        """
        available_methods = ['get', 'post', 'put', 'delete',
                             'patch', 'head', 'options', 'trace',
                             'connect']
        resource_stack = []

        # Akward code, create a helper method for it.
        for k, v in list(self.raml.items()):
            if k.startswith("/"):
                for method in available_methods:
                    if method in self.raml[k].keys():
                        node = Resource(name=k, data=v, method=method,
                                        api=self.api)
                        resource_stack.append(node)

        # Akward code, create a helper method for it.
        while resource_stack:
            current = resource_stack.pop(0)
            yield current
            if current.data:
                for child_k, child_v in list(current.data.items()):
                    if child_k.startswith("/"):
                        for method in available_methods:
                            if method in current.data[child_k].keys():
                                child = Resource(name=child_k, data=child_v,
                                                 method=method, parent=current,
                                                 api=self.api)
                                resource_stack.append(child)


class _BaseResource(object):
    """
    Base class from which Resource and ResourceType to inherit.
    """
    def __init__(self, name, data, method, api, parent=None):
        self.name = name
        self.data = data
        self.api = api
        self.method = method

    @property
    def traits(self):
        """
        Returns a list of traits assigned to the Resource.
        """
        endpoint_traits = self.data.get('is', [])
        method_traits = self.data.get(self.method, {}).get('is', [])
        return endpoint_traits + method_traits or None

    @property
    def headers(self):
        """
        Returns a list of Header objects that the endpoint accepts.

        Returns ``None`` if no headers defined.
        """

        resource_headers = self.data.get('headers', {})
        method_headers = self.data.get(self.method, {}).get('headers', {})
        _headers = dict(resource_headers.items() + method_headers.items())
        headers = []
        for k, v in list(_headers.items()):
            headers.append(Header(k, v, self.method))
        return headers or None

    def _get_body(self):
        bodies = []
        method_body = self.data.get(self.method, {}).get('body', {})
        resource_body = self.data.get('body', {})
        body = dict(resource_body.items() + method_body.items())
        for k, v in list(body.items()):
            bodies.append(Body(k, v))
        return bodies or None

    @property
    def body(self):
        """
        Returns a Body object of a request if defined in RAML, or ``None``
        if not.
        """
        return self._get_body()

    def _get_responses(self):
        resps = []
        resource_headers = self.data.get('responses', {})
        method_responses = self.data.get(self.method, {}).get('responses', {})
        responses = dict(resource_headers.items() + method_responses.items())
        for k, v in list(responses.items()):
            if int(k) in HTTP_RESP_CODES:
                resps.append(Response(k, v, self.method))
            else:
                msg = "{0} not a supported HTTP Response code".format(k)
                raise RAMLParserError(msg)

        return resps

    @property
    def responses(self):
        """
        Returns a list of Response objects of a resource.

        :raises RAMLParserError: Unsupported HTTP Response code
        """
        return self._get_responses()

    def _get_uri_params(self, node, uri_params):
        """Returns a list of URIParameter Objects"""
        # ResourceType does not have `parent` attr so need to check this
        if hasattr(node, 'parent') and node.parent:
            uri_params = self._get_uri_params(node.parent, [])

        for k, v in list(node.data.get('uriParameters', {}).items()):
            uri_params.append((URIParameter(k, v)))

        if self.traits:
            for trait in self.traits:
                params = self.api.traits.get(trait)
                uri_params.extend(
                    [p for p in params if isinstance(p, URIParameter)])

        return uri_params

    @property
    def uri_params(self):
        """
        Returns a list of ``URIParameter`` objects of a ``Resource``, or
        ``None`` if none are defined.
        """
        return self._get_uri_params(self, []) or None

    def _get_base_uri_params(self, node, base_uri_params):
        """
        Returns a list of ``URIParameter`` objects for the ``base_uri``
        """
        if node.parent:
            base_uri_params = self._get_base_uri_params(node.parent, [])
        if 'baseUriParameters' in node.data:
            for k, v in list(node.data['baseUriParameters'].items()):
                base_uri_params.append((URIParameter(k, v)))
        return base_uri_params

    @property
    def base_uri_params(self):
        """
        Returns a list of Base ``URIParameter`` objects of a Resource.
        """
        return self._get_base_uri_params(self, []) or None

    def _get_query_params(self, node):
        resource_params = self.data.get('queryParameters', {})
        method_params = self.data.get(self.method, {}).get('queryParameters', {})
        items = dict(resource_params.items() + method_params.items())

        query_params = []
        for k, v in list(items.items()):
            query_params.append((QueryParameter(k, v)))

        # TODO: Fix/update traits
        # if self.traits:
        #     for trait in self.traits:
        #         params = self.api.traits.get(trait)
        #         query_params.extend(
        #             [p for p in params if isinstance(p, QueryParameter)])
        return query_params

    @property
    def query_params(self):
        """
        Returns a list of ``QueryParameter`` objects, or ``None`` if no
        query parameters are defined.
        """
        return self._get_query_params(self) or None

    def _get_form_params(self, node):
        # TODO: abstract away the body/app/json shiz
        form_params = []
        if self.method in ['post', 'delete', 'put', 'patch']:
            form_headers = ['application/x-www-form-urlencoded',
                            'multipart/form-data']
            for header in form_headers:
                form = node.data.get(self.method, {}).get('body', {}).get(header, {})
                for k, v in list(form.get('formParameters', {}).items()):
                    form_params.append((FormParameter(k, v)))

        if self.traits:
            for trait in self.traits:
                form_params.extend(
                    self.api.traits.get(trait, {}).get('form_parameters', [])
                )
        return form_params or None

    @property
    def form_params(self):
        """
        Returns a list of FormParameter objects, or ``None`` if no form
        parameters are defined.
        """
        # TODO: seems like there isn't a test for this if None?
        return self._get_form_params(self)

    @property
    def req_mime_types(self):
        """
        Returns a list of ``ContentType`` objects that the Resource supports.
        """
        if self.method in ["post", "put", "delete", "patch"]:
            return self.data.get(self.method, {}).get('body', {}).keys() or None
        return None

    @property
    def description(self):
        """
        Returns ``DescriptiveContent`` object with ``raw`` and ``html``
        attributes, or ``None`` if not defined.

        Assumes raw content is written in plain text or Markdown in RAML
        per specification. (Optional)
        """
        method_desc = self.data.get(self.method, {}).get('description')
        resource_desc = self.data.get('description')
        if method_desc:
            return DescriptiveContent(method_desc)
        elif resource_desc:
            return DescriptiveContent(resource_desc)
        return None


class ResourceType(_BaseResource):
    def __init__(self, name, data, method, api, type=None, parent=None):
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
        Returns a string detailing how to use this resource type.
        """
        return self.data.get('usage')

    @property
    def optional(self):
        """
        Returns ``True`` if ``?`` in method, denoting that it is optional.
        """
        return "?" in self.orig_method

    def __repr__(self):
        return "<ResourceType(name='{0}')>".format(self.name)


class Resource(_BaseResource):
    """
    An API's endpoint (resource) defined in RAML, identified by a leading
    slash, ``/``.
    """
    def __init__(self, name, data, method, api, parent=None):
        _BaseResource.__init__(self, name, data, method, api)
        self.parent = parent

    def _get_path_to(self, node):
        parent_path = ''
        if node.parent:
            parent_path = self._get_path_to(node.parent)
        return parent_path + node.name

    @property
    def display_name(self):
        """
        Returns the Resource's display name.

        A friendly name used only for display or documentation purposes.

        If ``displayName`` is not specified in RAML, it defaults to ``name``.
        """
        return self.data.get('displayName', self.name)

    @property
    def path(self):
        """
        Returns string URI path of Resource.

        Not explicitly defined in RAML but inferred based off of
        the Resource ``name``.
        """
        return self._get_path_to(self)

    @property
    def absolute_path(self):
        """
        Return the full API URL for Resource.

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
            string = string.replace("<<" + key + ">>", value)
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
                # tmp = json.dumps(r.data)
                # res_data = self._fill_reserved_params(tmp)
                # data = json.loads(res_data)
                # return ResourceType(r.name, data, self.method, self.api, self.type)

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
                return ResourceType(r.name, data, self.method, self.api, self.type)
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
        Returns a list of resource types assigned to the resource.

        :raises RAMLParserError: Too many resource types applied to one \
        resource.
        :raises RAMLParserError: Resource not defined in the API Root.
        :raises RAMLParserError: If resource type is something other \
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
        return self.data.get('type')

    @property
    def scopes(self):
        """Returns a list of OAuth2 scopes assigned to the resource"""
        if self.secured_by:
            for item in self.secured_by:
                if 'oauth_2_0' == item.get('name'):
                    return item.get('scopes')
        else:
            return None

    @property
    def protocols(self):
        """
        Returns a list of supported protocols for the particular resource.

        Overrides the root API's protocols.  Returns ``None`` if not defined.
        """
        return self.data.get(self.method).get('protocols')

    @property
    def headers(self):
        headers = []
        if self.resource_type:
            headers.extend(self.resource_type.headers or [])
        _headers = super(Resource, self).headers or []
        return headers + _headers or None

    @property
    def responses(self):
        resp = []
        if self.resource_type:
            resp.extend(self.resource_type.responses or [])
        _resp = super(Resource, self).responses or []
        return resp + _resp or None

    @property
    def body(self):
        body = []
        if self.resource_type:
            body.extend(self.resource_type.body or [])
        _body = super(Resource, self).body or []
        return body + _body or None

    @property
    def query_params(self):
        params = []
        if self.resource_type:
            params.extend(self.resource_type.query_params or [])
        _params = super(Resource, self).query_params or []
        return params + _params or None

    @property
    def uri_params(self):
        params = []
        if self.resource_type:
            params.extend(self.resource_type.uri_params or [])
        _params = super(Resource, self).uri_params or []
        return params + _params or None

    @property
    def form_params(self):
        params = []
        if self.resource_type:
            params.extend(self.resource_type.form_params or [])
        _params = super(Resource, self).form_params or []
        return params + _params or None

    @property
    def traits(self):
        traits = []
        if self.resource_type:
            traits.extend(self.resource_type.traits or [])
        _traits = super(Resource, self).traits or []
        return traits + _traits or None

    @property
    def description(self):
        if super(Resource, self).description is not None:
            return super(Resource, self).description
        elif self.resource_type and self.resource_type.description:
            desc = self._fill_reserved_params(self.resource_type.description.raw)
            return DescriptiveContent(desc)
        return None

    def __repr__(self):
        return "<Resource(method='{0}', path='{1}')>".format(
            self.method.upper(), self.path)
