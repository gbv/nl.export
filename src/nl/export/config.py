# -*- coding: UTF-8 -*-
"""Config
##############################################################################
#
# Copyright (c) 2023 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

# Imports
import configparser
import os
from pathlib import Path

__author__ = """Marc-J. Tegethoff <marc.tegethoff@gbv.de>"""
__docformat__ = 'plaintext'

NLCONFIG = Path(os.environ['HOME']) / ".nl_export.conf"

NLACCESS_TOKEN = None
NLBASE_URL = None

try:
    config = configparser.ConfigParser()
    config.read(NLCONFIG)

    NLACCESS_TOKEN = config.get("plone", "access-token")
    NLBASE_URL = config.get("plone", "base-url")
    NLUSER_AGENT = "nl-export-not/1.0"
except Exception:
    pass
