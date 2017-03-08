# -*- coding: utf-8 -*-
import datetime
import logging
import os
import shutil
import tarfile
import tempfile

from contextlib import contextmanager

from sbackup.utils import get_backup_name
from sbackup.exception import SBackupValidationError
from .base import Task, Field, Backend

logger = logging.getLogger(__name__)


@contextmanager
def create_temp_dir(tmp_path=None):
    if tmp_path:
        tmp_dir = tempfile.mkdtemp(dir=tmp_path)
    else:
        tmp_dir = tempfile.mkdtemp()
    try:
        yield tmp_dir
    finally:
        shutil.rmtree(tmp_dir)


class DirBackupTask(Task):
    """
    The task for backup dirs
    Attributes:
       source(str): A source dir or file
       dst_backend(dict): A backend settings
       backup_name(basestring): Default is backup
       tmp_dir(basestring): A tmp path, default is TMPDIR

    Usage::

        from sbackup.task import DirBackupTask
        data = {
            'source': '/var/www/site1',
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
    source = Field()
    dst_backend = Backend()
    name = Field()
    tmp_dir = Field(required=False)

    @staticmethod
    def validate_source(attr):
        if not isinstance(attr, str):
            raise SBackupValidationError('The sources has to be a sting')
        if not os.path.exists(attr):
            logger.error("Can't find a %s" % attr)
            raise SBackupValidationError("Can't find a %s" % attr)
        if not os.access(attr, os.R_OK):
            logger.error("User don't have access to read a %s" % attr)
            raise SBackupValidationError("User don't have access to read a %s" % attr)
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

    def get_backup_name(self):
        return get_backup_name(self.name)

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
            name=self.get_backup_name(),
            time=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
        ))
        logger.debug("Create a temporary tar file: %s" % output_filename)
        try:
            with tarfile.open(output_filename, "x:gz") as tar:
                tar.add(self.source, arcname=os.path.basename(self.source))
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

    def extract(self, src_file):
        tar = tarfile.open(src_file)
        shutil.rmtree(self.source)
        tar.extractall(path=os.path.dirname(self.source))

    def create(self):
        self.validate()
        with create_temp_dir(self.tmp_dir) as tmp_dir:
            backup_file = self.make_tarfile(tmp_dir)
            self.upload_backup(backup_file)

    def restore(self, backup_file):
        if not backup_file:
            backup_file = self.dst_backend.get_last_backup(name=self.get_backup_name())
            if not backup_file:
                raise SBackupValidationError("Backup doesn't exist in the backend")
        logger.debug("Start download the file {file} to {backend}".format(
            file=backup_file,
            backend=str(self.dst_backend)
        ))
        with create_temp_dir(self.tmp_dir) as tmp_dir:
            src_file = self.dst_backend.download(backup_file, tmp_dir)
            logger.debug("Extract the file {file}".format(
                file=backup_file
            ))
            self.extract(src_file)