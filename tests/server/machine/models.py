# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

from django.db import models


class OperatingSystem(models.Model):
    name = models.CharField(max_length=32)
    arch = models.CharField(max_length=16)

    def __unicode__(self):
        return self.name


class Machine(models.Model):
    ip = models.CharField(max_length=15)
    name = models.CharField(max_length=32)
    cpu_count = models.SmallIntegerField()
    memory = models.IntegerField(help_text='Memory in gigabytes (GB)')
    created_at = models.DateTimeField()
    powered_on = models.BooleanField()
    os = models.ForeignKey(OperatingSystem, on_delete=models.CASCADE)

    @property
    def stats(self):
        return 'CPU: %s, Mem %sGB' % (self.cpu_count, self.memory)

    def __unicode__(self):
        return self.ip
