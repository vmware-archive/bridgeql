# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

from django.apps import apps
from django.core.exceptions import FieldDoesNotExist, FieldError
from django.db.models import QuerySet
from django.db.models.base import ModelBase

from bridgeql.types import DBRows
from bridgeql.django import logger
from bridgeql.django.exceptions import (
    ForbiddenModelOrField,
    InvalidRequest,
    InvalidAppOrModelName,
    InvalidModelFieldName,
    InvalidQueryException,
)
from bridgeql.django.fields import Field, FieldAttributes
from bridgeql.django.query import Query
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
                    _property, None, "ReadOnly Property", None)
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
        ('exclude', 'exclude', dict),
        ('distinct', 'distinct', bool),
        ('order_by', 'order_by', list),
        ('offset', 'offset', int),
        ('limit', 'limit', int),
        ('fields', 'values', list),
        ('count', 'count', bool),
    ]

    def __init__(self, params):
        self.params = Parameters(params)
        self.qset = None

        self.model_config = ModelConfig(
            self.params.app_name, self.params.model_name)
        requested_fields = list()
        requested_fields.extend(Query.extract_keys(self.params.filter))
        requested_fields.extend(Query.extract_keys(self.params.exclude))
        requested_fields.extend(self.params.fields)
        requested_fields.extend(self.params.order_by)
        self.model_config.validate_fields(set(requested_fields))

    def _apply_opts(self):
        for opt, qset_opt, opt_type in ModelBuilder._QUERYSET_OPTS:
            # offset and limit operation will return None
            func = getattr(self.qset, qset_opt, None)
            value = getattr(self.params, opt, None)
            # do not execute operation if value is not passed
            # or it does not have default value specified in
            # Parameters class such as [], {}, False
            if value is None:
                continue
            if not isinstance(value, opt_type):
                raise InvalidQueryException('Invalid type %s for %s'
                                            ' expected %s'
                                            % (type(value), opt, opt_type))
            if isinstance(value, dict):
                self.qset = func(**value)
            elif qset_opt == 'offset':
                self.qset = self.qset[self.params.offset:]
            elif qset_opt == 'limit':
                self.qset = self.qset[:self.params.limit]
            elif isinstance(value, list):
                # handle values case separately
                if qset_opt == 'values':
                    # list of parameters passed in values function
                    values_params = set(value) - \
                        self.model_config.get_properties()
                    # list of properties handled separately
                    properties = set(value) - values_params
                    try:
                        # qset.values(*fields) is called but not yet evaluated
                        qset_values = func(*values_params)
                    except FieldError as e:
                        raise InvalidModelFieldName(str(e))
                    if self.query_has_properties():
                        # queryset evaluated
                        qset_values = self._add_properties(
                            qset_values, properties)
                    self.qset = qset_values
                else:
                    try:
                        self.qset = func(*value)
                    except FieldError as e:
                        raise InvalidModelFieldName(str(e))
            elif isinstance(value, bool) and value:
                self.qset = func()

    def query_has_properties(self):
        # TODO show error if distinct is True and properties are present in fields
        if self.params.distinct:
            return False
        return bool(set(self.params.fields).intersection(self.model_config.get_properties()))

    def _add_properties(self, db_rows, query_properties):
        # evaluate queryset values
        db_rows = list(db_rows)
        qset_values = DBRows()
        # skipping select_related call, expecting
        # properties will not have references call
        # like machine.os.arch in any of the machine's property
        logger.debug('Request parameters: %s \nQuery (2nd call): %s\n',
                     self.params.params, self.qset.query)
        for i, row in enumerate(self.qset):
            for field in query_properties:
                try:
                    model_property = getattr(row, field)
                except AttributeError:
                    raise InvalidModelFieldName(
                        'Query field "%s" does not exists.' % field)
                db_rows[i][field] = model_property
            qset_values.append(db_rows[i])
        return qset_values

    def queryset(self):
        # construct Q object from dictionary
        query = Query(self.params.filter)
        if self.params.db_name:
            self.qset = self.model_config.model.objects.using(
                self.params.db_name).filter(query.Q)
        else:
            self.qset = self.model_config.model.objects.filter(query.Q)
        self._apply_opts()
        if isinstance(self.qset, QuerySet):
            logger.debug('Request parameters: %s \nQuery: %s\n',
                         self.params.params, self.qset.query)
            return list(self.qset)
        return self.qset
