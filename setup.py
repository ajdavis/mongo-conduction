#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.rst') as changelog_file:
    changelog = changelog_file.read().replace('.. :changelog:', '')

requirements = ['bottle', 'pymongo', 'mockupdb', 'mongo-orchestration']
dependency_links = [
    'git+git://github.com/ajdavis/mongo-mockup-db#egg=mockupdb',
]

test_requirements = []

if sys.version_info[:2] == (2, 6):
    requirements.extend(['argparse', 'simplejson'])
    test_requirements.append('unittest2')

setup(
    name='mongo-conduction',
    version='0.1.0',
    description="Wire Protocol frontend server to Mongo Orchestration.",
    long_description=readme + '\n\n' + changelog,
    author="A. Jesse Jiryu Davis",
    author_email='jesse@mongodb.com',
    url='https://github.com/ajdavis/mongo-conduction',
    packages=['conduction'],
    package_dir={'conduction': 'conduction'},
    include_package_data=True,
    install_requires=requirements,
    dependency_links=dependency_links,
    license="Apache License, Version 2.0",
    zip_safe=False,
    keywords='mongo-conduction',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        "License :: OSI Approved :: Apache Software License",
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    entry_points={
        'console_scripts': [
            'mongo-conduction = conduction.server:main'
        ]
    },
)
