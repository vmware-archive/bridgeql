# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

try:
    from django.urls import path
except ImportError:
    from django.conf.urls import url as path

from bridgeql.bridge import read_django_model

urlpatterns = [
    path('dj_read/', read_django_model, name='bridgeql_django_read'),
]
