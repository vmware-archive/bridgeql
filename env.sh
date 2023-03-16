#!/bin/sh

# -*- coding: utf-8 -*-
# Copyright © 2023, VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

PROJECT_ROOT=${PWD}
PY_VERSION="python3.9"
PY_BINARY=$(which "${PY_VERSION}")
VENV_DIR=${PROJECT_ROOT}/venv
PYTHONPATH=${VENV_DIR}/lib/${PY_VERSION}/site-packages

export PYTHONPATH=${PYTHONPATH}:${PWD}