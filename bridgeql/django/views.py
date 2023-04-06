# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

from django.shortcuts import render
from bridgeql import __copyright__, __license__, __title__, __version__


def index(request):
    return render(request, "bridgeql/index.html",
                  {
                      "copyright": __copyright__,
                      "license": __license__,
                      "title": __title__,
                      "version": __version__,
                  }
                  )
