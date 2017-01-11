# -*- coding: utf-8 -*-
import click
import sys
import logging

from . import SBackupCLI, SBackupException

logger = logging.getLogger(__name__)

LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"


@click.group()
def main():
    pass


@click.command()
@click.option('-d', '--debug', is_flag=True, help='increase output verbosity')
@click.argument('config_file', nargs=1)
def create(debug, config_file):
    if debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT
    )
    cli = SBackupCLI(config_file)
    try:
        cli.run()
    except SBackupException as error:
        logger.error(error.message)
        sys.exit(2)


main.add_command(create)
