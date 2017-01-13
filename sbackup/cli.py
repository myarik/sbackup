# -*- coding: utf-8 -*-
import click
import sys
import logging

from . import (
    SBackupCLI,
    SBackupException,
    TASK_CLASSES,
    DST_BACKENDS
)

logger = logging.getLogger(__name__)

LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"


def prompt_s3_data():
    data = dict()
    data['access_key_id'] = click.prompt("Enter a Amazon AccessKey")
    data['secret_access_key'] = click.prompt("Enter a Amazon SecretKey")
    data['bucket'] = click.prompt("Enter a Amazon BucketName")
    return data


@click.group()
def main():
    pass


@click.command()
@click.option('-d', '--debug', is_flag=True, help='increase output verbosity')
@click.option('--src', '-s', multiple=True,  help='Source dirs')
@click.option('-c', '--config', help='Configuration file')
def create(debug, src, config):
    if not src and not config:
        click.echo("Usage: sbackup create -c config.yml or "
                   "sbackup create -s /var/www/site1 -s /var/www/site2")
        return
    if debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT
    )
    if config:
        try:
            tasks = SBackupCLI.load_config(config, logger)
        except SBackupException as error:
            logger.error(error.message)
            sys.exit(2)
    else:
        task = dict(sources=src)
        task['type'] = click.prompt(
            "Choice backup type", type=click.Choice(TASK_CLASSES.keys()))
        dest_backend = click.prompt(
            "Choice destination backend", type=click.Choice(DST_BACKENDS.keys()))
        if dest_backend == 's3':
            task['dst_backends'] = dict(s3=prompt_s3_data())
        tasks = [task]
    cli = SBackupCLI(tasks)
    cli.create()

main.add_command(create)
