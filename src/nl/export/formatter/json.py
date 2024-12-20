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
from nl.export.utils import secure_filename
from types import TracebackType
import json
import typing

__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


class LFormatJSON(AbstractContextManager):

    def __init__(self, lmodel: LicenceModel, options: Namespace) -> None:
        self.lmodel = lmodel
        self.options = options
        self.destination = self.options.ablage.absolute()

        self.jpath = None

    def add_row(self, licence: dict | None, licencee: dict | None) -> dict:
        fpath = self.jpath / f"{licencee.plone_item['uid']}.json"
        with fpath.open("w") as jfh:
            json.dump(licencee.plone_item, jfh)

    def __enter__(self) -> typing.Any:
        fname = secure_filename(self.lmodel.productTitle(), only_ascii=self.options.only_ascii)
        self.jpath = self.destination / f"{fname}"
        self.jpath.mkdir(exist_ok=True)

        return super().__enter__()

    def __exit__(self, __exc_type: type[BaseException] | None, __exc_value: BaseException | None, __traceback: TracebackType | None) -> bool | None:
        return super().__exit__(__exc_type, __exc_value, __traceback)
