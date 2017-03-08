#!/usr/bin/env python
import sys

from sbackup.release import __version__, __author__, __author_email__
try:
    from setuptools import setup, find_packages
except ImportError:
    print("sbackup now needs setuptools in order to build. Install it using"
          " your package manager (usually python-setuptools) or via pip (pip"
          " install setuptools).")
    sys.exit(1)


setup(
    version=__version__,
    author=__author__,
    name='sbackup',
    author_email=__author_email__,
    description='Simple backup script',
    packages=["sbackup"],
    install_requires=['click', 'PyYAML', 'boto3'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'sbackup=sbackup.cli:main',
        ],
    }
)
