# -*- coding: utf-8 -*-
# Copyright © 2023, VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

# Utility Makefile to build, clean and test
PROJECT_ROOT := $(shell pwd)
PY_VERSION := "python3.9"
PY_BINARY := $(shell which $(PY_VERSION))
VENV_DIR := $(PROJECT_ROOT)/venv
PYTHONPATH := $(VENV_DIR)/lib/$(PY_VERSION)/site-packages
COVERAGE := $(VENV_DIR)/bin/coverage

default: install

test: install
	@echo "\nRunning the UnitTestCases with coverage enabled"
	@echo "--------------------------------------------------"
	@source env.sh && \
		cd $(PROJECT_ROOT)/tests/server && \
		$(COVERAGE) run --source="../../bridgeql" manage.py test -v2 && \
		$(COVERAGE) report

install: $(VENV_DIR)
	@echo "\nInstalling all required packages"
	@echo "--------------------------------------------------"
	$(VENV_DIR)/bin/pip install -r requirements.txt

$(VENV_DIR):
	@echo "\nRunning dev setup @ $(VENV_DIR) using $(PY_BINARY)"
	@echo "--------------------------------------------------"
	$(PY_BINARY) -m venv  $(VENV_DIR)
	@echo "\nUpgrading pip ..."
	@echo "--------------------------------------------------"
	$(VENV_DIR)/bin/pip install --upgrade pip

autopep8: install
	@echo "\nChecking with python PEP8 compliance"
	@echo "--------------------------------------------------"
	@source env.sh && autopep8 --in-place --exclude=venv,.tox -r .

clean:
	rm -rf $(VENV_DIR)

.PHONY: clean
