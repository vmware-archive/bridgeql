# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

from django.http import HttpResponseBadRequest


class BadRequestException(HttpResponseBadRequest):
    pass


class InvalidQueryException(Exception):
    pass
