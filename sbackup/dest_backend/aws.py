# -*- coding: utf-8 -*-
import logging
import os

from boto3 import Session
from boto3.exceptions import S3UploadFailedError
from botocore.exceptions import ClientError
from urllib.parse import urljoin

from sbackup.exception import (
    SBackupValidationError,
    SBackupException
)
from .base import BackendWrapper, validated

logger = logging.getLogger(__name__)


def safe_join(base_path, *paths):
    """
    Joins one or more path components to the base path component
    intelligently. Returns a normalized version of the final path.

    The final path must be located inside of the base path component
    (otherwise a ValueError is raised).

    """
    base_path = base_path.rstrip('/')
    paths = [p for p in paths]

    final_path = base_path
    for path in paths:
        final_path = urljoin(final_path.rstrip('/') + "/", path)

    base_path_len = len(base_path)
    if (not final_path.startswith(base_path) or
            final_path[base_path_len:base_path_len + 1] not in ('', '/')):
        raise ValueError('the joined path is located outside of the base path'
                         ' component')

    return final_path.lstrip('/')


class S3BackendException(SBackupException):
    """
    S3Backend Exception
    """
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

    def __init__(self, access_key_id, secret_access_key, bucket,
                 location='', *args, **kwargs):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.bucket_name = bucket
        self._session = Session(
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key
        )
        self.is_validated = False
        self._bucket = None
        self.location = (location or '').lstrip('/')

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

    def _normalize_name(self, name):
        """
        Normalizes the name so that paths like /path/to/ignored/../something.txt
        work. We check to make sure that the path pointed to is not outside
        the directory specified by the LOCATION setting.
        """
        try:
            return safe_join(self.location, name)
        except ValueError:
            raise S3BackendException("Attempted access to '%s' denied." % name)

    def _get_location(self):
        name = self._normalize_name('')
        if name and not name.endswith('/'):
            name += '/'
        return name

    def upload(self, src_path, *args, **kwargs):
        """
        Upload a file to S3
        Args:
            src_path(basestring): A path to file
            path(basestring): A S3 location
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
        name = self._normalize_name(filename)
        try:
            logger.debug("Start uploading the %s to S3" % filename)
            self.bucket.upload_file(src_path, name)
        except S3UploadFailedError as error:
            logger.error("Can't upload file to S3", exc_info=True)
            raise S3BackendException("%s" % error)

    def download(self, src_filename, dst_dir, dst_filename=None, **kwargs):
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
        name = self._normalize_name(src_filename)
        try:
            logger.debug("Start download the %s" % src_filename)
            self.bucket.download_file(name, dst_path)
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
        return dst_path

    def __iter__(self):
        for _, item in self._ls():
            yield item

    def _ls(self):
        name = self._normalize_name('')
        base_parts = name.split("/")[:-1]
        try:
            for item in self.bucket.objects.filter(Prefix=self._get_location()):
                parts = item.key.split("/")
                parts = parts[len(base_parts):]
                # Only work with files
                if len(parts) == 1:
                    yield item, parts[0]
        except ClientError as error:
            logger.error("Can't get objects from S3", exc_info=True)
            raise S3BackendException("%s" % error)

    def get_last_backup(self, name=None):
        """
        Get last backup

        Args:
            name(srt)
        """
        backup_file = None
        max_date = None
        for item, file_name in self._ls():
            if name and not file_name.startswith(name):
                continue
            if not max_date or max_date < item.last_modified:
                max_date, backup_file = item.last_modified, file_name
        return backup_file

    def delete_older(self, retention_date):
        """
        Delete files than older
        Args:
            retention_date(datetime.date)
        """
        for item, _ in self._ls():
            if item.last_modified.date() < retention_date:
                item.delete()

    def delete(self, filename):
        for item, name in self._ls():
            if name == filename:
                try:
                    item.delete()
                except ClientError as error:
                    logger.error("Can't delete a object from S3", exc_info=True)
                    raise S3BackendException("Can't delete a object: %s" % error)
                break

    def __repr__(self):
        return "S3"
