# -*- coding: utf-8 -*-
import click
import sys
import logging

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


@click.group()
def main():
    pass


@click.command()
@click.option('--debug', is_flag=True, help='increase output verbosity')
@click.option('--src', '-s', multiple=True,  help='Path to source dirs')
@click.option('-c', '--config', help='path to config file')
def create(debug, src, config):
    if not src and not config:
        click.echo("Usage: sbackup create -c config.yml or "
                   "sbackup create -s /var/www/site1 -s /var/www/site2")
        return
    setup_log(debug)
    if config:
        try:
            tasks = SBackupCLI.load_config(config, logger)
        except SBackupException as error:
            logger.error(error.message)
            sys.exit(2)
    else:
        task = dict(sources=src)
        task['type'] = click.prompt(
            "Choice backup type (%s)" % '|'.join(TASK_CLASSES.keys()),
            type=click.Choice(TASK_CLASSES.keys()))
        backend_name = click.prompt(
            "Choice destination backend (%s)" % '|'.join(DST_BACKEND.keys()),
            type=click.Choice(DST_BACKEND.keys()))
        task['dst_backends'] = populate_backend_value(backend_name)
        tasks = [task]
    cli = SBackupCLI(tasks)
    cli.create()


@click.command(name='list')
@click.option('--debug', is_flag=True, help='increase output verbosity')
@click.option('-d', '--destination', help='Destination backend (s3)')
@click.option('-c', '--config', help='Configuration file')
def ls(debug, destination, config):
    setup_log(debug)
    if config:
        try:
            tasks = SBackupCLI.load_config(config, logger)
        except SBackupException as error:
            logger.error(error.message)
            sys.exit(2)
        for task in tasks:
            click.echo('Task: %s' % task['task'])
            data = task['dst_backend'].copy()
            backend_name, backend_conf = data.popitem()
            for item in SBackupCLI.ls(backend_name, backend_conf):
                click.echo(item)
    else:
        if not destination:
            destination = click.prompt(
                "Choice destination backend (%s)" % '|'.join(DST_BACKEND.keys()),
                type=click.Choice(DST_BACKEND.keys()))
        data = populate_backend_value(destination.lower())
        backend_name, backend_conf = data.popitem()
        for item in SBackupCLI.ls(backend_name, backend_conf):
            click.echo(item)

main.add_command(create)
main.add_command(ls)
