# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)
import six


class SBackupException(Exception):
    """
    Package Exception
    """

    def __init__(self, message="", content=None):
        self.message = six.text_type(message)
        self.content = content

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message


class SBackupValidationError(SBackupException):
    pass
