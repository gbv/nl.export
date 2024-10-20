# -*- coding: utf-8 -*-
"""Beschreibung

##############################################################################
#
# Copyright (c) 2023-2024 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

from argparse import Namespace
from multiprocessing import Pool
from nl.export.formatter.csv import LFormatCSV
from nl.export.formatter.json import LFormatJSON
from nl.export.formatter.xml import LFormatXML
from nl.export.plone import get_items_found, get_search_results
from nl.export.utils import get_licence_data, get_licencemodel
from tqdm import tqdm
import logging

__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


global PROGRESS


def lizenznehmer(options: Namespace) -> None:
    logger = logging.getLogger(__name__)

    formatters = {"csv": LFormatCSV,
                  "json": LFormatJSON,
                  "xml": LFormatXML}

    if options.format not in formatters:
        msg = "Unbekanntes Format"
        logger.error(msg)
        return None

    for url in options.urls:
        licencemodel = get_licencemodel(url)

        if licencemodel is None:
            continue

        licences_ids = []

        query = licencemodel.lic_query

        if options.status is not None:
            query["review_state"] = options.status

        num_found = get_items_found(query)
        ptitle = licencemodel.productTitle()
        print(f"""{ptitle}: {num_found} Lizenz(en) gefunden""")

        if num_found == 0:
            return None

        with formatters[options.format](licencemodel, options) as formatter:
            print("Lade Lizenzinfo herunter")

            res = list(tqdm(get_search_results(query), total=num_found))
            for licence in res:
                ldict = {"licencee": licence["licencee"]["@id"],
                         "licence": licence["@id"]}
                licences_ids.append(ldict)

            print("Export")
            try:
                with Pool(processes=4) as pool:
                    ldata = list(tqdm(pool.imap(get_licence_data,
                                                licences_ids),
                                      total=num_found))

                for licence, licencee in ldata:
                    formatter.add_row(licence, licencee)
            except Exception:
                logger.error("", exc_info=True)

    return None
