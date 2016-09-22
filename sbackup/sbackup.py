# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)
import os
import stat
from yaml.error import YAMLError

from .exception import SBackupException
from .utils import load_config
from .display import Display


class SBackupCLI(object):

    def __init__(self, filename):
        self.filename = filename
        self.display = Display()
        self.logger = None

    def run(self):
        if not os.path.exists(self.filename):
            raise SBackupException(
                "the config: %s could not be found" % self.filename
            )
        if not (os.path.isfile(self.filename) or stat.S_ISFIFO(os.stat(self.filename).st_mode)):
            raise SBackupException(
                "the config: %s does not appear to be a file" % self.filename
            )
        try:
            config = load_config(self.filename)
        except YAMLError as error:
            msg = "Can't load config file: %s" % error
            self.display.log(msg, stderr=True, logger=self.logger)
            raise SBackupException(
                "the config: %s does not a yaml file" % self.filename
            )
        if config is None:
            raise SBackupException(
                "No values found in file %s" % self.filename
            )
        #[{'source_dirs': ['/tmp/dir1', '/tmp/dir2']},
         #{'backends': [{'s3': {'key': 'asd1123sds', 'id': 'Sdd3qsdasd', 'backet': 'test'}}, {'ssh': {'host': 'test'}}]}]




