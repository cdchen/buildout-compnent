#!/usr/bin/env python
# -*- coding: utf-8 -*-

source_dirname = 'src'

requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup_requires = [
    # TODO: put package for setup requirements here
]

dependency_links = [
    # TODO: put package dependency links here
]

import os
import sys

project_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(project_dir, source_dirname))
# os.environ.setdefault('RUN_SETUP', 'True')

import buildout_component

version = getattr(buildout_component, '__version__', '0.1.dev0')

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('ChangeLog.rst') as changelog_file:
    changelog = changelog_file.read().replace('.. :changelog:', '')

with open('requirements.txt') as fp:
    requirements.extend(fp.readlines())

from setuptools import setup, find_packages

setup(
    name='buildout_component',
    version=version,
    description="",
    long_description=readme + '\n\n' + changelog,
    author="niceStuio, Inc.",
    author_email='service@nicestudio.com.tw',
    url='https://www.nicestudio.com.tw/projects/Buildout Component/',
    packages=find_packages(source_dirname, exclude=['docs', 'tests']),
    package_dir={'': source_dirname},
    include_package_data=True,
    install_requires=list(set(requirements)),
    setup_requires=setup_requires,
    dependency_links=dependency_links,
    license="GPL-3.0 License",
    zip_safe=False,
    keywords='buildout_component',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
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
    entry_points={},
)
