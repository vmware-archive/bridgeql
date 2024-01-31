# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause
try:
    from django.urls import re_path as url
except ImportError:
    from django.conf.urls import url

from bridgeql.django import bridge
from bridgeql.django.settings import bridgeql_settings
from bridgeql.django.views import index, generate_bridgeql_schema

bridgeql_settings.validate()

urlpatterns = [
    url(r'^create/(?P<db_name>\w+)/(?P<app_label>\w+)/(?P<model_name>\w+)/$',
        bridge.create_django_model, name='bridgeql_django_create'),
    url(r'^stream/(?P<db_name>\w+)/(?P<app_label>\w+)/(?P<model_name>\w+)/$',
        bridge.StreamView.as_view(), name='bridgeql_django_stream'),
    url(r'^read/(?P<db_name>\w+)/(?P<app_label>\w+)/(?P<model_name>\w+)/(?P<pk>\w+)/$',
        bridge.read_django_model, name='bridgeql_django_read_pk'),
    url(r'^read/(?P<db_name>\w+)/(?P<app_label>\w+)/(?P<model_name>\w+)/$',
        bridge.read_django_model, name='bridgeql_django_read'),
    url(r'^update/(?P<db_name>\w+)/(?P<app_label>\w+)/(?P<model_name>\w+)/(?P<pk>\w+)/$',
        bridge.update_django_model, name='bridgeql_django_update'),
    url(r'^delete/(?P<db_name>\w+)/(?P<app_label>\w+)/(?P<model_name>\w+)/(?P<pk>\w+)/$',
        bridge.delete_django_model, name='bridgeql_django_delete'),
    url(r'^schema/$', generate_bridgeql_schema, name='generate_bridgeql_schema'),
    url(r'', index, name='bridgeql_django_index'),
]
