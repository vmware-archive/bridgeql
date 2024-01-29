# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

from django.apps import apps
from django.core.exceptions import (
    FieldDoesNotExist,
    FieldError,
    ValidationError,
    ObjectDoesNotExist
)
from django.db.models import QuerySet, aggregates
from django.db.models.base import ModelBase
from django.db.utils import IntegrityError
try:
    from django.utils.connection import ConnectionDoesNotExist
except ImportError:
    from django.db.utils import ConnectionDoesNotExist

from bridgeql.django import logger
from bridgeql.django.exceptions import (
    ForbiddenModelOrField,
    InvalidRequest,
    InvalidAppOrModelName,
    InvalidModelFieldName,
    InvalidQueryException,
    InvalidPKException,
    ObjectNotFound
)
from bridgeql.django.fields import Field, FieldAttributes
from bridgeql.django.query import Query
from bridgeql.django.settings import bridgeql_settings
from bridgeql.types import DBRows


class Parameters(object):
    def __init__(self, **kwargs):
        self.params = kwargs.get('params')
        self.db_name = kwargs.get('db_name')  # db to connect
        self.app_name = kwargs.get('app_name')
        self.model_name = kwargs.get('model_name')
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

    @property
    def fk_refs_in_fields(self):
        refs = []
        for field in self.fields:
            if '__' in field:
                refs.append(field.rsplit('__', 1)[0])
        return refs


class ModelConfig(object):
    def __init__(self, app_name, model_name):
        self.app_name = app_name
        self.model_name = model_name
        self.restricted_fields = self._get_restricted_fields()
        self.model = self._get_model()  # restricted_fields list to set
        self.fields = self.get_fields()
        self.fields_attrs = {}

    def get_fields(self):
        return set([f.name for f in self.model._meta.local_fields])

    def get_properties(self):
        return set(self.model._meta._property_names) - {'pk'}

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


class ModelObject(object):
    def __init__(self, app_label, model_name, db_name, pk=None):
        self.db_name = db_name
        self.model_config = ModelConfig(app_label, model_name)
        self.instance = None
        if pk:
            obj_manager = self.model_config.model.objects.using(self.db_name)
            # throw error if more than one value found
            try:
                self.instance = obj_manager.get(pk=pk)
            except ValueError as e:
                raise InvalidPKException(str(e))
            except ObjectDoesNotExist as e:
                raise ObjectNotFound(str(e))
            except ConnectionDoesNotExist as e:
                raise InvalidRequest(str(e))

    def update(self, params):
        # TODO check if there are any restricted fields in data
        try:
            for key, val in params.items():
                if hasattr(self.instance, key):
                    setattr(self.instance, key, val)
                else:
                    raise InvalidRequest('%s does not have field %s'
                                         % (self.instance._meta.model.__name__,
                                            key))
            # Perform validation
            self.instance.validate_unique()
            self.instance.save()
        except (AttributeError, IntegrityError,
                ValidationError, ValueError) as e:
            raise InvalidRequest(str(e))
        return self.instance

    def create(self, params):
        # TODO validate data
        save_kwargs = {'using': self.db_name}
        # if db_name is None then save() function will use default db
        self.instance = self.model_config.model(**params)
        # Perform validation
        try:
            self.instance.validate_unique()
            self.instance.save(**save_kwargs)
        except (IntegrityError, ValidationError, ValueError) as e:
            raise InvalidRequest(str(e))
        return self.instance

    def delete(self):
        return self.instance.delete()


class ModelBuilder(object):
    _QUERYSET_OPTS = [
        ('exclude', 'exclude', dict),
        ('distinct', 'distinct', bool),
        ('order_by', 'order_by', list),
        ('offset', 'offset', int),
        ('limit', 'limit', int),
        ('aggregate', 'aggregate', dict),
        ('fields', 'values', list),
        ('count', 'count', bool),
    ]

    def __init__(self, db_name, app_name, model_name, params):
        kwargs = {
            'db_name': db_name,
            'app_name': app_name,
            'model_name': model_name,
            'params': params
        }
        self.params = Parameters(**kwargs)
        self.qset = None

        self.model_config = ModelConfig(
            self.params.app_name, self.params.model_name)
        requested_fields = list()
        requested_fields.extend(Query.extract_keys(self.params.filter))
        requested_fields.extend(Query.extract_keys(self.params.exclude))
        requested_fields.extend(self.params.fields)
        requested_fields.extend(self.params.order_by)
        self.model_config.validate_fields(set(requested_fields))

    def _apply_opts(self, stream=False):
        for opt, qset_opt, opt_type in ModelBuilder._QUERYSET_OPTS:
            # offset and limit operation will return None
            func = getattr(self.qset, qset_opt, None)
            value = getattr(self.params, opt, None)
            # do not execute operation (except values)
            # if value is not passed,
            # or it does not have default value specified in
            # Parameters class such as [], {}, False
            if not value and qset_opt != 'values':
                continue
            if not isinstance(value, opt_type):
                raise InvalidQueryException('Invalid type %s for %s'
                                            ' expected %s'
                                            % (type(value), opt, opt_type))
            if isinstance(value, dict):
                if qset_opt == 'aggregate':
                    aggr_arg = []
                    for aggr_opt, aggr_field in value.items():
                        aggr_func = getattr(aggregates, aggr_opt, None)
                        if aggr_func is None:
                            raise InvalidRequest('Invalid aggregate function %s' %
                                                 aggr_opt)
                        aggr_func_f = aggr_func(aggr_field)
                        aggr_arg.append(aggr_func_f)
                        self.qset = func(*aggr_arg)
                    # stop all operations after aggregate
                    break
                else:
                    self.qset = func(**value)
            elif qset_opt == 'offset':
                self.qset = self.qset[self.params.offset:]
            elif qset_opt == 'limit':
                self.qset = self.qset[:self.params.limit]
            elif isinstance(value, list):
                # handle values case where property is passed in fields
                if qset_opt == 'values' and stream:
                    return self.yield_fields()
                elif qset_opt == 'values' and self.query_has_properties():
                    # returns DBRows instance
                    self.qset = self._add_fields()
                else:
                    # in case if fields is not present in the query
                    # return all fields but restricted
                    if not value:
                        value = list(
                            self.model_config.fields - self.model_config.restricted_fields)
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
        return bool(set(self.params.fields).intersection(
            self.model_config.get_properties()))

    def _add_fields(self):
        qset_values = DBRows()
        self.qset = self.qset.select_related(*self.params.fk_refs_in_fields)
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

    def yield_fields(self):
        logger.debug('Request parameters: %s \nQuery: %s\n',
                     self.params.params, self.qset.query)
        self.qset = self.qset.select_related(*self.params.fk_refs_in_fields)
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
            yield model_fields

    def queryset(self, stream=False):
        # construct Q object from dictionary
        query = Query(self.params.filter)
        if self.params.db_name:
            self.qset = self.model_config.model.objects.using(
                self.params.db_name).filter(query.Q)
        else:
            self.qset = self.model_config.model.objects.filter(query.Q)
        if stream:
            return self._apply_opts(stream=stream)
        self._apply_opts()
        if isinstance(self.qset, QuerySet):
            logger.debug('Request parameters: %s \nQuery: %s\n',
                         self.params.params, self.qset.query)
            return list(self.qset)
        return self.qset
