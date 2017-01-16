# -*- coding: utf-8 -*-
from sbackup.exception import SBackupValidationError
from sbackup.dest_backend import DST_BACKENDS


class Field(object):
    def __init__(self, default=None, required=True):
        self.name = None
        self.internal_name = None
        self.default = default
        self.required = required

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = getattr(instance, self.internal_name, self.default)
        if self.required and (value is None or value == list()):
            raise AttributeError("The field %s is required" % self.name)
        return value

    def __set__(self, instance, value):
        setattr(instance, self.internal_name, value)


class Backend(Field):

    def __set__(self, instance, value):
        if not isinstance(value, dict):
            raise SBackupValidationError(
                'The %s has to be a dict' % self.__class__.__name__
            )
        backend = None
        for backend_name, backend_conf in value.items():
            obj = DST_BACKENDS[backend_name]
            try:
                backend = obj(**backend_conf)
            except TypeError:
                raise SBackupValidationError('Incorrect a backend configuration')
        if backend is None:
            raise SBackupValidationError('Incorrect a backend configuration')
        setattr(instance, self.internal_name, backend)


class TaskMetaclass(type):
    """
        This metaclass sets a list named `_fields` on the class.

        Any instances of `Field` included as attributes on either the class
        or on any of its superclasses will be include in the
        `_fields` list.
    """
    def __new__(meta, name, bases, class_dict):
        fields = []
        for field_name, obj in class_dict.items():
            if isinstance(obj, Field):
                obj.name = field_name
                obj.internal_name = '_' + 'hidden_' + field_name
                fields.append(field_name)
        class_dict['_fields'] = tuple(fields)
        cls = type.__new__(meta, name, bases, class_dict)
        return cls


class Task(object, metaclass=TaskMetaclass):
    _fields = ()

    def validate(self):
        errors = dict()
        for field in self.get_fields():
            validate_method = getattr(self, 'validate_' + field, None)
            attr = getattr(self, field)
            if attr is not None:
                try:
                    if validate_method and callable(validate_method):
                        setattr(self, field, validate_method(attr))
                    if callable(getattr(attr, 'validate', None)):
                        attr.validate()
                except SBackupValidationError as error:
                    errors[field] = error.message
        if errors:
            raise SBackupValidationError(
                message="Can't validate fields: %s" % (','.join(errors.keys())),
                content=errors
            )

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
        """
        obj = cls()
        for field in obj.get_fields():
            value = attrs.get(field)
            if not value:
                continue
            setattr(obj, field, value)
        return obj

    def run(self):
        return NotImplementedError
