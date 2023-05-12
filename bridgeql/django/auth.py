# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

from django.http import HttpResponse
from django.contrib.auth import authenticate

from bridgeql.django.settings import bridgeql_settings
from bridgeql.utils import b64decode, load_function


def basic_auth(api):
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


reader_auth = bridgeql_settings.BRIDGEQL_AUTHENTICATION_DECORATOR.get(
    'reader', None
)
writer_auth = bridgeql_settings.BRIDGEQL_AUTHENTICATION_DECORATOR.get(
    'writer', None
)
if reader_auth:
    read_auth_decorator = load_function(reader_auth)
else:
    def read_auth_decorator(func): return func

if writer_auth:
    write_auth_decorator = load_function(writer_auth)
else:
    def write_auth_decorator(func): return func
