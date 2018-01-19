from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='bank_server',
    version='1.0.0',
    description='',
    long_description=long_description,
    url='',
    python_requires='<3',
    packages=find_packages('bank_server', exclude=['contrib', 'docs', 'tests']),

    install_requires=['pyyaml','pyserial'],
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': ['check-manifest'],
        'test': ['nose'],
    },
    test_suite='nose.collector',

    tests_require=['nose'],

    #scripts=['scripts/create_card','scripts/create_hsm'],

    entry_points={
        'console_scripts': [
            'bank_server=bank_server:main'
        ],
    },
)
