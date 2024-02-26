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
import requests
import typing
import uuid
from nl.export.config import NLACCESS_TOKEN, NLUSER_AGENT, NLBASE_URL
from nl.export.errors import NoConfig, NoMember, Unauthorized
from urllib.parse import urlparse, urlunparse
from pathlib import Path

__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


def get_auth_session() -> requests.Session:
    """"""
    headers = {'Accept': 'application/json',
               'Accept-Language': "de",
               'Content-Type': 'application/json',
               "Authorization": f"Bearer {NLACCESS_TOKEN}",
               'User-Agent': NLUSER_AGENT}

    session = requests.Session()
    session.headers.update(headers)

    return session


def make_url(path: str) -> str:
    """"""
    from urllib.parse import urlparse, urlunparse

    uobj = list(urlparse(NLBASE_URL))
    uobj[2] = path

    return urlunparse(uobj)


def get_items_found(query: dict) -> int:
    session = get_auth_session()
    search_url = make_url("/@search")

    num_found = 0

    params = query.copy()

    if "b_size" not in params:
        params["b_size"] = 1

    with session.get(search_url, params=params) as req:
        if req.status_code == 200:
            res = req.json()
            num_found = res.get("items_total", 0)

    return num_found


def get_search_results(params: dict) -> typing.Iterator:
    search_url = make_url("/@search")
    session = get_auth_session()

    _params = params.copy()

    if "b_size" not in _params:
        _params["b_size"] = 100

    def search_(surl, squery):
        with session.get(surl, params=squery) as req:
            if req.status_code != 200:
                yield None

            res = req.json()

        for entry in res["items"]:
            yield entry

        try:
            for entry in search_(res["batching"]["next"], {}):
                yield entry
        except KeyError:
            yield None

    return (entry for entry in search_(search_url, _params) if entry is not None)


class Registry:

    def __init__(self, session=None) -> None:
        self.session = session

        if self.session is None:
            self.session = get_auth_session()

    def get(self, entry: str) -> any:
        """"""
        logger = logging.getLogger(__name__)

        regurl = make_url(f"/@registry/{entry}")

        value = None

        with self.session.get(regurl) as req:
            if req.status_code == 200:
                value = req.json()
            else:
                msg = "Keine Konfiguration"
                logger.error(msg)

                raise NoConfig

        return value


class PloneItem:

    def __init__(self, plone_uid: str, plone_item: dict = None, session=None, expands: list = []) -> None:
        """Ein Plone Item erzeugen

        Args:
            plone_uid (str): Eine Plone ID, entweder die UID oder den API Link
            plone_item (dict, optional): Das JSON Item eines Plone Objekts
        """
        logger = logging.getLogger(__name__)

        self.session = session

        if self.session is None:
            self.session = get_auth_session()
        self.search_url = make_url("/@search")
        self.relations_url = make_url("/@relations")

        self.plone_uid = None
        self.__item_url__ = None
        self.plone_item = {}
        self.registry = Registry(self.session)

        if isinstance(plone_item, dict):
            self.plone_item = plone_item
            self.plone_uid = self.plone_item["UID"]
            self.__item_url__ = urlparse(self.plone_item['@id'])
        else:
            try:
                puid = uuid.UUID(plone_uid)
                self.plone_uid = puid.hex
                self.getItemBySearch()
            except ValueError:
                self.__item_url__ = urlparse(plone_uid)
                params = {}
                if len(expands) > 0:
                    params["expand"] = expands
                with self.session.get(self.item_url, params=params) as req:
                    if req.status_code in (401, 403):
                        raise Unauthorized
                    self.plone_item = req.json()
                    self.plone_uid = self.plone_item["UID"]
            except IndexError:
                pass

    @property
    def item_url(self):
        """"""
        return urlunparse(self.__item_url__)

    def getItemBySearch(self):
        """"""
        logger = logging.getLogger(__name__)

        params = {"UID": self.plone_uid}

        with self.session.get(self.search_url, params=params) as req:
            if req.status_code in (401, 403):
                raise Unauthorized
            elif req.status_code != 200:
                msg = "Keinen Member gefunden"
                logger.error(msg)
                raise NoMember

            res = req.json()
            logger.debug(res)

            regurl = res["items"][0]['@id']

        with self.session.get(regurl) as req:
            self.plone_item = req.json()
            self.__item_url__ = urlparse(self.plone_item['@id'])

    def get_registry_record(self, entry):
        """"""
        return self.registry.get(entry)

    def update(self, values: dict):
        """"""
        logger = logging.getLogger(__name__)

        with self.session.patch(self.item_url, json=values) as req:
            if req.status_code != 204:
                msg = "Konnte Member nicht ändern"
                logger.error(msg)

        with self.session.get(self.item_url) as req:
            self.plone_item = req.json()


