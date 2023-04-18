# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause


from collections import defaultdict

from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.contrib.admin.views.decorators import staff_member_required


from bridgeql import __copyright__, __license__, __title__, __version__
from bridgeql.django.auth import auth_decorator
from bridgeql.django.schema import BridgeqlModelFields
from bridgeql.django.models import ModelConfig


def index(request):
    return render(request, "bridgeql/index.html",
                  {
                      "copyright": __copyright__,
                      "license": __license__,
                      "title": __title__,
                      "version": __version__,
                  }
                  )


@staff_member_required
@require_GET
def generate_bridgeql_schema(request):
    model_info = defaultdict(dict)
    local_apps_models = BridgeqlModelFields.get_local_apps_models()
    for app, models in local_apps_models.items():
        model_info[app] = {}
        for model in models:
            _model_config = ModelConfig(app, model)
            _model_name = _model_config.full_model_name
            model_info[app][_model_name] = _model_config.get_fields_attrs()
    return render(request, "bridgeql/schema.html", {"model_info": dict(model_info)})
