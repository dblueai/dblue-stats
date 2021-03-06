#!/usr/bin/env python

import os
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand


def version():
    project_root = os.path.abspath(os.path.dirname(__file__))

    version_file = os.path.join(project_root, "dblue_stats", "configs", "version.txt")

    with open(version_file, 'r') as f:
        return f.read().strip()


def requirements():
    with open('requirements/requirements-base.txt') as f:
        return f.readlines()


def read_readme():
    with open('README.md') as f:
        return f.read()


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []  # pylint: disable=attribute-defined-outside-init
        self.test_suite = True  # pylint: disable=attribute-defined-outside-init

    def run_tests(self):
        import pytest  # pylint: disable=import-outside-toplevel
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


PACKAGE_NAME = 'dblue-stats'
PACKAGE_VERSION = version()

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    description="Dblue's stats library for generating baseline statistics of ML features",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    maintainer='Rajesh Hegde',
    maintainer_email='rh@dblue.ai',
    author='Rajesh Hegde',
    author_email='rh@dblue.ai',
    url='https://github.com/dblueai/dblue-stats',
    license='Apache2',
    platforms='any',
    packages=find_packages(),
    package_dir={'dblue_stats': 'dblue_stats'},
    package_data={
        'dblue_stats': ['configs/*.yaml', 'configs/*.txt']
    },
    keywords=[
        'dblue',
        'machine-learning',
        'drift',
        'monitoring',
        'mlwatch',
        'statistics'

    ],
    install_requires=requirements(),
    extras_require={},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence'
    ],
    tests_require=[
        "pytest",
    ],
    cmdclass={'test': PyTest}
)
