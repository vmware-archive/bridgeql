# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

import json
from django.views.decorators.http import require_GET

from bridgeql.django.exceptions import ForbiddenModelOrField, InvalidRequest
from bridgeql.django.helpers import JSONResponse
from bridgeql.django.models import ModelBuilder

# TODO refine error handling


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
        res = {'data': [], 'message': str(e), 'success': False}
        return JSONResponse(res, status=403)
    except InvalidRequest as e:
        res = {'data': [], 'message': str(e), 'success': False}
        return JSONResponse(res, status=400)
    except Exception as e:
        res = {'data': [], 'message': str(e), 'success': False}
        return JSONResponse(res, status=500)

    """
    args = {
        selector: {
            and: [1,2,3],
            or: [1,2,3],
        },
        values: [],
        orderby: [],
        exclude: {
            buildid: 111
        },
        extras: {
            buildtree_url: []
        }
    }
    """
