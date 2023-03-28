# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

import json
import os

from django.urls import reverse
from django.test.client import Client
from django.test.testcases import TestCase
from django.conf import settings

from machine.models import OperatingSystem, Machine


class TestAPIReader(TestCase):
    fixtures = [os.path.join(settings.BASE_DIR, 'machine_tests.json'), ]

    def setUp(self):
        self.url = reverse('bridgeql_django_read')
        self.client = Client()

    def test_get_machine(self):
        self.params = {
            'app_name': 'machine',
            'model_name': 'Machine',
            'filter': {
                'name': 'machine-name-1'
            },
            'fields': ['ip', 'name', 'created_at']
        }
        resp = self.client.get(self.url, {'payload': json.dumps(self.params)})
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        self.assertEqual(resp_json['data'][0]['ip'], "10.0.0.1")

    def test_or_query(self):
        self.params = {
            'app_name': 'machine',
            'model_name': 'Machine',
            'filter': {
                'os': 1,
                '__or': [
                    {'pk': 1},
                    {'name__startswith': 'machine-name-2'}
                ]
            },
            'fields': ['ip']
        }
        resp = self.client.get(self.url, {'payload': json.dumps(self.params)})
        self.assertEqual(resp.status_code, 200)
        resp_json = resp.json()
        # matching results are machine-name-2, machine-name-1
        self.assertEqual(2, len(resp_json['data']))

    def test_exclude_query(self):
        self.params = {
            'app_name': 'machine',
            'model_name': 'Machine',
            'filter': {
                'os__name': 'os-name-1'
            },
            'fields': ['ip'],
            'exclude': {
                'name': 'machine-name-11'
            }
        }
        resp = self.client.get(self.url, {'payload': json.dumps(self.params)})
        self.assertEqual(resp.status_code, 200)
        res_json = resp.json()
        self.assertEqual(9, len(res_json['data']))

    def test_distinct_query(self):
        self.params = {
            'app_name': 'machine',
            'model_name': 'Machine',
            'filter': {
                'name__startswith': 'machine-name'
            },
            'fields': ['os__name'],
            'distinct': True
        }
        resp = self.client.get(self.url, {'payload': json.dumps(self.params)})
        self.assertEqual(resp.status_code, 200)
        res_json = resp.json()
        self.assertEqual(10, len(res_json['data']))

    def test_count_query(self):
        self.params = {
            'app_name': 'machine',
            'model_name': 'Machine',
            'filter': {
                'os__name': 'os-name-5'
            },
            'count': True
        }
        resp = self.client.get(self.url, {'payload': json.dumps(self.params)})
        self.assertEqual(resp.status_code, 200)
        res_json = resp.json()
        self.assertEqual(10, res_json['data'])

    def test_count_distinct_query(self):
        self.params = {
            'app_name': 'machine',
            'model_name': 'Machine',
            'filter': {
                'name__startswith': 'machine-name'
            },
            'fields': ['cpu_count'],
            'distinct': True,
            'count': True
        }
        resp = self.client.get(self.url, {'payload': json.dumps(self.params)})
        self.assertEqual(resp.status_code, 200)
        res_json = resp.json()
        self.assertEqual(8, res_json['data'])

    def test_limit_query(self):
        self.params = {
            'app_name': 'machine',
            'model_name': 'Machine',
            'filter': {
                'name__startswith': 'machine-name-5'
            },
            'order_by': ['name'],
            'fields': ['ip'],
            'limit': 2,
            'offset': 3
        }
        resp = self.client.get(self.url, {'payload': json.dumps(self.params)})
        self.assertEqual(resp.status_code, 200)
        res_json = resp.json()
        result = [
            {'ip': '10.0.0.52'},
            {'ip': '10.0.0.53'},
        ]
        self.assertListEqual(result, res_json['data'])

    # add properties
    def test_get_fields(self):
        self.params = {
            'app_name': 'machine',
            'model_name': 'Machine',
            'filter': {
                'created_at__lte': "2023-03-01"
            },
            'fields': ['id', 'ip', 'created_at']
        }
        resp = self.client.get(self.url, {'payload': json.dumps(self.params)})
        self.assertEqual(resp.status_code, 200)
        res_json = resp.json()
        self.assertEqual(83, len(res_json['data']))

    # add properties
    def test_get_one_field(self):
        self.params = {
            'app_name': 'machine',
            'model_name': 'Machine',
            'filter': {
                'pk': 4,
            },
            'fields': ['os__name']
        }
        resp = self.client.get(self.url, {'payload': json.dumps(self.params)})
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

    def test_fail_distinct_with_property(self):
        # TODO test should faild if distinct is True and
        # properties are present in fields
        pass

    def test_invalid_field(self):
        self.params = {
            'app_name': 'machine',
            'model_name': 'Machine',
            'filter': {
                'pk': 4,
            },
            'fields': ['invalid']
        }
        resp = self.client.get(self.url, {'payload': json.dumps(self.params)})
        self.assertEqual(resp.status_code, 400)
        resp_json = resp.json()
        self.assertFalse(resp_json['success'])

    def test_restricted_model(self):
        self.params = {
            'app_name': 'auth',
            'model_name': 'User',
            'filter': {
                'username': 'bridgeql',
            },
            'fields': ['username', 'last_login'],
        }
        resp = self.client.get(self.url, {'payload': json.dumps(self.params)})
        self.assertEqual(resp.status_code, 403)
        resp_json = resp.json()
        # print(resp_json['message'])
        self.assertFalse(resp_json['success'])

    def test_restricted_field(self):
        self.params = {
            'app_name': 'machine',
            'model_name': 'OperatingSystem',
            'filter': {
                'name__startswith': 'os-name-',
            },
            'fields': ['name', 'license_key'],
        }
        resp = self.client.get(self.url, {'payload': json.dumps(self.params)})
        self.assertEqual(resp.status_code, 403)
        resp_json = resp.json()
        print(resp_json['message'])
        self.assertFalse(resp_json['success'])

    def test_non_restricted_field(self):
        self.params = {
            'app_name': 'machine',
            'model_name': 'OperatingSystem',
            'filter': {
                'name__startswith': 'os-name-',
            },
            'fields': ['name', 'arch'],
        }
        # resp = self.client.get(self.url, {'payload': json.dumps(self.params)})
        # self.assertEqual(resp.status_code, 200)
        # resp_json = resp.json()
        # self.assertTrue(resp_json['success'])
        pass

    def test_invalid_model_name(self):
        self.params = {
            'app_name': 'machine',
            'model_name': 'InvalidModel',
            'filter': {
                'name__startswith': 'os-name-',
            },
            'fields': ['name', 'arch'],
        }
        resp = self.client.get(self.url, {'payload': json.dumps(self.params)})
        self.assertEqual(resp.status_code, 400)
        resp_json = resp.json()
        self.assertFalse(resp_json['success'])

    def test_invalid_app_name(self):
        self.params = {
            'app_name': 'InvalidApp',
            'model_name': 'Machine',
            'filter': {
                'name__startswith': 'os-name-',
            },
            'fields': ['name', 'arch'],
        }
        resp = self.client.get(self.url, {'payload': json.dumps(self.params)})
        self.assertEqual(resp.status_code, 400)
        resp_json = resp.json()
        self.assertFalse(resp_json['success'])
