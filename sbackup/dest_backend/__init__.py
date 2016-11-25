from .aws import S3Backend

__all__ = (
    'S3Backend',
    'DEST_BACKENDS'
)

_dest_backends = (
    ('s3', S3Backend),
)
DEST_BACKENDS = dict(_dest_backends)
