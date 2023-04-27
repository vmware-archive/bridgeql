# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause


class Field(object):
    def __init__(self, model_config, field_name):
        self.model_config = model_config
        self.name = field_name
        self._resolve_pk()

    def _resolve_pk(self):
        if self.name == 'pk':
            self.name = self.model_config.model._meta.pk.name

    @property
    def is_restricted(self):
        return self.name in self.model_config.restricted_fields


class FieldAttributes(object):

    def __init__(self, name, is_null, field_type, help_text):
        self.field_name = name
        self.is_null = is_null
        self.field_type = field_type
        self.help_text = help_text
