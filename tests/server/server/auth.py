# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

from django.http import HttpResponse


def same_sunbet(api):
    def wrap(request, *args, **kwargs):
        ip = request.META.get('REMOTE_ADDR', '')
        if ip.startswith('10.107'):
            print('Request for URL %s succeeded from %s' % (request.path, ip))
            return api(request, *args, **kwargs)
        response = HttpResponse(status=401)
        response['WWW-Authenticate'] = 'Unkonwn request source %s' % (ip)
        return response
    return wrap
