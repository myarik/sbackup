# -*- coding: utf-8 -*-
import functools
import abc

from sbackup.exception import SBackupValidationError


class BackendWrapper(metaclass=abc.ABCMeta):

    def validate(self):
        return NotImplementedError('subclasses of BackendWrapper may require a validate() method')

    @abc.abstractclassmethod
    def __iter__(self):
        return NotImplementedError

    @abc.abstractclassmethod
    def upload(self):
        return NotImplementedError

    @abc.abstractclassmethod
    def download(self):
        return NotImplementedError

    @abc.abstractclassmethod
    def delete(self):
        return NotImplementedError


def validated(function):
    @functools.wraps(function)
    def wrapper(self, *args, **kwargs):
        if not self.is_validated:
            raise SBackupValidationError('Run a validate() method before to use a method %s' % function.__name__)
        return function(self, *args, **kwargs)
    return wrapper
