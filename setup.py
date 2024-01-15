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

setup (
    name='nl.export',
    version=gc("VERSION.txt"),
    author = "Marc-J. Tegethoff",
    author_email = "tegethoff@gbv.de",
    description = "nl.export",
    keywords = "nl",
    classifiers = [
        'Development Status :: 1 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Natural Language :: Deutsch',
        'Operating System :: Linux',],
    url = 'https://info.gbv.de/',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['nl'],
    install_requires = [
        'setuptools',
        'zope.interface',
        'vzg.core'
        ],
    zip_safe = False,
    )