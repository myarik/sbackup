# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

from .constants import codeCodes


def stringc(text, color):
    """String in color."""

    return u"\033[%sm%s\033[0m" % (codeCodes[color], text)
