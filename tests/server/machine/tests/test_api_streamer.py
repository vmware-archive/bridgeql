# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

import json
import os

from django.urls import reverse as url_reverse
from django.test import TestCase, override_settings
from django.test.client import Client
from django.conf import settings

from machine.models import OperatingSystem, Machine


class TestAPIStreamer(TestCase):
    fixtures = [os.path.join(settings.BASE_DIR, 'machine_tests.json'), ]

    def setUp(self):
        self.client = Client()

    def getURL(self, **kwargs):
        db_name = kwargs.get('db_name', 'default')
        app_label = kwargs.get('app_label', 'machine')
        # default model name is Machine
        model_name = kwargs.get('model_name', 'Machine')
        url_name = 'bridgeql_django_read'
        url_kwargs = {
            'db_name': db_name,
            'app_label': app_label,
            'model_name': model_name
        }
        return url_reverse(url_name, kwargs=url_kwargs)

    def test_stream_one_field(self):
        self.params = {
            'filter': {
                'name__startswith': 'machine',
            },
            'fields': ['os__name', 'pk']
        }
        resp = self.client.get(
            self.getURL(), {'payload': json.dumps(self.params), 'stream': True})
        if resp.status_code == 200:
            streaming_content = []
            for chunk in resp.streaming_content:
                streaming_content.append(chunk)
            self.assertEqual(len(streaming_content), 100)

    def test_stream_invalid_model_name(self):
        self.params = {
            'filter': {
                'name__startswith': 'os-name-',
            },
            'fields': ['name', 'arch'],
        }
        resp = self.client.get(self.getURL(model_name='InvalidModel'), {
                               'payload': json.dumps(self.params), 'stream': True})
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(resp.json()['success'])

    def test_stream_invalid_field(self):
        self.params = {
            'filter': {
                'name__startswith': 'machine',
            },
            'fields': ['os1__name', 'pk']
        }
        resp = self.client.get(
            self.getURL(), {'payload': json.dumps(self.params), 'stream': True})
        if resp.status_code == 200:
            streaming_content = b""
            for chunk in resp.streaming_content:
                streaming_content += chunk
            streaming_content = streaming_content.decode('utf-8')
            err_json = json.loads(streaming_content)
            self.assertTrue(err_json['error'])
