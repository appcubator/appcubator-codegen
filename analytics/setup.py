#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='appcubator-analytics',
    version="0.1.0",
    description="Appcubator Analytics",
    author='Appcubator',
    author_email='team@appcubator.com',
    package_dir={'analytics': 'analytics'},
    include_package_data=True,
    url='https://github.com/appcubator/appcubator-analytics',
    packages=find_packages(),
)
