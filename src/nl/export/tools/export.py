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
    cfg.set("plone", "access-token", input("Access Token: ").strip())
    cfg.set("plone", "base-url", input("CMS URL: ").strip())

    with cfgpath.open("wt") as cfh:
        cfg.write(cfh)

    msg = f"Konfiguration erstellt ({cfgpath.as_posix()})"
    logger.info(msg)

    return None


def lmodels(options: Namespace) -> None:
    from nl.export.config import LicenceModels
    from nl.export.errors import NoMember
    from nl.export.plone import make_url, get_auth_session, LicenceModel
    from pprint import pprint
    from urllib.parse import urlparse

    logger = logging.getLogger(__name__)
    session = get_auth_session()

    paths = [urlparse(item).path for item in options.urls]

    search_url = make_url("/@search")

    if len(paths) == 0:
        search_params = {"object_provides": [entry.value for entry in LicenceModels],
                         "review_state": "published"}
    else:
        search_params = {"path": paths}

    search_params["metadata_fields"] = ["UID"]
    search_params["sort_on"] = "sortable_title"

    def search(surl: str, params={}) -> None:
        with session.get(surl, params=params) as req:
            if req.status_code != 200:
                msg = "Keine Lizenz-Modelle gefunden"
                logger.error(msg)
                raise NoMember

            res = req.json()

            for item in res["items"]:
                lmodel = LicenceModel(plone_uid=item["UID"])
                print(lmodel.getTitle())
                if options.verbose:
                    pprint(lmodel.plone_item)

                for licencee in lmodel.licences():
                    print("  {}".format(
                        licencee.plone_item["licencee"]["title"]))

        try:
            search(res["batching"]["next"])
        except KeyError:
            return None

    search(search_url, search_params)


def main():
    logger = logging.getLogger()

    usage = "NL Export Tool"

    o_parser = ArgumentParser(description=usage)
    subparsers = o_parser.add_subparsers()

    sub_config = subparsers.add_parser(
        'config', help="Konfiguration erstellen")
    sub_config.set_defaults(func=create_config)

    sub_lmodels = subparsers.add_parser(
        'lizenzmodelle', help="Lizenzmodelle anzeigen")
    sub_lmodels.add_argument(
        "--lizenznehmer",
        dest='licencee',
        action='store_true',
        default=False,
        help='Lizenznehmer anzeigen')
    sub_lmodels.add_argument('urls',
                             type=str,
                             nargs='*',
                             help='URL(s) von Lizenz-Modellen')
    sub_lmodels.set_defaults(func=lmodels)

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
