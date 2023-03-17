# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

import base64
import json

from django.urls import reverse
from django.test.client import Client
from django.test.testcases import TestCase

from machine.models import OperatingSystem, Machine


class MachineTest(TestCase):
    fixtures = ['machine_tests.json', ]

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

    def test_if_data_loaded(self):
        """
        with --scale set to default 1 we have created
         10 OperatingSystem entries and
        100 Machine entries in DB to make the test fixtures
        This will be used in testing
        machine.name = machine-name-%id
        os.name      = os-name-%id
        """
        self.assertEqual(OperatingSystem.objects.count(), 10)
        self.assertEqual(Machine.objects.count(), 100)
