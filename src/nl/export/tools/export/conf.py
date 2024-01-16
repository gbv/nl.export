# -*- coding: utf-8 -*-
"""Beschreibung

##############################################################################
#
# Copyright (c) 2023 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

import configparser
import logging
from argparse import Namespace
from pathlib import Path


__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


def create_config(options: Namespace) -> None:
    """"""
    from nl.export.config import NLCONFIG

    logger = logging.getLogger()
    cfgpath = Path(NLCONFIG)

    if cfgpath.is_file():
        msg = "Datei existiert bereits"
        logger.error(msg)
        return None

    cfg = configparser.ConfigParser()

    cfg.add_section("plone")
    cfg.set("plone", "access-token", input("Access Token: ").strip())
    cfg.set("plone", "base-url", input("CMS URL: ").strip())

    with cfgpath.open("wt") as cfh:
        cfg.write(cfh)

    msg = f"Konfiguration erstellt ({cfgpath.as_posix()})"
    logger.info(msg)

    return None
