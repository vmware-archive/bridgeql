# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

import json

from django.views.decorators.http import require_http_methods

from bridgeql.django import logger
from bridgeql.django.auth import auth_decorator
from bridgeql.django.exceptions import (
    BridgeqlException
)
from bridgeql.django.helpers import JSONResponse, get_json_request_body
from bridgeql.django.models import ModelBuilder, ModelObject

# TODO refine error handling


@auth_decorator
@require_http_methods(['GET'])
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


@auth_decorator
@require_http_methods(['POST', 'PATCH'])
def write_django_model(request, app_label, model_name, **kwargs):
    try:
        params = get_json_request_body(request.body)
        db_name = params.pop('db_name', None)
        pk = kwargs.pop('pk', None)
        mo = ModelObject(app_label, model_name, db_name=db_name, pk=pk)
        if mo.instance is None:
            obj = mo.create(params)
        else:
            obj = mo.update(params)
        res = {'data': obj.id, 'message': 'Updated fields %s' % (
            ", ".join(params.keys())), 'success': True}
        return JSONResponse(res)
    except BridgeqlException as e:
        e.log()
        res = {'data': [], 'message': str(e.detail), 'success': False}
        return JSONResponse(res, status=e.status_code)
