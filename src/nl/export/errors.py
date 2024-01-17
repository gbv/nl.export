# -*- coding: UTF-8 -*-
"""Errors
##############################################################################
#
# Copyright (c) 2023 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

# Imports

__author__ = """Marc-J. Tegethoff <marc.tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


class NoConfig(OSError):
    pass


class NoMember(BaseException):
    pass


class Unauthorized(BaseException):
    pass
