# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

from collections import Iterable

from django.apps import apps
from django.conf import settings

from bridgeql.django.exceptions import InvalidBridgeQLSettings, InvalidAppOrModelName, InvalidModelFieldName
from bridgeql.utils import load_function
import os


DEFAULTS = {
    'BRIDGEQL_RESTRICTED_MODELS': {},
    'BRIDGEQL_AUTHENTICATION_DECORATOR': False
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

    def _validate_restricted_models(self):
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

        # validate restricted fields
        for model in restricted_models.keys():
            try:
                app_name, model_name = str(model).split('.', 1)
                model_obj = apps.get_model(app_name, model_name)
                if isinstance(restricted_models[model], (list, tuple)):
                    for field_name in restricted_models[model]:
                        # fail fast in case attribute is not found
                        getattr(model_obj, field_name)
                elif not isinstance(restricted_models[model], bool):
                    raise AttributeError
            except (ValueError, LookupError):
                raise InvalidAppOrModelName('Invalid model %s in settings.BRIDGEQL_RESTRICTED_MODELS'
                                            % model)
            except AttributeError:
                raise InvalidModelFieldName(
                    'Invalid one or more fields %s in settings.BRIDGEQL_RESTRICTED_MODELS.'
                    % restricted_models[model])
        return True

    def _validate_auth_decorator(self):
        # check for the valid auth decorator
        if self.BRIDGEQL_AUTHENTICATION_DECORATOR:
            try:
                load_function(self.BRIDGEQL_AUTHENTICATION_DECORATOR)
            except (AttributeError, ImportError) as e:
                raise InvalidBridgeQLSettings(
                    'Wrong value for settings.BRIDGEQL_AUTHENTICATION_DECORATOR %s'
                    % self.BRIDGEQL_AUTHENTICATION_DECORATOR
                )
        return True

    def validate(self):
        return (
            self._validate_restricted_models() and
            self._validate_auth_decorator()
        )

    def get_local_apps(self):
        local_apps = []
        project_root = os.path.abspath(settings.BASE_DIR)
        for app in apps.get_app_configs():
            if os.path.dirname(app.path) == project_root:
                local_apps.append(app.label)
        return local_apps


bridgeql_settings = BridgeQLSettings()
