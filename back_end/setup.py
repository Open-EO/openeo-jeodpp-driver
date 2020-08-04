"""Install the openeo jeodpp backend package."""

import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


from setuptools import find_packages


setup(
    name='openeo-jeodpp_backend',
    version='0.1.0',
    author_email='pieter.kempeneers@ec.europa.eu',
    url='https://jeodpp.jrc.ec.europa.eu/apps/gitlab/jeodpp/openeo/-/tree/master/back_end',
    description='https://jeodpp.jrc.ec.europa.eu/'
	'apps/gitlab/jeodpp/openeo/-/blob/master/back_end/README.md',
    license='GPLv3',
    packages=find_packages(),
    include_package_data=False,
    install_requires=['pyjeo']
)
