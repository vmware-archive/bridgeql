# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

import json
import time

from django.http import StreamingHttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views import View

from bridgeql.django.auth import read_auth_decorator, write_auth_decorator
from bridgeql.django.exceptions import BridgeqlException
from bridgeql.django.helpers import JSONResponse, get_json_request_body
from bridgeql.django.models import ModelBuilder, ModelObject
from bridgeql.django.query import Query


@csrf_exempt
@require_http_methods(['POST'])
@write_auth_decorator
def create_django_model(request, db_name, app_label, model_name):
    try:
        params = get_json_request_body(request.body)
        mo = ModelObject(app_label, model_name, db_name)
        obj = mo.create(params)
        msg = 'Added new object of %s with pk=%s' % (
            model_name,
            obj.pk
        )
        res = {'data': obj.id, 'message': msg, 'success': True}
        return JSONResponse(res, status=201)
    except BridgeqlException as e:
        e.log()
        res = {'data': [], 'message': str(e.detail), 'success': False}
        return JSONResponse(res, status=e.status_code)


@method_decorator(require_http_methods(['GET']), name='dispatch')
class StreamView(View):

    def stream_response(self, mb, chunk_size):
        for i, x in enumerate(mb.queryset(stream=True)):
            yield x
            if i % chunk_size == 0:
                time.sleep(1)

    def get(self, request, db_name, app_label, model_name):
        chunk_size = request.GET.get('chunk_size', 1000)
        try:
            chunk_size = int(chunk_size)
        except ValueError:
            chunk_size = 1000
        params = request.GET.get('payload', None)
        try:
            params = json.loads(params)
            mb = ModelBuilder(db_name, app_label, model_name, params)
            return StreamingHttpResponse(self.stream_response(mb, chunk_size), content_type='application/json')
        except BridgeqlException as e:
            e.log()
            res = {'data': [], 'message': str(e.detail), 'success': False}
            return JSONResponse(res, status=e.status_code)

@require_http_methods(['GET'])
@read_auth_decorator
def read_django_model(request, db_name, app_label, model_name, pk=None):
    try:
        if pk:
            params = {
                'filter': {
                    'pk': pk
                }
            }
        else:
            params = request.GET.get('payload', None)
            params = json.loads(params)
        mb = ModelBuilder(db_name, app_label, model_name, params)
        qset = mb.queryset()  # get the result based on the given parameters
        res = {'data': qset, 'message': '', 'success': True}
        return JSONResponse(res)
    except BridgeqlException as e:
        e.log()
        res = {'data': [], 'message': str(e.detail), 'success': False}
        return JSONResponse(res, status=e.status_code)


# no session to ride, hence no need for csrf protection
@csrf_exempt
@require_http_methods(['PATCH'])
@write_auth_decorator
def update_django_model(request, db_name, app_label, model_name, pk):
    try:
        params = get_json_request_body(request.body)
        mo = ModelObject(app_label, model_name, db_name, pk=pk)
        obj = mo.update(params)
        msg = 'Updated %s with pk=%s, fields=%s' % (
            model_name,
            obj.pk,
            ", ".join(params.keys()))
        res = {'data': obj.id, 'message': msg, 'success': True}
        return JSONResponse(res)
    except BridgeqlException as e:
        e.log()
        res = {'data': [], 'message': str(e.detail), 'success': False}
        return JSONResponse(res, status=e.status_code)


@csrf_exempt
@require_http_methods(['DELETE'])
@write_auth_decorator
def delete_django_model(request, db_name, app_label, model_name, pk):
    try:
        mo = ModelObject(app_label, model_name, db_name, pk=pk)
        obj = mo.delete()
        msg = 'Deleted %s with pk=%s' % (model_name, pk)
        res = {'data': obj, 'message': msg, 'success': True}
        return JSONResponse(res)
    except BridgeqlException as e:
        e.log()
        res = {'data': [], 'message': str(e.detail), 'success': False}
        return JSONResponse(res, status=e.status_code)
