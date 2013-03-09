#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import socyallib

setup(
    name="socyallib",
    vesion=socyallib.__version__,
    packages=find_packages(),
    author="Martin Trigaux",
    author_email="socyallib@dotzero.me",
    description="Python library to interact with socyal networking websites",
    long_description=open('README.md').read(),
    include_package_data=True,
    url="https://github.com/mart-e/socyallib",
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
        "License :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
    ],
)
