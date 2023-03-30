# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause


class InvalidQueryException(Exception):
    pass


class ForbiddenModelOrField(Exception):
    pass


class InvalidRequest(Exception):
    pass


class InvalidAppOrModelName(InvalidRequest):
    pass


class InvalidModelFieldName(InvalidRequest):
    pass


class InvalidBridgeQLSettings(Exception):
    pass
