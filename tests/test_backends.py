# -*- coding: utf-8 -*-
from unittest import mock

from botocore.exceptions import ClientError
from sbackup.exception import SBackupValidationError
from sbackup.dest_backend.aws import S3Backend, S3BackendException

import pytest
import os


@mock.patch('sbackup.dest_backend.aws.Session.client')
def test_validate_login_aws_backend(session_mock):
    def side_effect(value, *args):
        caller = mock.Mock()
        caller.side_effect = ClientError({'Error': {'Code': 404}}, 'Error')
        sts = mock.Mock()
        sts.get_caller_identity = caller
        return sts
    session_mock.side_effect = side_effect
    with pytest.raises(SBackupValidationError):
        obj = S3Backend('FAKE_KEY_ID', 'FAKE_KEY', 'backup')
        obj.validate()


@mock.patch('sbackup.dest_backend.aws.Session.client')
@mock.patch('sbackup.dest_backend.aws.Session.resource')
def test_validate_aws_bucket(session_mock, *args):
    def side_effect(value, ):
        if value == 'sts':
            caller = mock.Mock()
            caller.return_value = None
            sts = mock.Mock()
            sts.get_caller_identity = caller
            return sts
        elif value == 's3':
            caller = mock.Mock()
            caller.side_effect = ClientError({'Error': {'Code': 404}}, 'Error')
            s3 = mock.Mock()
            s3.meta.client.head_bucket = caller
            return s3

    session_mock.side_effect = side_effect
    with pytest.raises(SBackupValidationError):
        obj = S3Backend('FAKE_KEY_ID', 'FAKE_KEY', 'backup')
        obj.validate()

@mock.patch('sbackup.dest_backend.aws.Session.resource')
@mock.patch('sbackup.dest_backend.aws.Session.client')
def test_validate_aws_upload(session_mock, resourse_mock):
    session_mock.client.get_caller_identity.return_value = True
    resourse_mock.meta.client.head_bucket.return_value = True
    here = os.path.dirname(__file__)
    obj = S3Backend('FAKE_KEY_ID', 'FAKE_KEY', 'backup')
    obj.validate()
    fake_path = os.path.join(here, 'fake_file.txt')
    with pytest.raises(S3BackendException):
        obj.upload(fake_path)


@mock.patch('sbackup.dest_backend.aws.Session.resource')
@mock.patch('sbackup.dest_backend.aws.Session.client')
def test_validate_aws_download(session_mock, resourse_mock):
    session_mock.client.get_caller_identity.return_value = True
    resourse_mock.meta.client.head_bucket.return_value = True
    here = os.path.dirname(__file__)
    obj = S3Backend('FAKE_KEY_ID', 'FAKE_KEY', 'backup')
    obj.validate()
    fake_path = os.path.join(here, '/fake_dir')
    with pytest.raises(S3BackendException):
        obj.download('test.txt', fake_path)
    with mock.patch('os.access') as m_os:
        with pytest.raises(S3BackendException):
            m_os.return_value = False
            obj.download('test.txt', '/tmp')
    error = ClientError({'Error': {'Code': 404}}, 'Error')
    with mock.patch("sbackup.dest_backend.aws.Session.resource", side_effect=error):
        with pytest.raises(S3BackendException):
            obj.download('test.txt', '/tmp')
