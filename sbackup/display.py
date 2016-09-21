# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

import sys
import getpass
import errno
from .utils import stringc


class Display:

    def __init__(self):

        self._warns = {}
        self._errors = {}

    @staticmethod
    def display(msg, color=None, stderr=False):
        if color:
            msg = stringc(msg, color)
        if not stderr:
            fileobj = sys.stdout
        else:
            fileobj = sys.stderr

        fileobj.write(msg)

        try:
            fileobj.flush()
        except IOError as e:
            # Ignore EPIPE in case fileobj has been prematurely closed, eg.
            # when piping to "head -n1"
            if e.errno != errno.EPIPE:
                raise

    @staticmethod
    def log(msg, stderr=False, logger=None):
        if logger:
            msg.lstrip(u'\n')
            if stderr:
                logger.error(msg)
            else:
                logger.info(msg)

    def warning(self, msg, formatted=False):
        new_msg = "\n[WARNING]: %s" % msg
        if new_msg not in self._warns:
            self.display(new_msg, color='bright purple', stderr=True)
            self._warns[new_msg] = 1

    def error(self, msg, wrap_text=True):
        new_msg = u"\n[ERROR]: %s" % msg
        if new_msg not in self._errors:
            self.display(new_msg, color='red', stderr=True)
            self._errors[new_msg] = 1

    @staticmethod
    def prompt(msg, private=False):
        if private:
            return getpass.getpass(msg)
        else:
            return input(msg)
