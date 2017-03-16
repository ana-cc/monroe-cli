from setuptools import setup, find_packages
from codecs import open
from os import path

with open('VERSION') as version_file:
    VERSION = version_file.read().strip()

setup(
    name='monroe-lib',
    version=VERSION,

    description='Python library for interacting with the MONROE scheduler',
    long_description='Library for interacting with the MONROE scheduler',

    url='https://github.com/ana-cc/monroe-lib',

    author='Ana Custura',
    author_email='ana@netstat.org.uk',

    license='BSD 2-clause',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: MONROE Researchers',
        'License :: OSI Approved :: BSD 2-clause License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    packages=find_packages(exclude=['docs', 'tests']),

    entry_points={
    'console_scripts': [
        'monroe=monroe.cli:main',
    ],
},
)
