# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

from bridgeql.django import logger


class BridgeqlException(Exception):
    status_code = 500
    default_detail = 'A server error occurred.'

    def __init__(self, detail=None):
        self.detail = detail
        if self.detail is None:
            self.detail = self.default_detail

    def __str__(self):
        return str(self.detail)

    def log(self):
        if self.status_code >= 500:
            logger.exception(self)
        else:
            logger.error(self)


class ForbiddenModelOrField(BridgeqlException):
    status_code = 403
    default_detail = 'Unauthorized access to forbidden ' \
                     'model or field'


class InvalidRequest(BridgeqlException):
    status_code = 400
    default_detail = 'Invalid request received'


class InvalidAppOrModelName(InvalidRequest):
    pass


class InvalidModelFieldName(InvalidRequest):
    pass


class InvalidQueryException(InvalidRequest):
    pass


class InvalidPKException(InvalidRequest):
    pass


class InvalidBridgeQLSettings(BridgeqlException):
    pass


class ObjectNotFound(BridgeqlException):
    status_code = 404
    default_detail = 'Object not found'
