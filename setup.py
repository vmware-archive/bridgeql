# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bridgeql",
    version="0.1.7",
    author="Piyus Kumar",
    author_email="piyusk@vmware.com",
    description="Query language to bridge the gap between REST API and ORM capability",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='BSD-2',
    platforms=['Any'],
    keywords=['django'],
    url="https://github.com/vmware/bridgeql",
    project_urls={
        "Bug Tracker": "https://github.com/vmware/bridgeql/issues"
    },
    classifiers={
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: BSD 2 License",
        "Operating System :: OS Independent",
    },
    packages=[
        "bridgeql",
    ],
    python_requires=">=2.7"
)
