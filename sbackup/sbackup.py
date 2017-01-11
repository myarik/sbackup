# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import stat
import logging

from yaml.error import YAMLError

from .task import TASK_CLASSES
from .exception import SBackupException
from .utils import load_config


class SBackupCLI(object):
    def __init__(self, filename, logger=None):
        self.filename = filename
        self.logger = logger or logging.getLogger(__name__)

    def run(self):
        if not os.path.exists(self.filename):
            raise SBackupException(
                "Can't find a config file \"%s\"" % self.filename
            )
        if not (os.path.isfile(self.filename) or stat.S_ISFIFO(os.stat(self.filename).st_mode)):
            raise SBackupException(
                "the config: %s does not appear to be a file" % self.filename
            )
        try:
            config = load_config(self.filename)
        except YAMLError as error:
            msg = "Can't load config file: %s" % error
            self.logger.error(msg)
            raise SBackupException(
                "the config: %s does not a yaml file" % self.filename
            )
        if config is None:
            raise SBackupException(
                "No values found in file %s" % self.filename
            )
        for task in config:
            task_type = task['type']
            if task_type not in TASK_CLASSES:
                self.logger.warning("Can't work with backup's type %s" % task['type'])
                continue
            handler = TASK_CLASSES[task_type]
            handler.create_task(task)
            # handler.validate()
                # [{'sources': ['/tmp/dir1', '/tmp/dir2']},
                # named{'backends': [{'s3': {'key': 'asd1123sds', 'id': 'Sdd3qsdasd', 'backet': 'test'}}, {'ssh': {'host': 'test'}}]}]
