"""Install the openeo jeodpp backend package."""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='openeo_jeodpp_backend',
    version='0.1.0',
    author_email='pieter.kempeneers@ec.europa.eu',
    url='https://jeodpp.jrc.ec.europa.eu/apps/gitlab/jeodpp/openeo/-/tree/master/back_end',
    description='https://jeodpp.jrc.ec.europa.eu/'
	'apps/gitlab/jeodpp/openeo/-/blob/master/back_end/README.md',
    license='Apache',
    py_modules = ['openeo_jeodpp_backend'],
    install_requires=['pyjeo', 'jeolib', 'openeo_pg_parser']
)
