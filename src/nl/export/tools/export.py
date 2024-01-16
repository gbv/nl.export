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
import gettext
import logging
# from argparse import Namespace
from pathlib import Path

__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


def get_items_found(query: dict) -> int:
    from nl.export.plone import make_url, get_auth_session

    session = get_auth_session()
    search_url = make_url("/@search")

    num_found = 0

    with session.get(search_url, params=query) as req:
        if req.status_code == 200:
            res = req.json()
            num_found = res.get("items_total", 0)

    return num_found


def create_config(options) -> None:
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


def lizenznehmer(options) -> None:
    from nl.export.errors import NoMember
    from nl.export.plone import make_url, get_auth_session, LicenceModel
    from pprint import pprint

    logger = logging.getLogger(__name__)
    session = get_auth_session()

    for url in options.urls:
        licencemodel = LicenceModel(plone_uid=url)

        query = licencemodel.lic_query

        if options.status is not None:
            query["review_state"] = options.status

        num_found = get_items_found(query)

        print(f"{licencemodel.productTitle()}: {
              num_found} Lizenz(en) gefunden")

        for licencee in licencemodel.licences(review_state=options.status):
            print("  {}".format(
                licencee.plone_item["licencee"]["title"]))

    return None


def main():
    def translate(Text):
        Text = Text.replace("usage:", "Verwendung")
        Text = Text.replace("show this help message and exit",
                            "zeige diese Hilfe an und tue nichts weiteres")
        Text = Text.replace("error:", "Fehler:")
        Text = Text.replace("the following arguments are required:",
                            "Die folgenden Argumente müssen angegeben werden:")
        Text = Text.replace("positional arguments",
                            "Kommandos")
        Text = Text.replace("options",
                            "Optionen")
        return Text

    gettext.gettext = translate

    import argparse

    logger = logging.getLogger()

    usage = "NL Export Tool"

    o_parser = argparse.ArgumentParser(description=usage)
    subparsers = o_parser.add_subparsers()

    sub_config = subparsers.add_parser(
        'config', help="Konfiguration erstellen")
    sub_config.set_defaults(func=create_config)

    sub_licencees = subparsers.add_parser(
        'lzn', help="Lizenznehmer")
    sub_licencees.add_argument('--format',
                               nargs="?",
                               type=str,
                               help="""Ausgabeformat (csv|xml|json). Standard ist %(default)s)""",
                               metavar="Format",
                               default="csv")
    sub_licencees.add_argument('--status',
                               type=str,
                               help="Status der Lizenz(en). Mehrfachnennung möglich",
                               action='append',
                               metavar="Status")
    sub_licencees.add_argument('urls',
                               type=str,
                               nargs='+',
                               help='URL(s) von Lizenz-Modellen')
    sub_licencees.set_defaults(func=lizenznehmer)

    o_parser.add_argument(
        "-v",
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
