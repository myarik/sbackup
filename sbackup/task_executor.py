# -*- coding: utf-8 -*-
import datetime
import concurrent.futures


from sbackup.dest_backend import get_backend
from .exception import SBackupException
from .task import TASK_CLASSES


class TaskExecutor:
    """
    This is the main worker class for the executor task
    """
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

    def create(self, tasks, logger=None, executor_cls=None, max_workers=2):
        executor_cls = executor_cls or concurrent.futures.ThreadPoolExecutor
        future_tasks = {}
        with executor_cls(max_workers=max_workers) as executor:
            for task in tasks:
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
