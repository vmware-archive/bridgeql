# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

import json

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from bridgeql.django.auth import read_auth_decorator, write_auth_decorator
from bridgeql.django.exceptions import (
    BridgeqlException,
    InvalidRequest
)
from bridgeql.django.helpers import JSONResponse, get_json_request_body
from bridgeql.django.models import ModelBuilder, ModelObject

# TODO refine error handling


@require_http_methods(['GET'])
@read_auth_decorator
def read_django_model(request):
    params = request.GET.get('payload', None)
    try:
        params = json.loads(params)
        mb = ModelBuilder(params)
        qset = mb.queryset()  # get the result based on the given parameters
        res = {'data': qset, 'message': '', 'success': True}
        return JSONResponse(res)
    except BridgeqlException as e:
        e.log()
        res = {'data': [], 'message': str(e.detail), 'success': False}
        return JSONResponse(res, status=e.status_code)


# no session to ride, hence no need for csrf protection
@csrf_exempt
@require_http_methods(['POST', 'PATCH'])
@write_auth_decorator
def write_django_model(request, app_label, model_name, **kwargs):
    try:
        params = get_json_request_body(request.body)
        db_name = params.pop('db_name', None)
        pk = kwargs.pop('pk', None)
        mo = ModelObject(app_label, model_name, db_name=db_name, pk=pk)
        if mo.instance is None and request.method == 'POST':
            obj = mo.create(params)
            msg = 'Added new %s model, pk = %s' % (
                obj._meta.model.__name__,
                obj.pk
            )
        elif mo.instance and request.method == 'PATCH':
            obj = mo.update(params)
            msg = 'Updated fields %s' % ", ".join(params.keys())
        else:
            raise InvalidRequest(
                'Invalid request method %s for the url' % request.method)
        res = {'data': obj.id, 'message': msg, 'success': True}
        return JSONResponse(res)
    except BridgeqlException as e:
        e.log()
        res = {'data': [], 'message': str(e.detail), 'success': False}
        return JSONResponse(res, status=e.status_code)
