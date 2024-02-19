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
import json
import logging
import re
import typing
from argparse import Namespace
from contextlib import AbstractContextManager
from lxml import etree
from multiprocessing import Pool
from pathlib import Path
from nl.export.plone import get_items_found, get_auth_session, get_search_results
from nl.export.plone import LicenceModel, Licence, PloneItem
from tqdm import tqdm
from types import TracebackType

__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = 'plaintext'

WF_STATES_CACHE = {}
global PROGRESS


def option_title(val: dict | str, option: str) -> str:
    if isinstance(val, dict):
        val = val.get(option, {})
        if isinstance(val, dict):
            return val.get("title", "")
        return val
    elif isinstance(val, str):
        return val

    return val


def secure_filename(input_str: str) -> str:
    # Replace spaces with underscores
    safe_str = input_str.replace(' ', '_')

    # Remove any characters that are not alphanumeric, underscores, dots, or hyphens
    safe_str = re.sub(r'[^\w.-]', '', safe_str)

    # Limit the length of the filename
    max_length = 255  # Adjust according to the file system's limitations
    safe_str = safe_str[:max_length]

    return safe_str.lower()


def get_wf_state(item: dict) -> str:
    if "@id" not in item:
        return ""

    if item["review_state"] in WF_STATES_CACHE:
        return WF_STATES_CACHE[item["review_state"]]

    session = get_auth_session()
    wfurl = "{}/@workflow".format(item["@id"])

    with session.get(wfurl) as req:
        res = req.json()
        WF_STATES_CACHE[item["review_state"]] = res["state"]["title"]

    return WF_STATES_CACHE[item["review_state"]]


class LFormatCSV(AbstractContextManager):

    def __init__(self, lmodel: LicenceModel, destination: Path) -> None:
        self.lmodel = lmodel
        self.destination = destination.absolute()

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


class LFormatJSON(AbstractContextManager):

    def __init__(self, lmodel: LicenceModel, destination: Path) -> None:
        self.lmodel = lmodel
        self.destination = destination.absolute()

        self.jpath = None

    def add_row(self, licence: dict | None, licencee: dict | None) -> dict:
        fpath = self.jpath / f"{licencee.plone_item['uid']}.json"
        with fpath.open("w") as jfh:
            json.dump(licencee.plone_item, jfh)

    def __enter__(self) -> typing.Any:
        fname = secure_filename(self.lmodel.productTitle())
        self.jpath = self.destination / f"{fname}"
        self.jpath.mkdir(exist_ok=True)

        return super().__enter__()

    def __exit__(self, __exc_type: type[BaseException] | None, __exc_value: BaseException | None, __traceback: TracebackType | None) -> bool | None:
        return super().__exit__(__exc_type, __exc_value, __traceback)


class LFormatXML(AbstractContextManager):

    def __init__(self, lmodel: LicenceModel, destination: Path) -> None:
        self.lmodel = lmodel
        self.destination = destination.absolute()

        self.xmlpath = None
        self.xfh = None
        self.dom = None

    def add_row(self, licence: dict | None, licencee: dict | None) -> None:
        NL_NAMESPACE = "http://www.nationallizenzen.de/ns/nl"
        XNL = "{%s}" % NL_NAMESPACE
        NSMAP = {None: NL_NAMESPACE}

        def cenc(key, data):
            val_node = etree.Element(XNL + key, nsmap=NSMAP)

            if isinstance(data, (list, tuple)):
                for entry in data:
                    token_node = etree.Element(XNL + "token", nsmap=NSMAP)
                    token_node.text = entry

                    val_node.append(token_node)
            elif type(data) is dict:
                pass
            else:
                val_node.text = data

            return val_node

        licencee = {} if licencee is None else licencee.plone_item

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
        row["ezb_id"] = licencee.get("ezb_id", [])
        row["subscriber_group"] = option_title(licencee, "subscriper_group")
        row["ipv4_allow"] = licencee.get("ipv4_allow", [])
        row["ipv4_deny"] = licencee.get("ipv4_deny", [])
        row["shib_provider_id"] = licencee.get("shib_provider_id", "")
        row["zuid"] = licencee.get("UID", "")
        row["mtime"] = licencee.get("modified", "")

        inst_node = etree.Element(XNL + "institution", nsmap=NSMAP)
        self.dom.append(inst_node)

        for key, val in row.items():
            val_node = cenc(key, val)
            inst_node.append(val_node)

    def __enter__(self) -> typing.Any:
        fname = secure_filename(self.lmodel.productTitle())
        self.xmlpath = self.destination / f"{fname}.xml"

        basexml = b"""<?xml version='1.0' encoding='UTF-8'?>"""
        basexml += b"""<nl:institutions xmlns:nl="http://www.nationallizenzen.de/ns/nl"></nl:institutions>"""

        self.dom = etree.fromstring(basexml)

        return super().__enter__()

    def __exit__(self, __exc_type: type[BaseException] | None, __exc_value: BaseException | None, __traceback: TracebackType | None) -> bool | None:
        with self.xmlpath.open("wb") as xfh:
            xfh.write(etree.tostring(self.dom,
                                     xml_declaration=True,
                                     encoding="UTF-8",
                                     method="xml",
                                     pretty_print=True,))

        return super().__exit__(__exc_type, __exc_value, __traceback)


def get_licence_data(lids: dict) -> None:
    """"""
    licence = Licence(lids["licence"], expands=["completerelations"])

    try:
        licencee = PloneItem(
            None, plone_item=licence.plone_item["@components"]["completerelations"]["licencee"])
    except Exception:
        licencee = PloneItem(lids["licencee"])

    return (licence, licencee)


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
        licencemodel = LicenceModel(plone_uid=url)
        licences_ids = []

        query = licencemodel.lic_query

        if options.status is not None:
            query["review_state"] = options.status

        num_found = get_items_found(query)
        ptitle = licencemodel.productTitle()
        print(f"""{ptitle}: {num_found} Lizenz(en) gefunden""")

        if num_found == 0:
            return None

        with formatters[options.format](licencemodel, options.ablage) as formatter:
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
