# -*- coding: utf-8 -*-
"""Beschreibung

##############################################################################
#
# Copyright (c) 2024 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

from argparse import Namespace
from contextlib import AbstractContextManager
from nl.export.plone import LicenceModel
from nl.export.utils import get_wf_state, option_title, secure_filename
from types import TracebackType
import csv
import typing

__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


class LFormatCSV(AbstractContextManager):

    def __init__(self, lmodel: LicenceModel, options: Namespace) -> None:
        self.lmodel = lmodel
        self.options = options
        self.destination = self.options.ablage.absolute()

        self.cfh = None
        self.csvpath = None
        self.writer = None

    def add_row(self, licence: dict | None, licencee: dict | None) -> dict:
        match self.options.version:
            case 2:
                self.add_row_version_2(licence, licencee)
            case _:
                self.add_row_version_1(licence, licencee)

    def add_row_version_1(self, licence: dict | None, licencee: dict | None) -> dict:
        licencee = {} if licencee is None else licencee.plone_item

        ipv4_allow = licencee.get("ipv4_allow", "")
        ipv4_deny = None
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

    def add_row_version_2(self, licence: dict | None, licencee: dict | None) -> dict:
        licencee = {} if licencee is None else licencee.plone_item

        ipv4_allow = licencee.get("ipv4_allow", "")
        ipv6 = licencee.get("ipv6", "")
        ezb_id = licencee.get("ezb_id", "")
        foreign_keys = licencee.get("foreign_keys", "")

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
        row["isni"] = licencee.get("isni", "")
        row["foreign_keys"] = ",".join(
            foreign_keys) if isinstance(foreign_keys, list) else ""
        row["subscriber_group"] = option_title(licencee, "subscriper_group")
        row["ipv4_allow"] = ",".join(
            ipv4_allow) if isinstance(ipv4_allow, list) else ""
        row["ipv6"] = ",".join(ipv6) if isinstance(ipv6, list) else ""
        row["shib_provider_id"] = licencee.get("shib_provider_id", "")
        row["zuid"] = licencee.get("UID", "")
        row["mtime"] = licencee.get("modified", "")

        if licence is None:
            self.writer.writerow(row.keys())
        else:
            self.writer.writerow(row.values())

        return row

    def __enter__(self) -> typing.Any:
        fname = secure_filename(self.lmodel.productTitle(), only_ascii=self.options.only_ascii)
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
