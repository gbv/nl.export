# -*- coding: utf-8 -*-
"""Beschreibung

##############################################################################
#
# Copyright (c) 2023 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

import logging
from argparse import Namespace


__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


def lizenznehmer(options: Namespace) -> None:
    from nl.export.plone import make_url, get_auth_session, LicenceModel, get_items_found
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
