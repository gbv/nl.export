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
import logging
import configparser
import os
from enum import Enum
from pathlib import Path

__author__ = """Marc-J. Tegethoff <marc.tegethoff@gbv.de>"""
__docformat__ = 'plaintext'

logger = logging.getLogger(__name__)

NLCONFIG = Path(os.environ['HOME']) / ".nl_export.conf"

NLACCESS_TOKEN = None
NLBASE_URL = None
NLUSER_AGENT = "nl-export-not/1.0"

try:
    config = configparser.ConfigParser()
    config.read(NLCONFIG)

    NLACCESS_TOKEN = config.get("plone", "access-token")
    NLBASE_URL = config.get("plone", "base-url")
except Exception:
    pass


class LicenceModels(Enum):

    NLLicenceModelStandard = "Products.VDNL.content.NLLicenceModelStandard.INLLicenceModelStandard"
    NLLicenceModelOptIn = "Products.VDNL.content.NLLicenceModelOptIn.INLLicenceModelOptIn"
    # NLLicenceModelSingleUser = "Products.VDNL.content.NLLicenceModelSingleUser.INLLicenceModelSingleUser"
