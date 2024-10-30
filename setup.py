# -*- coding: UTF-8 -*-
"""Beschreibung
##############################################################################
#
# Copyright (c) 2023 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

# Imports
from setuptools import setup, find_packages

__author__ = """Marc-J. Tegethoff <marc.tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


def gc(fname):
    return open(fname).read()


setup(
    name='nl.export',
    version=gc("VERSION.txt"),
    author="Marc-J. Tegethoff",
    author_email="marc.tegethoff@gbv.de",
    description="Einfaches Tool für den Zugriff auf ein NL-CMS",
    long_description=gc("README.md"),
    long_description_content_type="text/markdown",
    keywords="VZG Python Plone Nationallizenzen",
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        'Natural Language :: German',
        'Operating System :: POSIX :: Linux',
        "License :: OSI Approved :: GNU Affero General Public License v3",
    ],
    url='https://github.com/gbv/nl.export',
    project_urls={
        "PyPI": "https://pypi.python.org/pypi/nl.export",
        "Source": "https://github.com/gbv/nl.export",
        "Tracker": "https://github.com/gbv/nl.export/issues",
    },
    packages=find_packages('src'),
    include_package_data=True,
    license="GNU Affero General Public License v3",
    package_dir={'': 'src'},
    namespace_packages=['nl'],
    install_requires=[
        'setuptools',
        'zope.interface',
        'requests',
        "tqdm",
        "lxml"
    ],
    entry_points={'console_scripts': [
        'nl-export = nl.export.tools.export:main'
    ]},
    python_requires=">=3.10",
    zip_safe=False,
)
