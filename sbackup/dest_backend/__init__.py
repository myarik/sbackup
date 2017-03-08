from .aws import S3Backend

__all__ = (
    'get_backend',
    'DST_BACKEND'
)

_dst_backend = (
    ('s3', S3Backend),
)
DST_BACKEND = dict(_dst_backend)


def get_backend(backend_name, backend_conf):
    """
    Args:
        backend_name(str): A backend name
        backend_conf(dict): A backend configuration
    Returns:
        A backend instance
    Raises:
        TypeError: An error occur if configuration is incorrect
    """
    obj = DST_BACKEND[backend_name]
    return obj(**backend_conf)
