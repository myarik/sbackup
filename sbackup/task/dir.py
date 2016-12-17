# -*- coding: utf-8 -*-
import collections
import os
import tempfile
import tarfile
import shutil
import datetime
import concurrent.futures

from sbackup.exception import SBackupValidationError

from .base import Task, Field, Backends


class DirBackupTask(Task):
    sources = Field()
    dst_backends = Backends()
    backup_name = Field(default='backup')
    tmp_dir = Field(required=False)

    _executor_cls = concurrent.futures.ThreadPoolExecutor
    _max_workers = 2

    def validate_sources(self, attr):
        if not isinstance(attr, collections.Iterable):
            raise SBackupValidationError('The sources has to be a list')
        for source_item in attr:
            if not os.path.exists(source_item):
                raise SBackupValidationError("Can't find a %s" % source_item)
            if not os.access(source_item, os.R_OK):
                raise SBackupValidationError("User don't have access to read a %s" % source_item)
        return attr

    def validate_tmp_dir(self, attr):
        if not os.path.exists(attr):
            raise SBackupValidationError("Can't find a %s" % attr)
        if not os.access(attr, os.R_OK):
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
        try:
            with tarfile.open(output_filename, "x:gz") as tar:
                for source in self.sources:
                    tar.add(source, arcname=os.path.basename(source))
        except FileExistsError:
            raise SBackupValidationError("Can't create a tarfile")
        return output_filename

    @staticmethod
    def upload_backup(backend, filename):
        backend.upload(filename)
        return "Uploaded"

    def create(self):
        if self.tmp_dir:
            tar_dir = tempfile.mkdtemp(dir=self.tmp_dir)
        else:
            tar_dir = tempfile.mkdtemp(dir=self.tmp_dir)
        try:
            backup_file = self.make_tarfile(tar_dir)
            with self._executor_cls(max_workers=self._max_workers) as executor:
                future_to_upload = [executor.submit(self.upload_backup, backend, backup_file)
                                    for backend in self.dst_backends]
                for future in concurrent.futures.as_completed(future_to_upload):
                    # https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.as_completed
                    data = future.result()
                    print(data)
        finally:
            shutil.rmtree(tar_dir)

    def run(self):
        self.create()
        # TODO remove old backup
