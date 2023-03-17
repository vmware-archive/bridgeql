# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand

from machine.models import Machine, OperatingSystem


class Command(BaseCommand):
    help = "Command to populate test data locally."

    def add_arguments(self, parser):
        parser.add_argument('--scale', '-n',
                            dest="scale",
                            default=1,
                            help=('This implies no of records to be created in Machine table'
                                  'Scale 1 means 100 machine and 10 os entries, default : %(default)s.'),
                            type=int,
                            )

    def handle(self, *args, **options):
        scale = options['scale']
        for i in range(10 * scale):
            os = OperatingSystem.objects.create(
                name="os-name-%d" % (i+1),
                arch="arch-name-%d" % (i+1)
            )
        for i in range(100 * scale):
            machine = Machine.objects.create(
                ip="10.0.0.%d" % (i+1),
                name="machine-name-%d" % (i+1),
                cpu_count=((i+1) % 8)*2,
                memory=(i+1)**2,
                created_at=timezone.now() - timedelta(days=99-i),
                powered_on=bool(i % 2),
                os_id=i % (10*scale) + 1
            )
        print("Test data created successfully %d os and %d machine." % (
            OperatingSystem.objects.count(),
            Machine.objects.count()
        ))
