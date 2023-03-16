# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

from datetime import datetime
import json

from django.http import HttpResponse
from django.db.models.query import QuerySet


class JSONEncoder(json.JSONEncoder):
    '''
    Encode an object in JSON.
    '''

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.ctime()
        if hasattr(obj, '__json__'):
            return obj.__json__()
        return json.JSONEncoder.default(self, obj)


class JSONResponse(HttpResponse):
    '''
    Create a response that contains a JSON string.
    '''

    def __init__(self, content,
                 content_type='application/json; charset=utf-8', status=200,
                 encoder=JSONEncoder):
        if isinstance(content, QuerySet):
            # evaluate the queryset with list(content)
            data = json.dumps(list(content), indent=3, cls=encoder)
        else:
            data = json.dumps(content, indent=3, cls=encoder)
        HttpResponse.__init__(self, data, content_type, status)
