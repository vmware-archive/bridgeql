# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

import json
from django.views.decorators.http import require_GET

from bridgeql.django import logger
from bridgeql.django.auth import auth_decorator
from bridgeql.django.exceptions import (
    ForbiddenModelOrField,
    InvalidRequest
)
from bridgeql.django.helpers import JSONResponse
from bridgeql.django.models import ModelBuilder

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
