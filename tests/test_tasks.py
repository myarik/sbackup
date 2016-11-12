# -*- coding: utf-8 -*-

import pytest
from sbackup.tasks import DirBackupTask
from sbackup.exception import SBackupValidationError


def test_validate_dir_task():
    with pytest.raises(AttributeError):
        DirBackupTask.create_task({'type': 'dir'})
    with pytest.raises(SBackupValidationError):
        DirBackupTask.create_task({
            'type': 'dir',
            'source_dirs': ['/test/fake_dir/aXsTrasL'],
            'backends': [{
                's3': {
                    'key': 'asd1123sds',
                    'id': 'Sdd3qsdasd',
                    'backet': 'test'
                }
            }]
        })
