# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause
import os
from datetime import datetime
import json

from django.apps import apps
from django.conf import settings
from django.db.models.query import QuerySet
from django.http import HttpResponse

from bridgeql.django.exceptions import InvalidRequest
from bridgeql.django.settings import bridgeql_settings


class JSONEncoder(json.JSONEncoder):
    """
    Encode an object in JSON.
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.ctime()
        if hasattr(obj, '__json__'):
            return obj.__json__()
        return json.JSONEncoder.default(self, obj)


class JSONResponse(HttpResponse):
    """
    Create a response that contains a JSON string.
    """

    def __init__(self, content,
                 content_type='application/json; charset=utf-8', status=200,
                 encoder=JSONEncoder):
        if isinstance(content, QuerySet):
            # evaluate the queryset with list(content)
            data = json.dumps(list(content), indent=3, cls=encoder)
        else:
            data = json.dumps(content, indent=3, cls=encoder)
        HttpResponse.__init__(self, data, content_type, status)


def get_local_apps():
    _local_apps = []
    if hasattr(settings, 'BASE_DIR'):
        project_root = os.path.abspath(settings.BASE_DIR)
    elif hasattr(settings, 'SITE_ROOT'):
        project_root = os.path.abspath(settings.SITE_ROOT)
    else:
        return _local_apps

    for app in apps.get_app_configs():
        if os.path.dirname(app.path) == project_root:
            _local_apps.append(app.label)
    return _local_apps


def get_allowed_apps():
    return bridgeql_settings.BRIDGEQL_ALLOWED_APPS or get_local_apps()


def get_json_request_body(body):
    try:
        params = json.loads(body)
        payload = params.get('payload', None)
        if payload is None:
            raise InvalidRequest('payload is not present in request body')
        if not isinstance(payload, dict):
            raise InvalidRequest(
                'Incorrect payload type, Expected dict, got %s' % type(payload))
        return payload
    except ValueError as e:
        raise InvalidRequest(str(e))
