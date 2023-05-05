# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

try:
    from django.urls import path
except ImportError:
    from django.conf.urls import url as path

from bridgeql.django import bridge
from bridgeql.django.settings import bridgeql_settings
from bridgeql.django.views import index, generate_bridgeql_schema

bridgeql_settings.validate()

urlpatterns = [
    path('reader/', bridge.read_django_model, name='bridgeql_django_read'),
    path('writer/(?P<app_label>\w+)/(?P<model_name>\w+)/(?P<pk>\d+)/',
         bridge.write_django_model, name='bridgeql_django_update'),
    path('writer/(?P<app_label>\w+)/(?P<model_name>\w+)/',
         bridge.write_django_model, name='bridgeql_django_create'),
    path('schema/', generate_bridgeql_schema, name='generate_bridgeql_schema'),
    path('', index, name='bridgeql_django_index'),
]
