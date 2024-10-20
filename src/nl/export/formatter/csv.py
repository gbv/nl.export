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
import typing
from contextlib import AbstractContextManager
from pathlib import Path
from types import TracebackType
from nl.export.plone import LicenceModel
from nl.export.utils import get_wf_state, option_title, secure_filename

__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


class LFormatCSV(AbstractContextManager):

    def __init__(self, lmodel: LicenceModel, options: any) -> None:
        self.lmodel = lmodel
        self.options = options
        self.destination = self.options.ablage.absolute()

        self.cfh = None
        self.csvpath = None
        self.writer = None

    def add_row(self, licence: dict | None, licencee: dict | None) -> dict:
        licencee = {} if licencee is None else licencee.plone_item

        ipv4_allow = licencee.get("ipv4_allow", "")
        ipv4_deny = licencee.get("ipv4_deny", "")
        ezb_id = licencee.get("ezb_id", "")

        row = {}
        row["user_name"] = licencee.get("uid", "")
        row["status"] = get_wf_state(licencee)
        row["title"] = licencee.get("title", "")
        row["street"] = licencee.get("street", "")
        row["zip"] = licencee.get("zip", "")
        row["city"] = licencee.get("city", "")
        row["county"] = option_title(licencee, "county")
        row["country"] = option_title(licencee, "country")
        row["telephone"] = licencee.get("telephone", "")
        row["fax"] = licencee.get("fax", "")
        row["email"] = licencee.get("email", "")
        row["url"] = licencee.get("url", "")
        row["contactperson"] = licencee.get("contactperson", "")
        row["sigel"] = licencee.get("sigel", "")
        row["ezb_id"] = ",".join(ezb_id) if isinstance(ezb_id, list) else ""
        row["subscriber_group"] = option_title(licencee, "subscriper_group")
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
                                 quotechar='"',
                                 quoting=csv.QUOTE_ALL)
        self.add_row(None, None)

        return super().__enter__()

    def __exit__(self, __exc_type: type[BaseException] | None, __exc_value: BaseException | None, __traceback: TracebackType | None) -> bool | None:
        self.cfh.close()
        return super().__exit__(__exc_type, __exc_value, __traceback)
