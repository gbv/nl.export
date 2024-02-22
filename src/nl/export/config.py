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
import shutil

__author__ = """Marc-J. Tegethoff <marc.tegethoff@gbv.de>"""
__docformat__ = 'plaintext'

logger = logging.getLogger(__name__)

_config_path = Path(os.environ['HOME'])

if "XDG_CONFIG_HOME" in os.environ:
    _config_path = _config_path / os.environ["XDG_CONFIG_HOME"]
else:
    _config_path = _config_path / ".config"
    _config_path.mkdir(exist_ok=True)

NLCONFIG = _config_path / "nl_export.conf"
NLCONFIG_Deprecated = ((Path(os.environ['HOME']) / ".nl_export.conf"),
                       (_config_path / ".nl_export.conf"))

for cpath in NLCONFIG_Deprecated:
    if cpath.is_file():
        shutil.move(cpath, NLCONFIG)

NLACCESS_TOKEN = None
NLBASE_URL = None
NLUSER_AGENT = "nl-export-bot/1.0"

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
