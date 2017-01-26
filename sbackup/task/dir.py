# -*- coding: utf-8 -*-
import collections
import datetime
import logging
import os
import shutil
import tarfile
import tempfile

from sbackup.exception import SBackupValidationError
from .base import Task, Field, Backend

logger = logging.getLogger(__name__)


class DirBackupTask(Task):
    """
    The task for backup dirs
    Attributes:
       sources(list): A list of dirs
       dst_backend(dict): A backend settings
       backup_name(basestring): Default is backup
       tmp_dir(basestring): A tmp path, default is TMPDIR

    Usage::

        from sbackup.task import DirBackupTask
        data = {
            'sources': ['/var/www/site1', '/var/www/site2'],
            'dst_backend': {
                's3': {
                    'access_key_id': 'key_id',
                    'secret_access_key': 'access_key',
                    'bucket': 'backup'
                }
            },
            'retention_period': '7'
        }
        obj = DirBackupTask.create_task(data)
        obj.create() -- Create a backup and put it in dst backends

    Debug::

        import logging
        logging.basicConfig()
        logger = logging.getLogger('sbackup.task.dir')
        logger.setLevel(logging.DEBUG)

        from sbackup.task import DirBackupTask
        ...

    """
    sources = Field()
    dst_backend = Backend()
    backup_name = Field(default='backup')
    tmp_dir = Field(required=False)

    @staticmethod
    def validate_sources(attr):
        if not isinstance(attr, collections.Iterable):
            raise SBackupValidationError('The sources has to be a list')
        for source_item in attr:
            if not os.path.exists(source_item):
                logger.error("Can't find a %s" % source_item)
                raise SBackupValidationError("Can't find a %s" % source_item)
            if not os.access(source_item, os.R_OK):
                logger.error("User don't have access to read a %s" % source_item)
                raise SBackupValidationError("User don't have access to read a %s" % source_item)
        return attr

    @staticmethod
    def validate_tmp_dir(attr):
        if not os.path.exists(attr):
            logger.error("Can't find a %s" % attr)
            raise SBackupValidationError("Can't find a %s" % attr)
        if not os.access(attr, os.R_OK):
            logger.error("User don't have access to read a %s" % attr)
            raise SBackupValidationError("User don't have access to read a %s" % attr)
        return attr

    def make_tarfile(self, tar_dir):
        """
        Create a tar.gz backup

        Args:
            tar_dir(str)
        Returns:
            backup_file(str)

        Raises:
            SBackupValidationError: Exception if backup already exists.
        """
        output_filename = os.path.join(tar_dir, "{name}-{time}.tar.gz".format(
            name=self.backup_name,
            time=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
        ))
        logger.debug("Create a temporary tar file: %s" % output_filename)
        try:
            with tarfile.open(output_filename, "x:gz") as tar:
                for source in self.sources:
                    tar.add(source, arcname=os.path.basename(source))
        except FileExistsError:
            logger.error("Can't create a temporary tar file", exc_info=True)
            raise SBackupValidationError("Can't create a tarfile")
        return output_filename

    def upload_backup(self, filename):
        logger.debug("Start upload the file {file} to {backend}".format(
            file=filename,
            backend=str(self.dst_backend)
        ))
        self.dst_backend.upload(filename)
        logger.info("The {file} was uploaded to {backend}".format(
            file=filename,
            backend=str(self.dst_backend)
        ))

    def create(self):
        self.validate()
        if self.tmp_dir:
            tar_dir = tempfile.mkdtemp(dir=self.tmp_dir)
        else:
            tar_dir = tempfile.mkdtemp()
        try:
            backup_file = self.make_tarfile(tar_dir)
            self.upload_backup(backup_file)
        finally:
            shutil.rmtree(tar_dir)
