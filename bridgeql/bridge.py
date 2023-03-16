# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

import base64
import json
from django.views.decorators.http import require_GET

from bridgeql.exceptions import InvalidQueryException
from bridgeql.helpers import JSONEncoder, JSONResponse
from bridgeql.models import ModelBuilder


@require_GET
def read_django_model(request):
    params = request.GET.get('payload', None)
    try:
        params = json.loads(base64.b64decode(params).decode('utf-8'))
        mb = ModelBuilder(params)
        qset = mb.queryset()  # get the result based on the given parameters
        res = {'content': {'models': list(
            qset)}, 'message': '', 'success': True}
        return JSONResponse(res, content_type='application/json; charset=utf-8', encoder=JSONEncoder)
    except ValueError as e:
        res = {'content': {
        }, 'message': "error while decoding JSON for model %s - %s" % (params['model_name'], e), 'success': False}
        return JSONResponse(res, content_type='application/json; charset=utf-8', encoder=JSONEncoder)
    except InvalidQueryException as e:
        res = {'content': {
        }, 'message': "invalid selector query - %s" % e, 'success': False}
        return JSONResponse(res, content_type='application/json; charset=utf-8', encoder=JSONEncoder)
    except Exception as e:
        res = {'content': {}, 'message': e, 'success': False}
        return JSONResponse(res, content_type='application/json; charset=utf-8', encoder=JSONEncoder)

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
