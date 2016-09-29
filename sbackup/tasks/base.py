# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)
from sbackup.exception import SBackupValidationError


class Task(object):
    _fields = ()

    def validate(self):
        return True

    def get_fields(self):
        """
        Return all required fields
        """
        return self._fields

    @classmethod
    def create_task(cls, attrs):
        """
        Args:
            attrs(dict): A dict
        Raises:
            AttributeError: A Required field doesn't exist in attrs
        """
        errors = dict()
        obj = cls()
        for field in obj.get_fields():
            value = attrs.get(field)
            if not value:
                raise AttributeError(
                    "Field %s is required field for dir task" % field
                )
            validate_method = getattr(obj, 'validate_' + field, None)
            try:
                if validate_method:
                    validate_method(value)
            except SBackupValidationError as error:
                errors[field] = error.message
            else:
                setattr(obj, field, value)
        if errors:
            raise SBackupValidationError(
                message="Can't validate fields: %s" % (','.join(errors.keys())),
                content=errors
            )
        return cls
