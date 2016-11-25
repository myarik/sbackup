# -*- coding: utf-8 -*-
import collections

from sbackup.exception import SBackupValidationError
from sbackup.utils import validate_dir

from .base import Task, Field, DestField

# TODO tar
# https://docs.python.org/3/library/tarfile.html
# http://stackoverflow.com/questions/2032403/how-to-create-full-compressed-tar-file-using-python


class DirBackupTask(Task):
    source_dirs = Field()
    dest_backends = DestField()
    backup_name = Field(default='asa')
    tmp_dir = Field(default='/tmp')

    def validate_source_dirs(self, attr):
        if not isinstance(attr, collections.Iterable):
            raise SBackupValidationError('The source_dir has to be a list')
        for source_dir in attr:
            validate_dir(source_dir)
        return attr


