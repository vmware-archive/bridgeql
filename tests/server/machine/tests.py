import base64
import json

from django.urls import reverse
# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

from django.test.client import Client
from django.test.testcases import TestCase
# Create your tests here.


class MachineTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_get_machine(self):
        params = {
            'app_name': 'machine',
            'model_name': 'Machine',
            'filter': {
                'name': 'test-linux-vm'
            },
            'fields': ['ip', 'name', 'created_at']
        }
        params = base64.b64encode(json.dumps(params).encode('utf-8'))
        url = reverse('bridgeql_django_read')
        resp = self.client.get(url, {'payload': params})
        self.assertEqual(resp.status_code, 200)
