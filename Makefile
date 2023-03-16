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
	@echo "Running the UnitTestCases with coverage enabled"
	@echo "--------------------------------------------------"
	@source env.sh && $(PY_BINARY) $(PROJECT_ROOT)/tests/server/manage.py test

install: $(VENV_DIR)
	@echo "Installing all required packages"
	@echo "--------------------------------------------------"
	$(VENV_DIR)/bin/pip install -r requirements.txt

$(VENV_DIR):
	@echo "Running dev setup @ $(VENV_DIR) using $(PY_BINARY)"
	@echo "--------------------------------------------------"
	$(PY_BINARY) -m venv  $(VENV_DIR)
	@echo "Upgrading pip ..."
	@echo "--------------------------------------------------"
	$(VENV_DIR)/bin/pip install --upgrade pip

clean:
	rm -rf $(VENV_DIR)

.PHONY: clean
