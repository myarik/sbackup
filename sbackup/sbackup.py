# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import stat
import logging
import datetime
import yaml

from .task import TASK_CLASSES
from .exception import SBackupException

from sbackup.dest_backend import get_backend


class SBackupCLI(object):
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def create(self, tasks):
        for task in tasks:
            task_type = task['type']
            if task_type not in TASK_CLASSES:
                self.logger.warning("Can't work with backup's type %s" % task['type'])
                continue
            handler = TASK_CLASSES[task_type]
            obj = handler.create_task(task)
            obj.create()

    @staticmethod
    def get_backend(backend_name, backend_conf):
        try:
            return get_backend(backend_name, backend_conf)
        except TypeError:
            raise SBackupException('Incorrect a backend configuration')

    def ls(self, backend_name, backend_conf):
        """
        Return generator
        """
        for item in self.get_backend(backend_name, backend_conf):
            yield item

    def restore(self, filename):
        return NotImplementedError

    def delete(self, backend_name, backend_conf, filename):
        backend = self.get_backend(backend_name, backend_conf)
        backend.delete(filename)

    def delete_older(self, backend_name, backend_conf, retention_period):
        retention_date = datetime.date.today() - datetime.timedelta(retention_period)
        backend = self.get_backend(backend_name, backend_conf)
        backend.delete_older(retention_date)

    @staticmethod
    def load_config(filename, logger=None):
        if not os.path.exists(filename):
            raise SBackupException(
                "Can't find a config file \"%s\"" % filename
            )
        if not (os.path.isfile(filename) or stat.S_ISFIFO(os.stat(filename).st_mode)):
            raise SBackupException(
                "the config: %s does not appear to be a file" % filename
            )
        try:
            with open(filename, 'rt') as file_config:
                config = yaml.safe_load(file_config)
        except yaml.YAMLError as error:
            msg = "Can't load config file: %s" % error
            if logger:
                logger.error(msg)
            raise SBackupException(
                "the config: %s does not a yaml file" % filename
            )
        if config is None:
            raise SBackupException(
                "No values found in file %s" % filename
            )
        return config
