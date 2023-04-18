# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

from django.apps import apps
from django.core.exceptions import FieldDoesNotExist
from django.db.models import QuerySet
from django.db.models.base import ModelBase

from bridgeql.django import logger
from bridgeql.django.exceptions import (
    ForbiddenModelOrField,
    InvalidRequest,
    InvalidAppOrModelName,
    InvalidModelFieldName,
    InvalidQueryException,
)
from bridgeql.django.query import construct_query, extract_keys
from bridgeql.django.settings import bridgeql_settings


class Parameters(object):
    def __init__(self, params):
        self.params = params
        self.db_name = None  # db to connect
        self.app_name = None
        self.model_name = None
        self.filter = {}
        self.exclude = {}
        self.fields = []
        self.order_by = []
        self.distinct = False
        self.count = False
        self.limit = None
        self.offset = 0  # default offset is 0
        self._inject_params()

    def _inject_params(self):
        """
        populate all ModelBuilder object variables and validate it
        """
        for param, value in self.params.items():
            setattr(self, param, value)
        # validation for required fields
        if not any((self.app_name, self.model_name)):
            raise InvalidRequest('app_name or model_name missing')


class DBRows(list):
    # override count method of list
    def count(self):
        return len(self)


class Field(object):
    def __init__(self, model_config, field_name):
        self.model_config = model_config
        self.name = field_name
        self._resolve_pk()

    def _resolve_pk(self):
        if self.name == 'pk':
            self.name = self.model_config.model._meta.pk.name

    @property
    def is_restricted(self):
        return (self.name in self.model_config.restricted_fields)


class FieldAttributes(object):

    def __init__(self, name, is_null, field_type, help_text):
        self.field_name = name
        self.is_null = is_null
        self.field_type = field_type
        self.help_text = help_text


class ModelConfig(object):
    def __init__(self, app_name, model_name):
        self.app_name = app_name
        self.model_name = model_name
        self.restricted_fields = self._get_restricted_fields()
        self.model = self._get_model()  # restricted_fields list to set
        self.fields = self._get_fields()
        self.fields_attrs = {}

    def get_fields_attrs(self):
        _restricted_fields = self._get_restricted_fields()
        for field in self.model._meta.local_fields:
            if field.name not in _restricted_fields:
                self.fields_attrs[field.name] = FieldAttributes(
                    field.name, field.null, field.get_internal_type(), field.help_text)

        for _property in self.get_properties():
            if _property not in _restricted_fields:
                self.fields_attrs[_property] = FieldAttributes(
                    _property, None, "ReadOnly Propery", None)
        return self.fields_attrs

    def _get_fields(self):
        return set([f.name for f in self.model._meta.local_fields])

    def get_properties(self):
        return set(self.model._meta._property_names) - {'pk'}

    def _get_restricted_fields(self):
        # get from settings
        restricted_fields = bridgeql_settings.BRIDGEQL_RESTRICTED_MODELS.get(
            self.full_model_name, [])
        if isinstance(restricted_fields, list):
            restricted_fields = set(restricted_fields)
        return restricted_fields

    def _get_model(self):
        if self.full_model_name in bridgeql_settings.BRIDGEQL_RESTRICTED_MODELS:
            if self.restricted_fields is True:
                raise ForbiddenModelOrField(
                    'Unable to access restricted model %s.' % self.full_model_name)
        try:
            model = apps.get_model(self.app_name,
                                   self.model_name)
        except LookupError:
            raise InvalidAppOrModelName(
                'Invalid app or model name %s.' % self.full_model_name)
        return model

    @property
    def full_model_name(self):
        return "%s.%s" % (
            self.app_name,
            self.model_name
        )

    def validate_fields(self, query_fields):
        # combination of all fields used in query
        for q_field in query_fields:
            parent = self
            for field in q_field.split('__'):
                field_obj = Field(parent, field)
                if field_obj.is_restricted:
                    raise ForbiddenModelOrField('%s is restricted for model %s' %
                                                (field_obj.name, parent.full_model_name))
                try:
                    attr = parent.model._meta.get_field(
                        field_obj.name).related_model
                    if isinstance(attr, ModelBase):
                        parent = ModelConfig(
                            attr._meta.app_label, attr._meta.object_name)
                    else:
                        break
                except FieldDoesNotExist:
                    if hasattr(parent.model, field_obj.name):
                        prop_obj = Field(parent, field_obj.name)
                        if prop_obj.is_restricted:
                            raise ForbiddenModelOrField('%s is restricted for model %s' %
                                                        (prop_obj.name, parent.full_model_name))
        return True


class ModelBuilder(object):
    _QUERYSET_OPTS = [
        ('exclude', 'exclude', dict),  # dict
        ('distinct', 'distinct', bool),  # bool
        ('order_by', 'order_by', list),  # list
        ('fields', 'values', list),  # list
        ('count', 'count', bool),  # bool
    ]

    def __init__(self, params):
        self.params = Parameters(params)
        self.qset = None

        self.model_config = ModelConfig(
            self.params.app_name, self.params.model_name)
        requested_fields = list()
        requested_fields.extend(extract_keys(self.params.filter))
        requested_fields.extend(extract_keys(self.params.exclude))
        requested_fields.extend(self.params.fields)
        requested_fields.extend(self.params.order_by)
        self.model_config.validate_fields(set(requested_fields))

    def _apply_opts(self):
        for opt, qset_opt, opt_type in ModelBuilder._QUERYSET_OPTS:
            func = getattr(self.qset, qset_opt)
            value = getattr(self.params, opt, None)
            if not value:
                continue
            if not isinstance(value, opt_type):
                raise InvalidQueryException('Invalid type %s for %s'
                                            % (type(value), value))
            if isinstance(value, dict):
                self.qset = func(**value)
            elif isinstance(value, list):
                # handle values case where property is passed in fields
                if qset_opt == 'values' and self.query_has_properties():
                    # returns DBRows instance
                    self.qset = self._add_fields()
                else:
                    self.qset = func(*value)
            elif value:
                self.qset = func()

    def query_has_properties(self):
        # TODO show error if distinct is True and properties are present in fields
        if self.params.distinct:
            return False
        return bool(set(self.params.fields) - self.model_config.fields)

    def _add_fields(self):
        qset_values = DBRows()
        self.qset = self.qset.select_related()
        logger.debug('Request parameters: %s \nQuery: %s\n',
                     self.params.params, self.qset.query)
        for row in self.qset:
            model_fields = {}
            for field in self.params.fields:
                attr = row
                for ref in field.split('__'):
                    try:
                        attr = getattr(attr, ref)
                        if attr is None:
                            break
                    except AttributeError:
                        raise InvalidModelFieldName(
                            'Invalid query for field %s in %s.' % (ref, attr))
                model_fields[field] = attr
            qset_values.append(model_fields)
        return qset_values

    def queryset(self):
        # construct Q object from dictionary
        # x = Machine.objects.filter(name__startswith='machine-name-1')
        # x.distinct().order_by('os__name').values('os__name','ip').count()
        query = construct_query(self.params.filter)
        if self.params.db_name:
            self.qset = self.model_config.model.objects.using(
                self.params.db_name).filter(query)
        else:
            self.qset = self.model_config.model.objects.filter(query)
        self._apply_opts()
        # handle limit and offset separately
        if self.params.limit:
            self.qset = self.qset[self.params.offset:
                                  self.params.offset + self.params.limit]
        if isinstance(self.qset, QuerySet):
            logger.debug('Request parameters: %s \nQuery: %s\n',
                         self.params.params, self.qset.query)
            return list(self.qset)
        return self.qset


# query -> normal fields, foreign key reference
