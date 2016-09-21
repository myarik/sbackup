# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

import click
import sys

from . import SBackupCLI, SBackupException
from .display import Display


@click.command()
@click.argument('filename', nargs=1)
def main(filename):
    """
    Args:
        filename(str): A filename
    """
    cli = SBackupCLI(filename)
    display = Display()
    try:
        cli.run()
    except SBackupException as error:
        display.error(error.message)
        sys.exit(2)

