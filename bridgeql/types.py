# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause
class DBRows(list):
    # override count method of list
    def count(self):
        return len(self)
