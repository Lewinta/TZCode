# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in tzcode/__init__.py
from tzcode import __version__ as version

setup(
	name='tzcode',
	version=version,
	description='Customization app for TZCode',
	author='Lewin Villar',
	author_email='lewinvillar@tzcode.tech',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
