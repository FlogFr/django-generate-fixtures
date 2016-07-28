# flake8: noqa
from setuptools import (
    setup,
    find_packages,
)

setup(
    name='django-generate-fixtures',
    version='0.1',
    description=''' Easy way to generate fixtures (in json)
    for django following the links of a given object ''',
    author='aRkadeFR',
    author_email='contact@arkade.info',
    url='https://github.com/aRkadeFR/django-generate-fixtures',
    download_url='https://github.com/arkadefr/django-generate-fixtures/tarball/v0.1',
    keywords=['django', 'generate', 'fixtures', 'fixture'],
    packages=find_packages(),
)
