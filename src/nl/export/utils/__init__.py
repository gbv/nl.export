# -*- coding: utf-8 -*-
"""Beschreibung

##############################################################################
#
# Copyright (c) 2024 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

from nl.export.plone import get_auth_session
import re
from urllib.parse import urlparse, urlunparse
from nl.export.plone import LicenceModel, Licence, PloneItem
from nl.export.config import LicenceModels, NLBASE_URL
import uuid
from nl.export.plone import get_items_found, get_search_results

__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = 'plaintext'

WF_STATES_CACHE = {}


def option_title(val: dict | str, option: str) -> str:
    if isinstance(val, dict):
        val = val.get(option, {})
        if isinstance(val, dict):
            return val.get("title", "")
        return val
    elif isinstance(val, str):
        return val

    return val


def secure_filename(input_str: str, only_ascii=False) -> str:
    # Replace spaces with underscores
    safe_str = input_str.replace(' ', '_')

    # Remove any characters that are not alphanumeric, underscores, dots, or hyphens
    if only_ascii:
        safe_str = re.sub(r'[^\w.-]', '', safe_str, flags=re.ASCII)
    else:
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


def get_licence_data(lids: dict) -> None:
    """"""
    licence = Licence(lids["licence"], expands=["licenceerelation"])

    try:
        licencee = PloneItem(
            None, plone_item=licence.plone_item["@components"]["licenceerelation"])
    except Exception:
        licencee = PloneItem(lids["licencee"])

    return (licence, licencee)


def get_licencemodel(lurl: str) -> LicenceModel | None:
    """Lizenz-Modell bestimmen

    Args:
        lurl (str): URL

    Returns:
        LicenceModel: Lizenz-Modell
    """
    def is_uuid(entry: str) -> bool:
        try:
            uuid.UUID(entry)
        except ValueError:
            return False

        return True

    valid_types = ["NLProduct"] + [entry.name for entry in list(LicenceModels)]

    if is_uuid(lurl):
        lmodel = PloneItem(plone_uid=uuid.UUID(lurl).hex)
    else:
        urlobj = urlparse(lurl)
        baseurl = urlparse(NLBASE_URL)

        if not bool(urlobj.hostname):
            # Wahrscheinlich getId
            query = {"portal_type": valid_types, "getId": urlobj.path}
            if bool(get_items_found(query)):
                urlobj = urlparse(list(get_search_results(query))[0]["@id"])

        if urlobj.hostname != baseurl.hostname:
            print(f"Unbekannter Host: {urlobj.hostname}")
            return None

        lmodel = PloneItem(plone_uid=urlunparse(urlobj))

    if "@type" not in lmodel.plone_item:
        print(f"Objekt nicht vorhanden: {lurl}")
        return None

    if lmodel.plone_item["@type"] not in valid_types:
        print(f"Unbekannter Typ: {lmodel.plone_item['@type']}")
        return None

    match lmodel.plone_item["@type"]:
        case "NLProduct":
            _lmodels = [entry for entry in lmodel.plone_item["items"]
                        if entry["@type"] == LicenceModels.NLLicenceModelStandard.name]

            if bool(len(_lmodels)):
                lmodel = LicenceModel(plone_uid=_lmodels[0]["@id"])
            else:
                lmodel = None
        case LicenceModels.NLLicenceModelStandard.name:
            lmodel = LicenceModel("", plone_item=lmodel.plone_item)
        case LicenceModels.NLLicenceModelOptIn.name:
            lmodel = LicenceModel("", plone_item=lmodel.plone_item)
        case _:
            lmodel = None

    return lmodel
