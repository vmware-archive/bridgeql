# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from django.test.client import Client


class TestViews(TestCase):

    def setUp(self):
        self.client = Client()

    def test_page_index(self):
        _url = reverse('bridgeql_django_index')
        resp = self.client.get(_url)
        self.assertEqual(resp.status_code, 200)

    def test_page_schema_should_fail(self):
        testuser_without_staff = User.objects.create(
            username='testuser_without_staff')
        testuser_without_staff.set_password('password')
        testuser_without_staff.save()
        _url = reverse('generate_bridgeql_schema')
        self.client.login(username="testuser_without_staff",
                          password="password")
        resp = self.client.get(_url)
        self.assertEqual(resp.status_code, 302)

    def test_page_schema_should_pass(self):
        testuser_with_staff = User.objects.create(
            username='testuser_with_staff')
        testuser_with_staff.set_password('password')
        testuser_with_staff.is_staff = True
        testuser_with_staff.save()
        _url = reverse('generate_bridgeql_schema')
        self.client.login(username="testuser_with_staff", password="password")
        resp = self.client.get(_url)
        self.assertEqual(resp.status_code, 200)
