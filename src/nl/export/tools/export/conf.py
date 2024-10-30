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


def check_config() -> bool:
    from nl.export.config import NLCONFIG
    cfgpath = Path(NLCONFIG)
    return cfgpath.is_file()


def main(options: Namespace) -> bool | None:
    """"""
    if options.show:
        show_config(options)
        return None

    create_config(options)


def create_config(options: Namespace) -> bool | None:
    """"""
    from nl.export.config import NLCONFIG
    from nl.export.gapi import TerminalColors
    from urllib.parse import urlparse

    logger = logging.getLogger()
    cfgpath = Path(NLCONFIG)

    if options.force is False and cfgpath.is_file():
        msg = "Datei existiert bereits"
        logger.error(msg)
        return None

    cfg = configparser.ConfigParser()

    cfg.add_section("plone")
    cfg.set("plone", "access-token", input("Access Token: ").strip())
    cfg.set("plone", "base-url", input("CMS URL: ").strip())

    if len(cfg.get("plone", "access-token")) == 0:
        print(TerminalColors.bold("\nKein Token gesetzt"))
        return False
    elif len(cfg.get("plone", "base-url")) == 0:
        print(TerminalColors.bold("\nKeine URL gesetzt"))
        return False

    uobj = urlparse(cfg.get("plone", "base-url"))

    if not uobj.scheme or not uobj.hostname:
        print(TerminalColors.bold("\nKeine valide URL gesetzt"))
        return False

    with cfgpath.open("wt") as cfh:
        cfg.write(cfh)

    msg = f"\nKonfiguration erstellt ({cfgpath.as_posix()})"
    logger.info(msg)

    return True


def show_config(options: Namespace) -> bool | None:
    """"""
    from nl.export.config import NLCONFIG
    from nl.export.gapi import TerminalColors

    logger = logging.getLogger()
    cfgpath = Path(NLCONFIG)

    if not cfgpath.is_file():
        msg = "Datei existiert nicht"
        logger.error(msg)
        return None

    print(TerminalColors.bold(f"Konfiguration: {cfgpath.as_posix()}\n"))

    with cfgpath.open() as cfh:
        print(cfh.read())
