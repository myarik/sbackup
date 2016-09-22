# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

from .constants import codeCodes

import yaml


def stringc(text, color):
    """String in color."""

    return u"\033[%sm%s\033[0m" % (codeCodes[color], text)


def load_config(filename: str):
    """
    Load yml config
    """
    with open(filename, 'rt') as file_config:
        config = yaml.safe_load(file_config)
    return config
