# -*- coding: utf-8 -*-
from unittest import mock

import pytest
from sbackup.exception import SBackupValidationError
from sbackup.task import DirBackupTask


@pytest.fixture(scope='session')
def fake_dir(tmpdir_factory):
    dir = tmpdir_factory.mktemp('data')
    return dir


def test_validation():
    with pytest.raises(AttributeError):
        obj = DirBackupTask.create_task({'type': 'dir'})
        obj.validate()
    # Source dir error
    with pytest.raises(SBackupValidationError):
        obj = DirBackupTask.create_task({
            'type': 'dir',
            'source_dirs': ['/test/fake_dir/aXsTrasL'],
            'dest_backends': {
                's3': {
                    'access_key_id': 'asd1123sds',
                    'secret_access_key': 'Sdd3qsdasd',
                    'bucket': 'test'
                }
            }
        })
        obj.validate()


def test_backend_validation(fake_dir):
    # Incorrect configuration
    with pytest.raises(SBackupValidationError):
        obj = DirBackupTask.create_task({
            'type': 'dir',
            'source_dirs': ['/test/fake_dir/aXsTrasL'],
            'dest_backends': {
                's3': {
                    'secret_access_key': 'Sdd3qsdasd',
                    'bucket': 'test'
                }
            }
        })
        obj.validate()
    with mock.patch('sbackup.dest_backend.aws.S3Backend.validate') as mock_validate:
        obj = DirBackupTask.create_task({
            'type': 'dir',
            'source_dirs': [fake_dir.dirname, ],
            'dest_backends': {
                's3': {
                    'access_key_id': 'asd1123sds',
                    'secret_access_key': 'Sdd3qsdasd',
                    'bucket': 'bucket'
                }
            }
        })
        obj.validate()
        assert mock_validate.called