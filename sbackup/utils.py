# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os

import yaml

from .constants import codeCodes
from .exception import SBackupValidationError


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


def validate_dir(dir_path: str):
    is_dir = os.path.exists(dir_path) or os.path.isdir("dir")
    if not is_dir:
        raise SBackupValidationError("Can't find a dir %s" % dir_path)
    if not os.access(dir_path, os.R_OK):
        raise SBackupValidationError("User don't have access to read a dir %s" % dir_path)
    return True
