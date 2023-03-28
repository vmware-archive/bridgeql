# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

from django.apps import apps
from django.db.models import QuerySet

from bridgeql.django import logger
from bridgeql.django.exceptions import (
    ForbiddenModelOrField,
    InvalidRequest,
    InvalidAppOrModelName,
    InvalidModelFieldName
)
from bridgeql.django.query import construct_query
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


class ModelBuilder(object):
    _QUERYSET_OPTS = [
        ('exclude', 'exclude'),  # dict
        ('distinct', 'distinct'),  # bool
        ('order_by', 'order_by'),  # list
        ('fields', 'values'),  # list
        ('count', 'count'),  # bool
    ]

    def __init__(self, params):
        self.params = Parameters(params)
        self.model = None
        self.qset = None

        self.model = self._get_model()

    def _apply_opts(self):
        for opt, qset_opt in ModelBuilder._QUERYSET_OPTS:
            func = getattr(self.qset, qset_opt)
            value = getattr(self.params, opt, None)
            if not value:
                continue
            if isinstance(value, dict):
                self.qset = func(**value)
            elif isinstance(value, list):
                # handle values case where property is passed in fields
                if qset_opt == 'values' and self.has_properties():
                    # returns DBRows instance
                    self.qset = self._add_fields()
                else:
                    self.qset = func(*value)
            else:
                self.qset = func()

    def _get_model(self):
        app_model_name = '.'.join(
            (self.params.app_name, self.params.model_name))
        if app_model_name in bridgeql_settings.BRIDGEQL_RESTRICTED_MODELS:
            raise ForbiddenModelOrField(
                'Unable to access restricted model %s.' % app_model_name)
        try:
            model = apps.get_model(self.params.app_name,
                                   self.params.model_name)
        except LookupError:
            raise InvalidAppOrModelName(
                'Invalid app or model name %s.' % app_model_name)
        return model

    def has_properties(self):
        # TODO show error if distinct is True and properties are present in fields
        if self.params.distinct:
            return False
        return bool(set(self.params.fields) -
                    set(f.name for f in self.model._meta.fields))

    def _add_fields(self):
        qset_values = DBRows()
        self.print_db_query_log()
        for row in self.qset:
            model_fields = {}
            for field in self.params.fields:
                attr = row
                for ref in field.split('__'):
                    try:
                        attr = getattr(attr, ref)
                    except AttributeError:
                        raise InvalidModelFieldName(
                            'Invalid query for field %s.' % ref)
                model_fields[field] = attr
            qset_values.append(model_fields)
        return qset_values

    def queryset(self):
        # construct Q object from dictionary
        # x = Machine.objects.filter(name__startswith='machine-name-1')
        # x.distinct().order_by('os__name').values('os__name','ip').count()
        query = construct_query(self.params.filter)
        if self.params.db_name:
            self.qset = self.model.objects.using(
                self.params.db_name).filter(query)
        else:
            self.qset = self.model.objects.filter(query)
        self._apply_opts()
        # handle limit and offset seperately
        if self.params.limit:
            self.qset = self.qset[self.params.offset:
                                  self.params.offset + self.params.limit]
        if isinstance(self.qset, QuerySet):
            self.print_db_query_log()
            return list(self.qset)
        return self.qset

    def print_db_query_log(self):
        logger.debug('Request parameters: %s \nQuery: %s',
                     self.params.params, self.qset.query)
