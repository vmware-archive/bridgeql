# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

"""
Everything related to model._meta
"""


def _get_fields(model):
    return set([f.name for f in model._meta.local_fields])


def get_properties(model):
    return set(model._meta._property_names) - {'pk'}
