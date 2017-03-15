# -*- coding: utf-8 -*-
import concurrent.futures
import datetime
from collections import MutableMapping

from sbackup.dest_backend import get_backend
from .exception import SBackupException
from .task import TASK_CLASSES


class TaskExecutor:
    """
    This is the main worker class for the executor task
    """

    def __init__(self, tasks):
        """
        Args:
            : An open Bigtable Table instance.
            : A sequence of strings representing the key of each table row
                    to fetch.
        Returns:
            For example:

        Raises:
            IOError: An error occurred accessing the bigtable. Table object.
        """
        if tasks is None:
            raise SBackupException("Can't find a settings")
        elif not isinstance(tasks, list):
            data = [tasks]
        else:
            data = tasks
        for item in data:
            if not isinstance(item, MutableMapping):
                raise SBackupException("Config file must contain either a dictionary of variables, "
                                       "or a list of dictionaries. Got: %s (%s)" % (tasks, type(tasks)))
            self.validate_task(item)
        self.tasks = tasks

    @staticmethod
    def validate_task(task):
        if not task.get('name'):
            raise SBackupException("Incorrect config, can't find a task name")
        if not task.get('dst_backend'):
            raise SBackupException("Incorrect config, can't find a dst_backend")
        if not isinstance(task['dst_backend'], MutableMapping):
            raise SBackupException("The dst_backend value must be a dictionary")

    @staticmethod
    def get_handler(task_type, logger=None):
        if task_type not in TASK_CLASSES:
            error_msg = "Can't work with backup's type {}".format(task_type)
            if logger:
                logger.error(error_msg)
            raise SBackupException(error_msg)
        return TASK_CLASSES[task_type]

    @staticmethod
    def get_backend(backend_name, backend_conf):
        try:
            return get_backend(backend_name, backend_conf)
        except TypeError:
            raise SBackupException('Incorrect a backend configuration')

    def create(self, logger=None, executor_cls=None, max_workers=2):
        executor_cls = executor_cls or concurrent.futures.ThreadPoolExecutor
        future_tasks = {}
        with executor_cls(max_workers=max_workers) as executor:
            for task in self.tasks:
                try:
                    handler = self.get_handler(task['type'], logger)
                except SBackupException:
                    continue
                obj = handler.create_task(task)
                future_tasks[executor.submit(obj.create)] = task['name']
            for future in concurrent.futures.as_completed(future_tasks):
                task_name = future_tasks[future]
                try:
                    future.result()
                except Exception as exc:
                    print('%s generated an exception: %s' % (task_name, exc))
                else:
                    print('Task %s, finished' % task_name)

    def ls(self, backend_name, backend_conf):
        """
        Return generator
        """
        for item in self.get_backend(backend_name, backend_conf):
            yield item

    def restore(self, task, backup_file, logger=None):
        handler = self.get_handler(task['type'], logger)
        obj = handler.create_task(task)
        obj.restore(backup_file)

    def delete(self, backend_name, backend_conf, filename):
        backend = self.get_backend(backend_name, backend_conf)
        backend.delete(filename)

    def delete_older(self, backend_name, backend_conf, retention_period):
        retention_date = datetime.date.today() - datetime.timedelta(retention_period)
        backend = self.get_backend(backend_name, backend_conf)
        backend.delete_older(retention_date)

    def download(self, backend_name, backend_conf, backup_file, dst_path):
        backend = self.get_backend(backend_name, backend_conf)
        backend.download(backup_file, dst_path)
