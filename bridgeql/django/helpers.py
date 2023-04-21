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


from bridgeql.django.exceptions import InvalidBridgeQLSettings

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


def get_local_apps():
    if hasattr(settings, 'BASE_DIR'):
        project_root = os.path.abspath(settings.BASE_DIR)
    elif hasattr(settings, 'SITE_ROOT'):
        project_root = os.path.abspath(settings.SITE_ROOT)
    else:
        project_root = None

    if not project_root:
        raise InvalidBridgeQLSettings(
                'Could not find BASE_DIR and SITE_ROOT \
                BRIDGEQL_ALLOWED_APPS needs to be initilised in settings')
    _local_apps = []
    for app in apps.get_app_configs():
        if os.path.dirname(app.path) == project_root:
            _local_apps.append(app.label)
    return _local_apps


def get_allowed_apps():
    if hasattr(settings, 'BRIDGEQL_ALLOWED_APPS'):
        return settings.BRIDGEQL_ALLOWED_APPS or get_local_apps()
    raise InvalidBridgeQLSettings(
            'BRIDGEQL_ALLOWED_APPS needs to be initilised in settings')

