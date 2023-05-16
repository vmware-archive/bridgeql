# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

from django.test import TestCase, override_settings

from bridgeql.django.exceptions import (
    InvalidAppOrModelName,
    InvalidBridgeQLSettings,
    InvalidModelFieldName
)
from bridgeql.django.settings import bridgeql_settings
from bridgeql.django.helpers import get_allowed_apps


class TestSettings(TestCase):

    @override_settings(BRIDGEQL_RESTRICTED_MODELS=['invalid'])
    def test_invalid_restricted_models(self):
        self.assertRaises(InvalidBridgeQLSettings, bridgeql_settings.validate)

    def test_invalid_model(self):
        invalid_models = [
            'invalid_app.invalid_model',
            123,
            'invalid',
            ('invalid_tuple',)
        ]
        for model in invalid_models:
            with self.settings(BRIDGEQL_RESTRICTED_MODELS={
                model: True
            }):
                self.assertRaises(InvalidAppOrModelName,
                                  bridgeql_settings.validate)

    def test_valid_model_invalid_field(self):
        valid_model_invalid_fields = [
            {'machine.Machine': ['os__license_key']},
            {'machine.Machine': ['dns', 'name']},
            {'machine.Machine': 'ip'},
            {
                'machine.OperatingSystem': ['license_key'],
                'machine.Machine': ['ip1'],
            }
        ]
        for model in valid_model_invalid_fields:
            with self.settings(BRIDGEQL_RESTRICTED_MODELS=model):
                self.assertRaises(InvalidModelFieldName,
                                  bridgeql_settings.validate)

    def test_valid_restricted_models(self):
        valid_models = [
            {},  # only dict type allowed
            {'machine.Machine': True},
            {
                'auth.User': True,
                'machine.OperatingSystem': ['license_key'],
                'machine.Machine': ['ip']
            }
        ]
        for model in valid_models:
            with self.settings(BRIDGEQL_RESTRICTED_MODELS=model):
                self.assertTrue(bridgeql_settings.validate())

    def test_invalid_restricted_models_setting(self):
        invalid_settings = [
            None,
            [],
            'strings-not-allowed'
        ]
        for model in invalid_settings:
            with self.settings(BRIDGEQL_RESTRICTED_MODELS=model):
                self.assertRaises(InvalidBridgeQLSettings,
                                  bridgeql_settings.validate)

    @override_settings(BRIDGEQL_AUTHENTICATION_DECORATOR='nopackage.nomodule.nodecorator')
    def test_invalid_auth_decorator(self):
        self.assertRaises(InvalidBridgeQLSettings, bridgeql_settings.validate)

    @override_settings(BRIDGEQL_AUTHENTICATION_DECORATOR={
        'reader': 'server.auth.localtest1',
        'writer': 'server.auth.localtest1'
    })
    def test_valid_module_invalid_auth_decorator(self):
        self.assertRaises(InvalidBridgeQLSettings, bridgeql_settings.validate)

    @override_settings(BRIDGEQL_AUTHENTICATION_DECORATOR={
        'reader': 'server.auth.localtest',
        'writer': 'server.auth.localtest'
    })
    def test_valid_auth_decorator(self):
        self.assertTrue(bridgeql_settings.validate())    \


    @override_settings(BRIDGEQL_AUTHENTICATION_DECORATOR={
        'writer': 'server.auth.localtest'
    })
    def test_valid_writer_auth_decorator(self):
        self.assertTrue(bridgeql_settings.validate())

    def test_list_local_apps(self):
        self.assertListEqual(get_allowed_apps(), ['machine'])
