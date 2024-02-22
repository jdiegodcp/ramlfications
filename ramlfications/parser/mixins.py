# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function


from ramlfications.utils.parser import parse_assigned_dicts


class TraitsMixin(object):
    """
    Mixin to provide methods that parses RAML Trait-related attributes.

    *NOTE:* Mixin assumes that it will be used along with
    :py:class:`.base.BaseNodeParser`
    """
    def __init__(self):
        self.is__ = None

    def is_(self):
        return self.resolve_inherited("is")

    def traits(self):
        if not self.is__:
            return None
        trait_objs = []
        assigned = parse_assigned_dicts(self.is__)
        if not isinstance(assigned, list):
            # I think validate.py would error out so
            # I don't think anything is needed here...
            return None
        for trait in assigned:
            obj = [t for t in self.root.traits if t.name == trait]
            if obj:
                trait_objs.append(obj[0])
        return trait_objs or None


class ResourceTypeMixin(object):
    """
    Mixin to provide methods that parses RAML Resource Type-related attributes.

    *NOTE:* Mixin assumes that it will be used along with
    :py:class:`.base.BaseNodeParser`
    """
    def __init__(self):
        self.type__ = None

    def type_(self):
        return self.resolve_inherited("type")

    def resource_type(self):
        if self.type__ and self.root.resource_types:
            res_types = self.root.resource_types
            assigned = parse_assigned_dicts(self.type__)
            type_obj = [r for r in res_types if r.name == assigned]
            type_obj = [r for r in type_obj if r.method == self.method]
            if type_obj:
                return type_obj[0]


class SecurityMixin(object):
    """
    Mixin to provide methods that parses RAML Security-related attributes.

    *NOTE:* Mixin assumes that it will be used along with
    :py:class:`.base.BaseNodeParser`
    """
    def __init__(self):
        self.secured

    def secured_by(self):
        ret = self.resolve_inherited("securedBy")
        self.secured = ret
        return ret

    def security_schemes(self):
        if not self.secured:
            return None
        assigned_sec_schemes = parse_assigned_dicts(self.secured)
        sec_objs = []
        for sec in assigned_sec_schemes:
            obj = [s for s in self.root.security_schemes if s.name == sec]
            if obj:
                sec_objs.append(obj[0])
        return sec_objs or None


class NodeMixin(TraitsMixin, ResourceTypeMixin, SecurityMixin):
    """
    Helper class to combine the above three defined mixins.

    Only for visual purposes.
    """
