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


def setup_log(debug):
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT
    )


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
            "Choice backup type %s" % '|'.join(TASK_CLASSES.keys()),
            type=click.Choice(TASK_CLASSES.keys()))
        dest_backend = click.prompt(
            "Choice destination backend %s" % '|'.join(DST_BACKENDS.keys()),
            type=click.Choice(DST_BACKENDS.keys()))
        if dest_backend == 's3':
            task['dst_backends'] = dict(s3=prompt_s3_data())
        tasks = [task]
    cli = SBackupCLI(tasks)
    cli.create()


@click.command()
@click.option('--debug', is_flag=True, help='increase output verbosity')
@click.option('-d', '--destination', help='Destination backend (s3)')
@click.option('-c', '--config', help='Configuration file')
def show(debug, destination, config):
    setup_log(debug)
    dest_list = list()
    if config:
        try:
            tasks = SBackupCLI.load_config(config, logger)
        except SBackupException as error:
            logger.error(error.message)
            sys.exit(2)
        # TODO Change
        for task in tasks:
            for backend in task['dst_backends']:
                dest_list.append(backend)
    else:
        if destination:
            if destination not in DST_BACKENDS.keys():
                click.echo(
                    "The destination backend '{current_value}' "
                    "doesn't support, you can use: {backends}".format(
                        current_value=destination,
                        backends='|'.join(DST_BACKENDS.keys())
                ))
            destination = destination.lower()
        else:
            destination = click.prompt(
                "Choice destination backend %s" % '|'.join(DST_BACKENDS.keys()),
                type=click.Choice(DST_BACKENDS.keys()))
        dest_list.append(dict(s3=prompt_s3_data()))

main.add_command(create)
main.add_command(show)
