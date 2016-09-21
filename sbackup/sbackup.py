# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)
import os
from .exception import SBackupException
import stat
# import yaml


class SBackupCLI(object):

    def __init__(self, filename):
        self.filename = filename

    # def _load_config(self):
    #     """
    #     Load yml config
    #     """
    #     with open(self.filename, 'rt') as file_config:
    #         config = yaml.load(file_config)
    #     return config

    def run(self):
        if not os.path.exists(self.filename):
            raise SBackupException(
                "the config: %s could not be found" % self.filename
            )
        if not (os.path.isfile(self.filename) or stat.S_ISFIFO(os.stat(self.filename).st_mode)):
            raise SBackupException(
                "the config: %s does not appear to be a file" % self.filename
            )