class Member(PloneItem):

    @classmethod
    def byLogonName(cls, uid):
        """Einen Nutzer anhand der Kennung finden

        Args:
            uid ([type]): [description]
        """
        logger = logging.getLogger(__name__)

        session = get_auth_session()
        search_url = make_url("/@search")

        params = {"logonname": uid, "fullobjects": 1}

        with session.get(search_url, params=params) as req:
            if req.status_code != 200:
                msg = "Keinen Member gefunden"
                logger.error(msg)
                raise NoMember

            res = req.json()
            logger.debug(res)

        try:
            return cls(None, plone_item=res["items"][0])
        except IndexError:
            msg = "Keinen Member gefunden"
            logger.error(msg)
            raise NoMember

    def licences(self, licence_type=None, review_state=None):
        """"""
        logger = logging.getLogger(__name__)

        query = {'nlLicenseOwner': self.plone_uid,
                 'object_provides': ["nl.behavior.behaviors.licence.ILicenceMarker"],
                 "fullobjects": 1}

        if isinstance(review_state, str):
            query["review_state"] = review_state

        if isinstance(licence_type, str):
            query["licence_type"] = licence_type

        with self.session.get(self.search_url, params=query) as req:
            if req.status_code != 200:
                msg = "Keine Lizenzen gefunden"
                logger.error(msg)
                return []

            res = req.json()

        return (Licence(None, plone_item=entry) for entry in res["items"])

    def workflow(self):
        logger = logging.getLogger(__name__)

        with self.session.get(self.plone_item["@components"]["workflow"]["@id"]) as req:
            if req.status_code != 200:
                msg = "Kein Workflow gefunden"
                logger.error(msg)
                return []

            res = req.json()

        return res


class Institution(Member):
    """"""

    def __init__(self, plone_uid: str, plone_item: dict = None, session=None) -> None:
        super().__init__(plone_uid, plone_item, session)

        uobj = list(self.__item_url__)
        self.ipath = Path(uobj[2])

        uobj[2] = (self.ipath / "files").as_posix()
        self.filespath = urlunparse(uobj)

        formname = Path(self.get_registry_record(
            "nl.site.registration_form_name"))
        eulaname = Path(self.get_registry_record(
            "nl.site.registration_eula_name"))

        self.formpath = self.filespath / formname
        self.eulapath = self.filespath / eulaname

    def files(self):
        """"""
        fcontainer = PloneItem(self.filespath, session=self.session)

        return (PloneItem(item["@id"]) for item in fcontainer.plone_item["items"])


class Product(PloneItem):
    """"""


class LicenceModel(PloneItem):
    """"""

    @property
    def lic_query(self) -> dict:
        return {"lmuid": self.plone_uid,
                'object_provides': ["nl.behavior.behaviors.licence.ILicenceMarker"],
                "fullobjects": 1}

    def getEula(self):
        """"""
        eulaurl = self.plone_item["f_eula"]["download"]
        with self.session.get(eulaurl) as req:
            xml = req.text

        return xml

    def getSignedEula(self):
        """"""
        eulaurl = self.plone_item["f_eula_sign"]["download"]
        with self.session.get(eulaurl) as req:
            xml = req.text

        return xml

    def getTitle(self) -> str:
        stitles = ('Classic SingleUser',
                   "Classic Institution",
                   'Opt-In', )

        if self.plone_item["title"] in stitles:
            return self.productTitle()

        return self.plone_item["title"]

    def productTitle(self):
        """"""
        return self.plone_item["parent"]["title"]

    def licences(self, review_state: list = None) -> typing.Iterator:
        """"""
        logger = logging.getLogger(__name__)

        query = self.lic_query

        if isinstance(review_state, list):
            query["review_state"] = review_state

        return (Licence(None, plone_item=entry) for entry in get_search_results(query))


class Licence(PloneItem):
    """"""

    def lmodel(self):
        """"""
        return LicenceModel(self.plone_item["lmodel"]["@id"])


class Registration(PloneItem):
    """"""

    def lmodels(self):
        """"""
        return (LicenceModel(entry["@id"]) for entry in self.plone_item["licence_models"])


class Vocabulary:

    def __init__(self, vocabulary: str) -> None:
        """Ein Plone Vokabular

        Args:
            vocabulry ([type]): [description]
        """
        logger = logging.getLogger(__name__)

        self.vocabulary = vocabulary
        self.session = get_auth_session()
        self.vocab_url = make_url(f"/@vocabularies/{vocabulary}")

        self.item_url = None
        self.plone_vocab = {}

        with self.session.get(self.vocab_url) as req:
            self.plone_vocab = req.json()
            self.item_url = self.plone_vocab["@id"]

    def getTitle(self, token):
        """"""
        for entry in self.plone_vocab["items"]:
            if entry["token"] == token:
                return entry["title"]
        return ""


class Group:

    def __init__(self, groupname: str) -> None:
        """Eine Plone Gruppe

        Args:
            groupname ([type]): [description]
        """
        logger = logging.getLogger(__name__)

        self.groupname = groupname
        self.session = get_auth_session()
        self.group_url = make_url(f"/@groups/{groupname}")

        self.plone_group = {}

        with self.session.get(self.group_url) as req:
            self.plone_group = req.json()
            self.item_url = self.plone_group["@id"]

    def members(self):
        """Alle Mitglieder einer Gruppe"""
        mlist = []

        for uid in self.plone_group["members"]["items"]:
            mlist.append(getMember(uid))

        return mlist


def getMember(uid):
    """Einen Plone Member auslesen"""
    session = get_auth_session()

    member = {}

    purl = make_url(f"/@users/{uid}")
    with session.get(purl) as req:
        member = req.json()

    return member
