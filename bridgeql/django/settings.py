# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

from django.apps import apps
from django.conf import settings

from bridgeql.django.exceptions import InvalidBridgeQLSettings, InvalidAppOrModelName


DEFAULTS = {
    'BRIDGEQL_RESTRICTED_MODELS': None
}


class BridgeQLSettings:
    """
    Used to access bridgeql settings
    """

    def __init__(self):
        self.defaults = DEFAULTS

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid bridgeql setting '%s'" % attr)
        return getattr(settings, attr, self.defaults[attr])

    def validate(self):
        """
        read settings.BRIDGEQL_RESTRICTED_MODELS and validate all models/fields
        BRIDGEQL_RESTRICTED_MODELS = {
            'auth.User': True,
            'machine.OperatingSystem': ['license_key'],
        }
        """
        restricted_models = self.BRIDGEQL_RESTRICTED_MODELS
        # restricted models in None
        if not restricted_models:
            return True

        if not isinstance(restricted_models, dict):
            raise InvalidBridgeQLSettings(
                'BRIDGEQL_RESTRICTED_MODELS requires dict value')

        for restricted_model in restricted_models.keys():
            try:
                app_name, model_name = restricted_model.split('.', 1)
                _ = apps.get_model(app_name, model_name)
            except (ValueError, LookupError, AttributeError):
                raise InvalidAppOrModelName('Invalid model %s in settings.BRIDGEQL_RESTRICTED_MODELS'
                                            % restricted_model)
        return True


bridgeql_settings = BridgeQLSettings()
