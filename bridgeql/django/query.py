# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

from django.db.models import Q

from bridgeql.django.exceptions import InvalidQueryException


class Query(object):

    def __init__(self, query_dict):
        self.query_dict = query_dict
        self.Q = self.construct_query(self.query_dict)

    def construct_query(self, query_dict):
        query = Q()
        if query_dict is None:
            return query
        if not isinstance(query_dict, dict):
            raise InvalidQueryException(
                "Selector is of the type %s, expected dict" % type(query_dict))
        or_filter = query_dict.pop('__or', [])
        if or_filter:
            if not isinstance(or_filter, list):
                raise InvalidQueryException(
                    "__or filter is of the type %s, expected list" % type(or_filter))
            for f in or_filter:
                query.add(self.construct_query(f), conn_type=Q.OR)
        return query & Q(**dict(query_dict))

    @classmethod
    def extract_keys(cls, query_dict):
        exclusion = ('__or',)
        keys = []
        for key, val in query_dict.items():
            if key not in exclusion:
                keys.append(key)
            else:
                for nested_dict in val:
                    keys.extend(Query.extract_keys(nested_dict))
        return keys
