"""Install the openeo jeodpp backend package."""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='openeo-jeodpp-backend',
    version='0.1.0',
    author_email='pieter.kempeneers@ec.europa.eu',
    url='https://jeodpp.jrc.ec.europa.eu/apps/gitlab/jeodpp/openeo/-/tree/master/back_end',
    description='https://jeodpp.jrc.ec.europa.eu/'
	'apps/gitlab/jeodpp/openeo/-/blob/master/back_end/README.md',
    license='Apache',
    packages=setuptools.find_packages(),
    include_package_data=False,
    install_requires=['pyjeo', 'jeolib', 'openeo-pg-parser']
)
