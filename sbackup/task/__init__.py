# -*- coding: utf-8 -*-
from .dir import DirBackupTask

__all__ = (
    'DirBackupTask',
    'TASK_CLASSES'
)

_task_classes = (
    ('dir', DirBackupTask),
)
TASK_CLASSES = dict(_task_classes)
