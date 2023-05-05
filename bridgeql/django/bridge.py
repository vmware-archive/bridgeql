# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

import json

from django.views.decorators.http import require_GET, require_POST
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from bridgeql.django import logger
from bridgeql.django.auth import auth_decorator
from bridgeql.django.exceptions import (
    ForbiddenModelOrField,
    InvalidRequest
)
from bridgeql.django.helpers import JSONResponse
from bridgeql.django.models import ModelBuilder, ModelObject

# TODO refine error handling


@auth_decorator
@require_GET
def read_django_model(request):
    params = request.GET.get('payload', None)
    try:
        params = json.loads(params)
        mb = ModelBuilder(params)
        qset = mb.queryset()  # get the result based on the given parameters
        res = {'data': qset, 'message': '', 'success': True}
        return JSONResponse(res)
    except ForbiddenModelOrField as e:
        logger.error(e)
        res = {'data': [], 'message': str(e), 'success': False}
        return JSONResponse(res, status=403)
    except InvalidRequest as e:
        logger.error(e)
        res = {'data': [], 'message': str(e), 'success': False}
        return JSONResponse(res, status=400)
    except Exception as e:
        logger.exception(e)
        res = {'data': [], 'message': str(e), 'success': False}
        return JSONResponse(res, status=500)


@auth_decorator
@require_POST
# can use **kwargs
def write_django_model(request, app_label, model_name, **kwargs):
    params = request.POST.get('payload', None)
    try:
        params = json.loads(params)
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
    except ObjectDoesNotExist as e:
        logger.error(e)
        res = {'data': [], 'message': str(e), 'success': False}
        return JSONResponse(res, status=404)
    except ForbiddenModelOrField as e:
        logger.error(e)
        res = {'data': [], 'message': str(e), 'success': False}
        return JSONResponse(res, status=403)
    except (AttributeError, InvalidRequest, ValidationError) as e:
        logger.error(e)
        res = {'data': [], 'message': str(e), 'success': False}
        return JSONResponse(res, status=400)
    except Exception as e:
        logger.exception(e)
        res = {'data': [], 'message': str(e), 'success': False}
        return JSONResponse(res, status=500)