# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

from django.db.models import Q

from bridgeql.django.exceptions import InvalidQueryException


def construct_query(selector):
    """
    selector: {
        'pk': 123,
        'type': 'release',
        '__or': [
            {'user': args.user},
            {'email': args.email}
        ]
    }

    selector: {
        '__or': [
            {'pk': 1, 'user': 'John Doe'},
            {'buildtype': 'release'}
        ]
    }
    """
    query = Q()
    if selector is None:
        return query
    if not isinstance(selector, dict):
        raise InvalidQueryException(
            "Selector is of the type %s, expected dict" % type(selector))
    or_filter = selector.pop('__or', [])
    if or_filter:
        if not isinstance(or_filter, list):
            raise InvalidQueryException(
                "__or filter is of the type %s, expected list" % type(or_filter))
        for f in or_filter:
            query.add(construct_query(f), conn_type=Q.OR)
    return query & Q(**dict(selector))
