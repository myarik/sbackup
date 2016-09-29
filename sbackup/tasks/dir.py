# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

import collections

from sbackup.exception import SBackupValidationError
from sbackup.utils import validate_dir

from .base import Task


class DirBackupTask(Task):
    _fields = (
        'source_dirs',
        'backends'
    )

    # TODO think about not required fields (tmp_dir, backup_name)

    def validate_source_dirs(self, attr):
        if not isinstance(attr, collections.Iterable):
            raise SBackupValidationError('The source_dir has to be a list')
        for source_dir in attr:
            validate_dir(source_dir)
        return attr

    def validate_backends(self, attr):
        pass
