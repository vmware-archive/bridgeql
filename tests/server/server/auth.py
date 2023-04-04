# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

from django.http import HttpResponse

from bridgeql.utils import local_ip_hostname, get_client_ip


def localtest(api):
    def wrap(request, *args, **kwargs):
        ip = get_client_ip(request)
        local_ip, hostname = local_ip_hostname()
        if ip == '127.0.0.1':  # Allowed only for local IP
            print('Request for URL %s succeeded from %s/%s'
                  % (request.path, ip, local_ip))
            return api(request, *args, **kwargs)
        response = HttpResponse(status=401)
        response['WWW-Authenticate'] = 'Unkonwn request source %s' % (ip)
        return response
    return wrap
