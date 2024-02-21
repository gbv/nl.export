# -*- coding: utf-8 -*-
"""Beschreibung

##############################################################################
#
# Copyright (c) 2023 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

import gettext
import logging
from pathlib import Path

__author__ = """Marc-J. Tegethoff <tegethoff@gbv.de>"""
__docformat__ = 'plaintext'


def main():
    def translate(Text):
        Text = Text.replace("usage:", "Verwendung")
        Text = Text.replace("show this help message and exit",
                            "zeige diese Hilfe an und tue nichts weiteres")
        Text = Text.replace("error:", "Fehler:")
        Text = Text.replace("the following arguments are required:",
                            "Die folgenden Argumente müssen angegeben werden:")
        Text = Text.replace("positional arguments",
                            "Kommandos")
        Text = Text.replace("options",
                            "Optionen")
        return Text

    gettext.gettext = translate

    import argparse
    from .conf import create_config, check_config
    from .lzn import lizenznehmer
    from nl.export.errors import NoConfig, Unauthorized
    from nl.export.gapi import TerminalColors

    logger = logging.getLogger()

    usage = "NL Export Tool"

    o_parser = argparse.ArgumentParser(description=usage)
    subparsers = o_parser.add_subparsers()

    sub_config = subparsers.add_parser(
        'konfig', help="Konfiguration erstellen")
    sub_config.add_argument(
        "--force",
        dest='force',
        action='store_true',
        default=False,
        help='Konfiguration überschreiben, falls vorhanden')
    sub_config.set_defaults(func=create_config)

    sub_licencees = subparsers.add_parser(
        'lzn', help="Lizenznehmer")
    sub_licencees.add_argument('--format',
                               nargs="?",
                               type=str,
                               help="""Ausgabeformat (csv|xml|json). Standard ist %(default)s)""",
                               metavar="Format",
                               default="csv")
    sub_licencees.add_argument('--ablage',
                               nargs="?",
                               type=Path,
                               help="Ablageverzeichnis. ",
                               metavar="Verzeichnis",
                               default=Path("."))
    sub_licencees.add_argument('--status',
                               type=str,
                               help="Status der Lizenz(en). Mehrfachnennung möglich",
                               action='append',
                               metavar="Status")
    sub_licencees.add_argument('urls',
                               type=str,
                               nargs='+',
                               help='URL(s) oder eindeutige Identifier (UUID) von Lizenz-Modellen oder Produkten')
    sub_licencees.set_defaults(func=lizenznehmer)

    o_parser.add_argument(
        "-v",
        dest='verbose',
        action='store_true',
        default=False,
        help='Mehr Nachrichten')

    options = o_parser.parse_args()

    log_level = logging.WARN

    if options.verbose:
        log_level = logging.INFO

    logging.basicConfig(encoding='utf-8',
                        format="%(levelname)s - %(funcName)s - %(message)s",
                        level=log_level)

    try:
        if options.func != create_config:
            if not check_config():
                raise NoConfig
        options.func(options)
    except Unauthorized:
        msg = "Zugriff nicht erlaubt. Bitte überprüfen Sie ihre Zugangsdaten."
        logger.error(msg)
    except AttributeError:
        logger.error("", exc_info=True)
        o_parser.print_help()
    except NoConfig:
        cmd = TerminalColors.bold("nl-export konfig")
        msg = f"""Die Konfigurationsdatei ist nicht vorhanden.

Diese kann mit {cmd} angelegt werden.
                """
        logger.error(msg)
