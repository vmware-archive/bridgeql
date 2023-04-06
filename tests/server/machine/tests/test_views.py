# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

from django.urls import reverse
from django.test import TestCase
from django.test.client import Client


class TestViews(TestCase):

    def setUp(self):
        self.url = reverse('bridgeql_django_index')
        self.client = Client()

    def test_page_index(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
