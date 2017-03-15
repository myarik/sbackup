# -*- coding: utf-8 -*-
import logging
import sys

import click

from .exception import SBackupException
from .task_executor import TaskExecutor
from .utils import load_config


logger = logging.getLogger(__name__)

LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"


def setup_log(ctx, param, value):
    log_level = logging.DEBUG if value else logging.ERROR
    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT
    )


def load_executor(ctx, param, value):
    try:
        config = load_config(value)
        executor = TaskExecutor(config)
    except SBackupException as error:
        logger.error(error.message)
        sys.exit(2)
    except Exception as error:
        logger.error(error)
        sys.exit(2)
    return executor


def choice_task(tasks):
    """
    Args:
        tasks(list): A list of tasks
    Returns:
        task(dict): A task
    Raise:

    """
    if len(tasks) == 1:
        return tasks[0]
    try:
        tasks_position = {task['name']: index for index, task in enumerate(tasks)}
    except KeyError:
        raise SBackupException("Can't find a task name in the configuration file")
    name = click.prompt("Please, choose a restore task: ({})".format('|'.join(tasks_position.keys())),
                        type=click.Choice(tasks_position.keys()))
    return tasks[tasks_position[name]]


# ==================================
# click options

option_config = click.option(
    '-c', '--config', 'executor',
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    default='/etc/sbackup.conf',
    help='Config File',
    callback=load_executor
)
option_debug = click.option(
    '--debug',
    is_flag=True, help='increase output verbosity',
    callback=setup_log
)
option_download_file = click.option(
    '-f', '--backup_file', help='Backup file', required=True)
option_download_path = click.option(
    '-dst', '--dst_path', help='Upload path', required=True)
option_backup_file = click.option('-f', '--backup_file', help='Backup file')
option_delete_older = click.option(
    '--older', default=30, metavar='<int>',
    help='Delete files older than n days'
)

# ==================================
# click commands


@click.group()
def main():
    pass


@main.command()
@option_debug
@option_config
def create(debug, executor):
    """create a backup"""
    executor.create(logger)


@main.command('list')
@option_debug
@option_config
def ls(debug, executor):
    """list of backups"""
    for task in executor.tasks:
        click.echo('Task: %s' % task['name'])
        data = task['dst_backend'].copy()
        backend_name, backend_conf = data.popitem()
        for item in executor.ls(backend_name, backend_conf):
            click.echo(item)


@main.command()
@option_debug
@option_config
@option_backup_file
@option_delete_older
def delete(debug, executor, backup_file, older):
    """Delete backup"""
    if backup_file:
        task = choice_task(executor.tasks)
        backend_name, backend_conf = task['dst_backend'].popitem()
        executor.delete(backend_name, backend_conf, backup_file)
    else:
        for task in executor.tasks:
            backend = task['dst_backend'].copy()
            backend_name, backend_conf = backend.popitem()
            executor.delete_older(backend_name, backend_conf, older)


@main.command()
@option_debug
@option_config
@option_backup_file
def restore(debug, executor, backup_file):
    task = choice_task(executor.tasks)
    executor.restore(task, backup_file)


@main.command()
@option_debug
@option_config
@option_download_file
@option_download_path
def download(debug, executor, backup_file, dst_path):
    task = choice_task(executor.tasks)
    backend_name, backend_conf = task['dst_backend'].popitem()
    try:
        executor.download(backend_name, backend_conf, backup_file, dst_path)
    except SBackupException as error:
        print(error.message)
