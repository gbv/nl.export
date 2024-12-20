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
from lxml import etree
from nl.export.plone import LicenceModel
from nl.export.utils import get_wf_state, option_title, secure_filename
from types import TracebackType
import typing

__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


class LFormatXML(AbstractContextManager):

    def __init__(self, lmodel: LicenceModel, options: Namespace) -> None:
        self.lmodel = lmodel
        self.options = options
        self.destination = self.options.ablage.absolute()

        self.xmlpath = None
        self.xfh = None
        self.dom = None

    def add_row(self, licence: dict | None, licencee: dict | None) -> None:
        match self.options.version:
            case 2:
                self.add_row_version_2(licence, licencee)
            case _:
                self.add_row_version_1(licence, licencee)

    def add_row_version_1(self, licence: dict | None, licencee: dict | None) -> None:
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
        row["ipv4_deny"] = []
        row["shib_provider_id"] = licencee.get("shib_provider_id", "")
        row["uid"] = licencee.get("UID", "")
        row["mtime"] = licencee.get("modified", "")

        inst_node = etree.Element(XNL + "institution", nsmap=NSMAP)
        self.dom.append(inst_node)

        for key, val in row.items():
            val_node = cenc(key, val)
            inst_node.append(val_node)

    def add_row_version_2(self, licence: dict | None, licencee: dict | None) -> None:
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
        row["foreign_keys"] = licencee.get("foreign_keys", [])
        row["isni"] = licencee.get("isni", [])
        row["subscriber_group"] = option_title(licencee, "subscriper_group")
        row["ipv4_allow"] = licencee.get("ipv4_allow", [])
        row["ipv6"] = licencee.get("ipv6", [])
        row["shib_provider_id"] = licencee.get("shib_provider_id", "")
        row["uid"] = licencee.get("UID", "")
        row["mtime"] = licencee.get("modified", "")

        inst_node = etree.Element(XNL + "institution", nsmap=NSMAP)
        self.dom.append(inst_node)

        for key, val in row.items():
            val_node = cenc(key, val)
            inst_node.append(val_node)

    def __enter__(self) -> typing.Any:
        fname = secure_filename(self.lmodel.productTitle(), only_ascii=self.options.only_ascii)
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
