# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

import base64
from datetime import datetime, timedelta
import json
import os

from django.urls import reverse
from django.test.client import Client
from django.test.testcases import TestCase
from django.conf import settings

from machine.models import OperatingSystem, Machine


class MachineTest(TestCase):
    fixtures = [os.path.join(settings.BASE_DIR, 'machine_tests.json'), ]

    def setUp(self):
        self.params = {
            'app_name': 'machine',
            'model_name': 'Machine'
        }
        self.url = reverse('bridgeql_django_read')
        self.client = Client()

    def test_get_machine(self):
        self.params.update({
            'filter': {
                'name': 'machine-name-1'
            },
            'fields': ['ip', 'name', 'created_at']
        })
        resp = self.client.post(self.url, {'payload': json.dumps(self.params)})
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json['data'][0]['ip'], "10.0.0.1")

    def test_exclude_query(self):
        self.params.update({
            'filter': {
                'os__name': 'os-name-1'
            },
            'fields': ['ip'],
            'exclude': {
                'name': 'machine-name-11'
            }
        })
        resp = self.client.post(self.url, {'payload': json.dumps(self.params)})
        self.assertEqual(resp.status_code, 200)
        res_json = resp.json()
        self.assertEqual(9, len(res_json['data']))

    def del_test_distinct_query(self):
        self.params.update({
            'filter': {
                'name__startswith': 'machine-name'
            },
            'fields': ['cpu_count'],
            'distinct': True
        })
        resp = self.client.post(self.url, {'payload': json.dumps(self.params)})
        self.assertEqual(resp.status_code, 200)
        res_json = resp.json()
        self.assertEqual(2, len(res_json['data']))

    def test_count_query(self):
        self.params.update({
            'filter': {
                'os__name': 'os-name-5'
            },
            'count': True
        })
        resp = self.client.post(self.url, {'payload': json.dumps(self.params)})
        self.assertEqual(resp.status_code, 200)
        res_json = resp.json()
        self.assertEqual(10, res_json['data'])

    def test_limit_query(self):
        self.params.update({
            'filter': {
                'name__startswith': 'machine-name-5'
            },
            'order_by': ['name'],
            'fields': ['ip'],
            'limit': 2,
            'offset': 3
        })
        resp = self.client.post(self.url, {'payload': json.dumps(self.params)})
        self.assertEqual(resp.status_code, 200)
        res_json = resp.json()
        result = [
            {'ip': '10.0.0.52'},
            {'ip': '10.0.0.53'},
        ]
        self.assertListEqual(result, res_json['data'])

    # add properties
    def test_get_fields(self):
        self.params.update({
            'filter': {
                'created_at__lte': "2023-03-01"
            },
            'fields': ['id', 'ip', 'created_at']
        })
        resp = self.client.post(self.url, {'payload': json.dumps(self.params)})
        self.assertEqual(resp.status_code, 200)
        res_json = resp.json()
        self.assertEqual(83, len(res_json['data']))

    # add properties
    def test_get_one_field(self):
        self.params.update({
            'filter': {
                'pk': 4,
            },
            'fields': ['os__name']
        })
        resp = self.client.post(self.url, {'payload': json.dumps(self.params)})
        self.assertEqual(resp.status_code, 200)
        res_json = resp.json()
        self.assertEqual(1, len(res_json['data']))

    def test_if_data_loaded(self):
        """
        with --scale set to default 1 we have created
        010 OperatingSystem entries and
        100 Machine entries in DB to make the test fixtures
        This will be used in testing
        machine.name = machine-name-%id
        os.name      = os-name-%id
        """
        self.assertEqual(OperatingSystem.objects.count(), 10)
        self.assertEqual(Machine.objects.count(), 100)
