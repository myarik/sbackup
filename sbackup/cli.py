# -*- coding: utf-8 -*-
import click
import sys
import logging
import os

from . import (
    SBackupCLI,
    SBackupException,
    TASK_CLASSES,
    DST_BACKEND
)


logger = logging.getLogger(__name__)

LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"


def prompt_s3_data():
    data = dict()
    data['access_key_id'] = click.prompt("Enter a Amazon AccessKey")
    data['secret_access_key'] = click.prompt("Enter a Amazon SecretKey")
    data['bucket'] = click.prompt("Enter a Amazon BucketName")
    return data


def setup_log(debug):
    log_level = logging.DEBUG if debug else logging.ERROR
    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT
    )


def populate_backend_value(backend_name):
    if backend_name == 's3':
        return dict(s3=prompt_s3_data())
    click.echo("The backend %s doesn't support" % backend_name)
    sys.exit(2)


def load_config(file):
    try:
        return SBackupCLI.load_config(file, logger)
    except SBackupException as error:
        logger.error(error.message)
        sys.exit(2)


@click.group()
def main():
    pass


@click.command()
@click.option('--debug', is_flag=True, help='increase output verbosity')
@click.option('--src', '-s', help='Path to source dirs')
@click.option('-d', '--destination', help='Destination backend (s3)')
@click.option('-c', '--config', help='path to config file')
def create(debug, src, destination, config):
    """create a backup"""
    if not src and not config:
        click.echo("Usage: sbackup create -c config.yml or "
                   "sbackup create -s /var/www/site1")
        return
    setup_log(debug)
    if config:
        tasks = load_config(config)
    else:
        task = dict(source=src)
        task['type'] = click.prompt(
            "Choice backup type (%s)" % '|'.join(TASK_CLASSES.keys()),
            type=click.Choice(TASK_CLASSES.keys()))
        if not destination:
            destination = click.prompt(
                "Choice destination backend (%s)" % '|'.join(DST_BACKEND.keys()),
                type=click.Choice(DST_BACKEND.keys()))
        task['dst_backend'] = populate_backend_value(destination.lower())
        task['name'] = os.path.basename(src)
        tasks = [task]
    SBackupCLI().create(tasks, logger)


@click.command('list')
@click.option('--debug', is_flag=True, help='increase output verbosity')
@click.option('-d', '--destination', help='Destination backend (s3)')
@click.option('-c', '--config', help='Configuration file')
def ls(debug, destination, config):
    """list of backups"""
    setup_log(debug)
    if config:
        tasks = load_config(config)
        for task in tasks:
            click.echo('Task: %s' % task['name'])
            data = task['dst_backend'].copy()
            backend_name, backend_conf = data.popitem()
            for item in SBackupCLI().ls(backend_name, backend_conf):
                click.echo(item)
    else:
        if not destination:
            destination = click.prompt(
                "Choice destination backend (%s)" % '|'.join(DST_BACKEND.keys()),
                type=click.Choice(DST_BACKEND.keys()))
        data = populate_backend_value(destination.lower())
        backend_name, backend_conf = data.popitem()
        for item in SBackupCLI().ls(backend_name, backend_conf):
            click.echo(item)


@click.command()
@click.option('--debug', is_flag=True, help='increase output verbosity')
@click.option('-d', '--destination', help='Destination backend (s3)')
@click.option('-c', '--config', help='Configuration file')
@click.option('-f', '--backup_file', help='A backup file')
@click.option('--older', default=30, metavar='<int>',
              help='Delete files older than n days')
def delete(debug, destination, config, backup_file, older):
    """Delete backup"""
    setup_log(debug)
    if config:
        tasks = load_config(config)
        dst_backends = [task['dst_backend'].copy() for task in tasks]
    else:
        if not destination:
            destination = click.prompt(
                "Choice destination backend ({})".format('|'.join(DST_BACKEND.keys())),
                type=click.Choice(DST_BACKEND.keys()))
        dst_backends = [populate_backend_value(destination.lower())]

    for backend in dst_backends:
        backend_name, backend_conf = backend.popitem()
        if backup_file:
            SBackupCLI().delete(backend_name, backend_conf, backup_file)
        else:
            SBackupCLI().delete_older(backend_name, backend_conf, older)


@click.command()
@click.option('--debug', is_flag=True, help='increase output verbosity')
@click.option('-c', '--config', help='Configuration file', required=True)
@click.option('-f', '--backup_file', help='A backup file')
def restore(debug, config, backup_file):
    setup_log(debug)
    tasks = load_config(config)
    tasks_name = {}
    for position, item in enumerate(tasks):
        tasks_name[item['name']] = position
    task = click.prompt(
        "Please, choose a restore task: ({})".format('|'.join(
            tasks_name.keys())),
        type=click.Choice(tasks_name.keys()))
    restore_task = tasks[tasks_name[task]]
    SBackupCLI().restore(restore_task, backup_file)

main.add_command(create)
main.add_command(ls)
main.add_command(delete)
main.add_command(restore)
