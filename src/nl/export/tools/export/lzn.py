# -*- coding: utf-8 -*-
"""Beschreibung

##############################################################################
#
# Copyright (c) 2023 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

import csv
import logging
import re
from types import TracebackType
import typing
from argparse import Namespace
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Any
from nl.export.plone import get_items_found, get_auth_session
from nl.export.plone import LicenceModel, PloneItem
from pprint import pprint
from tqdm import tqdm

__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


def secure_filename(input_str: str) -> str:
    # Replace spaces with underscores
    safe_str = input_str.replace(' ', '_')

    # Remove any characters that are not alphanumeric, underscores, dots, or hyphens
    safe_str = re.sub(r'[^\w.-]', '', safe_str)

    # Limit the length of the filename
    max_length = 255  # Adjust according to the file system's limitations
    safe_str = safe_str[:max_length]

    return safe_str.lower()


class LFormatCSV(AbstractContextManager):

    def __init__(self, lmodel: LicenceModel, destination: Path) -> None:
        self.lmodel = lmodel
        self.destination = destination.absolute()

        self.cfh = None
        self.csvpath = None
        self.writer = None

    def add_row(self, licence: dict | None, licencee: dict | None) -> dict:
        licencee = {} if licencee is None else licencee.plone_item
        licence_ = {} if licence is None else licence.plone_item

        ipv4_allow = licencee.get("ipv4_allow", "")
        ipv4_deny = licencee.get("ipv4_deny", "")
        ezb_id = licencee.get("ezb_id", "")

        row = {}
        row["user_name"] = licencee.get("uid", "")
        row["status"] = licencee.get("review_state", "")
        row["title"] = licencee.get("title", "")
        row["street"] = licencee.get("street", "")
        row["zip"] = licencee.get("zip", "")
        row["city"] = licencee.get("city", "")
        row["county"] = licencee.get("county", {}).get("title", "")
        row["country"] = licencee.get("country", {}).get("title", "")
        row["telephone"] = licencee.get("telephone", "")
        row["fax"] = licencee.get("fax", "")
        row["email"] = licencee.get("email", "")
        row["url"] = licencee.get("url", "")
        row["contactperson"] = licencee.get("contactperson", "")
        row["sigel"] = licencee.get("sigel", "")
        row["ezb_id"] = ",".join(ezb_id) if isinstance(ezb_id, list) else ""
        row["subscriber_group"] = licencee.get(
            "subscriper_group", {}).get("title", "")
        row["ipv4_allow"] = ",".join(
            ipv4_allow) if isinstance(ipv4_allow, list) else ""
        row["ipv4_deny"] = ",".join(
            ipv4_deny) if isinstance(ipv4_deny, list) else ""
        row["shib_provider_id"] = licencee.get("shib_provider_id", "")
        row["zuid"] = licencee.get("UID", "")
        row["mtime"] = licencee.get("modified", "")

        if licence is None:
            self.writer.writerow(row.keys())
        else:
            self.writer.writerow(row.values())

        return row

    def __enter__(self) -> typing.Any:
        fname = secure_filename(self.lmodel.productTitle())
        self.csvpath = self.destination / f"{fname}.csv"
        self.cfh = self.csvpath.open("w")
        self.writer = csv.writer(self.cfh,
                                 delimiter=';',
                                 dialect="excel",
                                 quotechar='"',
                                 quoting=csv.QUOTE_ALL)
        self.add_row(None, None)

        return super().__enter__()

    def __exit__(self, __exc_type: type[BaseException] | None, __exc_value: BaseException | None, __traceback: TracebackType | None) -> bool | None:
        self.cfh.close()
        return super().__exit__(__exc_type, __exc_value, __traceback)


def lizenznehmer(options: Namespace) -> None:
    logger = logging.getLogger(__name__)
    session = get_auth_session()

    formatters = {"csv": LFormatCSV}

    if options.format not in formatters:
        msg = "Unbekanntes Format"
        logger.error(msg)
        return None

    for url in options.urls:
        licencemodel = LicenceModel(plone_uid=url)

        query = licencemodel.lic_query

        if options.status is not None:
            query["review_state"] = options.status

        num_found = get_items_found(query)

        print(f"{licencemodel.productTitle()}: {
              num_found} Lizenz(en) gefunden")

        progress = tqdm(total=num_found)

        try:
            with formatters[options.format](licencemodel, options.ablage) as formatter:
                for licence in licencemodel.licences(review_state=options.status):
                    licencee = PloneItem(licence.plone_item["licencee"]["@id"])
                    formatter.add_row(licence, licencee)
                    progress.update(1)
        except Exception:
            logger.error("", exc_info=True)
        finally:
            progress.close()

    return None
