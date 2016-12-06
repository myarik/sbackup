from .aws import S3Backend

__all__ = (
    'S3Backend',
    'DST_BACKENDS'
)

_dst_backends = (
    ('s3', S3Backend),
)
DST_BACKENDS = dict(_dst_backends)
