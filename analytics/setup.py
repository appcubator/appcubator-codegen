#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys, os
import analytics

setup(
    name='appcubator-analytics',
    version="0.1.0",
    description="Appcubator Analytics",
    author='Nikhil Khadke @ Appcubator',
    author_email='team@appcubator.com',
    package_dir={'analytics': 'analytics'},
    include_package_data=True,
    url='https://github.com/appcubator/appcubator-codegen',
    packages=find_packages(),
)
