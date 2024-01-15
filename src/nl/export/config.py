# -*- coding: UTF-8 -*-
"""Config
##############################################################################
#
# Copyright (c) 2019 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

# Imports
from six.moves import configparser
from vzg.core.config import get_config_path2

__author__ = """Marc-J. Tegethoff <marc.tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


VCONFIG = get_config_path2( "nl-export.conf" )
config = configparser.ConfigParser()

config.read( VCONFIG )

