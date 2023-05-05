# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

import json
import os
from datetime import datetime

from django.urls import reverse
from django.test import TestCase
from django.test.client import Client
from django.conf import settings


class TestAPIWriter(TestCase):
    fixtures = [os.path.join(settings.BASE_DIR, 'machine_tests.json'), ]

    def setUp(self):
        self.client = Client()

    # Test to create a successful machine model
    def test_create_machine(self):
        url = reverse('bridgeql_django_create', kwargs={
            'app_label': 'machine',
            'model_name': 'Machine',
        })
        params = {
            'ip': '10.0.0.211',
            'created_at': datetime.now().isoformat(),
            'cpu_count': 4,
            'memory': 4,
            'powered_on': False,
            'name': 'dummy_machine',
            'os_id': 1
        }
        resp = self.client.post(
            url, {'payload': json.dumps(params)}
        )
        self.assertEqual(resp.status_code, 200)

    # Validation error since NOT NULL fields are not passed
    def test_create_machine_missing_fields(self):
        url = reverse('bridgeql_django_create', kwargs={
            'app_label': 'machine',
            'model_name': 'Machine',
        })
        params = {
            'ip': '10.0.0.211',
        }
        resp = self.client.post(
            url, {'payload': json.dumps(params)}
        )
        self.assertEqual(resp.status_code, 400)

    def test_update_machine(self):
        machine_object_pk = 10
        url = reverse('bridgeql_django_update', kwargs={
            'app_label': 'machine',
            'model_name': 'Machine',
            'pk': machine_object_pk
        })
        params1 = {'ip': '10.0.0.111',
                   'name': 'updated-name-1',  # add datetime later
                   }
        resp = self.client.post(
            url, {'payload': json.dumps(params1)})
        # self.assertEqual(resp.json()['message'], '')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()['success'])
        # test if the machine table with pk updated successfully
        params2 = {
            'app_name': 'machine',
            'model_name': 'Machine',
            'filter': {
                'pk': machine_object_pk,
            },
            'fields': ['ip', 'name']
        }
        url = reverse('bridgeql_django_read')
        resp = self.client.get(url, {'payload': json.dumps(params2)})
        self.assertDictEqual(params1, resp.json()['data'][0])

    def test_update_non_existent_machine(self):
        machine_object_pk = 101
        url = reverse('bridgeql_django_update', kwargs={
            'app_label': 'machine',
            'model_name': 'Machine',
            'pk': machine_object_pk
        })
        params1 = {'ip': '10.0.0.111',
                   'name': 'updated-name-1',
                   }
        resp = self.client.post(
            url, {'payload': json.dumps(params1)})
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json()['message'],
                         'Machine matching query does not exist.')
        self.assertFalse(resp.json()['success'])

    def test_update_readonly_fields(self):
        machine_object_pk = 11
        url = reverse('bridgeql_django_update', kwargs={
            'app_label': 'machine',
            'model_name': 'Machine',
            'pk': machine_object_pk
        })
        params1 = {'ip': '10.0.0.111',
                   'name': 'updated-name-1',
                   'stats': 'updating the new stats'
                   }
        resp = self.client.post(url, {'payload': json.dumps(params1)})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['message'], 'can\'t set attribute')
        self.assertFalse(resp.json()['success'])
