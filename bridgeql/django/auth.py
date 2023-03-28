# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

import importlib

from django.http import HttpResponse
from django.contrib.auth import authenticate

from bridgeql.django.settings import bridgeql_settings
from bridgeql.utils import b64decode, load_function


def simple_auth(api):
    def wrap(request, *args, **kwargs):
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        if auth and len(auth.split()) == 2:
            if auth[0].lower() == "basic":
                uname, passwd = b64decode(auth[1]).split(':', 1)
                user = authenticate(username=uname, password=passwd)
                if user is not None and user.is_active:
                    request.user = user
                    return api(request, *args, **kwargs)
        response = HttpResponse(status=401)
        response['WWW-Authenticate'] = 'Basic base64(user:password)'
        return response
    return wrap


if bridgeql_settings.BRIDGEQL_AUTHENTICATION_DECORATOR is False:
    def auth_decorator(func): return func
elif bridgeql_settings.BRIDGEQL_AUTHENTICATION_DECORATOR:
    auth_decorator = load_function(
        bridgeql_settings.BRIDGEQL_AUTHENTICATION_DECORATOR)
else:
    auth_decorator = simple_auth
