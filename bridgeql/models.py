# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

from django.apps import apps

from bridgeql.exceptions import BadRequestException
from bridgeql.query import construct_query


class ModelBuilder(object):

    _QUERYSET_OPTS = (
        'filter',
        'exclude',
        'order_by',
        'distinct',
        'count',
    )

    def __init__(self, params):
        self.using = None  # db to connect
        self.app_name = None
        self.model_name = None
        self.filter = None
        self.exclude = None
        self.fields = None
        self.order_by = None
        self.distinct = None
        self.count = None
        self.limit = None
        self.offset = 0  # default offset is 0
        # extra fields required to make queryset
        self.model = None
        self._inject(params)

    def _inject(self, params):
        """
        populate all ModelBuilder object variables and validate it
        """
        for param, value in params.items():
            setattr(self, param, value)
        # validation for required fields
        if not any((self.app_name, self.model_name)):
            raise BadRequestException('app_name or model_name missing')

        self.model = apps.get_model(self.app_name, self.model_name)

    def queryset(self):
        # construct Q object from dictionary
        query = construct_query(self.filter)
        if not self.using:
            model_qset = self.model.objects.filter(query)
        else:
            model_qset = self.model.objects.using(self.using).filter(query)
        return model_qset
