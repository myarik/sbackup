# -*- coding: utf-8 -*-
import functools

from sbackup.exception import SBackupValidationError


class BackendWrapper(object):

    def validate(self):
        return NotImplementedError('subclasses of BackendWrapper may require a validate() method')


def validated(function):
    @functools.wraps(function)
    def wrapper(self, *args, **kwargs):
        if not self.is_validated:
            raise SBackupValidationError('Run a validate() method before to use a method %s' % function.__name__)
        return function(self, *args, **kwargs)
    return wrapper
