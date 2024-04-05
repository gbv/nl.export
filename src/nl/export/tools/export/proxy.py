# -*- coding: utf-8 -*-
"""Beschreibung

##############################################################################
#
# Copyright (c) 2024 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

import csv
import logging
import uuid
from argparse import Namespace
from io import StringIO
from nl.export.plone import get_items_found, get_search_results, LicenceModel
from urllib.parse import urlparse

__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


def lmproxy(options: Namespace) -> None:
    logger = logging.getLogger(__name__)

    query = {"fullobjects": "1",
             "portal_type": "NLLicenceModelSingleUser",
             "sort_on": "created",
             "b_size": 10}

    num_found = get_items_found(query)
    logger.info(f"""{num_found} Lizenzmodelle gefunden""")

    fpath = options.csvdatei

    with fpath.open("wt") as csvfh:
        proxywriter = csv.writer(csvfh,
                                 delimiter=';',
                                 quotechar='"',
                                 quoting=csv.QUOTE_ALL)

        proxywriter.writerow(["Titel", "ID", "Produkt-URL",
                              "Zugriffs-URL", "Letzte Änderung"])

        for item in get_search_results(query):
            lmodel = LicenceModel(None, plone_item=item)

            uobj = urlparse(lmodel.plone_item["access_url"])

            if uobj.hostname == "kxp.k10plus.de":
                logger.info((lmodel.getTitle(), "Belser"))
                continue

            logger.info(lmodel.getTitle())
            proxywriter.writerow((lmodel.getTitle(),
                                  str(uuid.UUID(lmodel.plone_item["UID"])),
                                  lmodel.plone_item["@id"],
                                  lmodel.plone_item["access_url"],
                                  lmodel.plone_item["modified"]))
