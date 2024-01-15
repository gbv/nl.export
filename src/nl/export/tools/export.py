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
from argparse import ArgumentParser, Namespace
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
    cfg.set("plone", "NLACCESS_TOKEN", input("Access Token: ").strip())
    cfg.set("plone", "NLBASE_URL", input("CMS URL: ").strip())

    with cfgpath.open("wt") as cfh:
        cfg.write(cfh)

    msg = f"Konfiguration erstellt ({cfgpath.as_posix()})"
    logger.info(msg)

    return None


def main():
    logger = logging.getLogger()

    usage = "NL Export Tool"

    o_parser = ArgumentParser(description=usage)
    subparsers = o_parser.add_subparsers()

    sub_config = subparsers.add_parser(
        'config', help="Konfiguration erstellen")
    sub_config.set_defaults(func=create_config)

    o_parser.add_argument(
        "-v",
        "--verbose",
        dest='verbose',
        action='store_true',
        default=False,
        help='Mehr Nachrichten')

    options = o_parser.parse_args()

    log_level = logging.WARN

    if options.verbose:
        log_level = logging.INFO

    logging.basicConfig(encoding='utf-8',
                        format="%(levelname)s - %(funcName)s - %(message)s",
                        level=log_level)

    try:
        options.func(options)
    except AttributeError:
        logger.error("", exc_info=True)
        o_parser.print_help()
