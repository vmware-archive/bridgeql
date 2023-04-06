# -*- coding: utf-8 -*-
# Copyright © 2023 VMware, Inc.  All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause

import os
import re
import setuptools


def read(f):
    return open(f, 'r').read()


def get_version(package):
    init_py = read(os.path.join(package, '__init__.py'))
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


version = get_version('bridgeql')

setuptools.setup(
    name="bridgeql",
    version=version,
    author="Piyus Kumar",
    author_email="piyusk@vmware.com",
    description="Query language to bridge the gap between REST API and ORM capability",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    license='BSD-2',
    platforms=['Any'],
    keywords=['django'],
    url="https://github.com/vmware/bridgeql",
    project_urls={
        "Bug Tracker": "https://github.com/vmware/bridgeql/issues"
    },
    classifiers={
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.1",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
    },
    packages=setuptools.find_packages(exclude=['tests*']),
    package_data={'': ['templates/**/*.html']},
    python_requires=">=2.7"
)
