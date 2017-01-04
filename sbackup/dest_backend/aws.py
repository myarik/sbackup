# -*- coding: utf-8 -*-
import logging
import os

from boto3 import Session
from boto3.exceptions import S3UploadFailedError
from botocore.exceptions import ClientError
from sbackup.exception import (
    SBackupValidationError,
    SBackupException
)

from .base import BackendWrapper, validated

logger = logging.getLogger(__name__)


class S3BackendException(SBackupException):
    pass


class S3Backend(BackendWrapper):
    """
    The S3 Backend
    Attributes:
       access_key_id(basestring): YOUR_ACCESS_KEY
       secret_access_key(basestring): YOUR_SECRET_KEY
       bucket(basestring): A bucket name

    Usage::

        from sbackup.dest_backend.aws import S3Backend
        s3 = S3Backend('mykey', 'mysecretkey', 'mybucket')
        s3.validate()

        ## Get objects name from S3
        for item in s3:
            print(s3)

        ## Upload a file to S3
        s3.upload('/tmp/my_file.csv')

        ## Download a file from S3
        s3.download('my_file.csv', '/tmp')

        ##Delete a file from S3
        s3.delete('my_file.csv')

    """

    def __init__(self, access_key_id, secret_access_key, bucket, *args, **kwargs):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.bucket_name = bucket
        self._session = Session(
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key
        )
        self.is_validated = False
        self._bucket = None

    @property
    def bucket(self):
        if self._bucket:
            return self._bucket
        self._bucket = self._session.resource('s3').Bucket(self.bucket_name)
        return self._bucket

    def validate(self):
        try:
            self._session.client('sts').get_caller_identity()
        except ClientError as error:
            raise SBackupValidationError(
                "Can't connect to AWS, error: %s" % error
            )
        try:
            s3 = self._session.resource('s3')
            s3.meta.client.head_bucket(Bucket=self.bucket_name)
        except ClientError as error:
            logger.error('Failed to connect to S3', exc_info=True)
            error_code = int(error.response['Error']['Code'])
            if error_code == 404:
                raise SBackupValidationError(
                    "The bucket %s does not exist" % self.bucket_name
                )
            raise SBackupValidationError(
                "Can't work with a bucket %s, error: %s" % (self.bucket_name, error)
            )
        else:
            self.is_validated = True

    @validated
    def upload(self, src_path):
        """
        Upload a file to S3
        Args:
            src_path(basestring): A path to file
        Raises:
            S3BackendException
        """

        if not src_path:
            logger.error("The src_path does not set")
            raise S3BackendException('Please set a path')
        if not os.path.exists(src_path):
            logger.error("Can't find a path %s" % src_path)
            raise S3BackendException("Can't find a path")
        filename = os.path.basename(src_path)
        try:
            logger.debug("Start uploading the %s to S3" % filename)
            self.bucket.upload_file(src_path, filename)
        except S3UploadFailedError as error:
            logger.error("Can't upload file to S3", exc_info=True)
            raise S3BackendException("%s" % error)

    @validated
    def download(self, src_filename, dst_dir, dst_filename=None):
        """
        Download item from AWS
        Args:
            src_filename(basestring): A source file name
            dst_dir(basestring): A dst dir
            dst_filename(basestring): A dst file
        Raises:
            S3BackendException
        """
        if not os.path.isdir(dst_dir):
            logger.error("Can't find a directory %s" % dst_dir)
            raise S3BackendException("Can't find a directory")
        if not os.access(dst_dir, os.W_OK):
            logger.error("The SRC dir %s is not writeable" % dst_dir)
            raise S3BackendException(
                "User dosen't have access to write in the %s" % dst_dir)
        if dst_filename:
            dst_path = os.path.join(dst_dir, dst_filename)
        else:
            dst_path = os.path.join(dst_dir, src_filename)
        try:
            logger.debug("Start download the %s" % src_filename)
            self.bucket.download_file(src_filename, dst_path)
        except ClientError as error:
            logger.error("Can't download file from S3", exc_info=True)
            error_code = int(error.response['Error']['Code'])
            if error_code == 404:
                raise S3BackendException(
                    "The file %s does not exist" % src_filename
                )
            else:
                raise S3BackendException(
                    "Can't download the file %s, error: %s" % (src_filename, error)
                )

    @validated
    def __iter__(self):
        for item in self._ls():
            yield item.key

    def _ls(self):
        try:
            for item in self.bucket.objects.all():
                yield item
        except ClientError as error:
            logger.error("Can't get objects from S3", exc_info=True)
            raise S3BackendException("%s" % error)

    @validated
    def last_modified(self):
        """
        A generator which yields filename and last modified date
        """
        for item in self.bucket.objects.all():
            yield item.key, item.last_modified

    @validated
    def delete_file(self, filename):
        for item in self._ls():
            if item.key == filename:
                try:
                    item.delete()
                except ClientError as error:
                    logger.error("Can't delete a object from S3", exc_info=True)
                    raise S3BackendException("Can't delete a object: %s" % error)
                break

    @validated
    def delete(self, file_list):
        if not isinstance(file_list, list):
            raise S3BackendException("file_list must be a list object")
        for item in self._ls():
            if item.key in file_list:
                try:
                    item.delete()
                except ClientError as error:
                    logger.error("Can't delete a object from S3", exc_info=True)
                    raise S3BackendException("Can't delete a object: %s" % error)

    def __repr__(self):
        return "S3"
