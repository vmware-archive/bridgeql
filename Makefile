# -*- coding: utf-8 -*-
# Copyright © 2023, VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

# Utility Makefile to build, clean and test
PROJECT_ROOT := $(shell pwd)
PY_VERSION := "python3.9"
PY_BINARY := $(shell which $(PY_VERSION))
VENV_DIR := $(PROJECT_ROOT)/venv
PYTHONPATH := $(VENV_DIR)/lib/$(PY_VERSION)/site-packages

default: install

test: install
	@echo "\nRunning the UnitTestCases with coverage enabled"
	@echo "--------------------------------------------------"
	@source env.sh && \
		cd $(PROJECT_ROOT)/tests/server && \
		$(PY_BINARY) manage.py test -v2

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
	@source env.sh && autopep8 --in-place --exclude=venv -r .

clean:
	rm -rf $(VENV_DIR)

.PHONY: clean
