# -*- coding: utf-8 -*-
import os
import stat

import yaml

from .exception import SBackupException


def get_backup_name(name):
    return 'backup-{name}'.format(name=name)


def load_config(filename):
    if not (os.path.isfile(filename) or stat.S_ISFIFO(os.stat(filename).st_mode)):
        raise SBackupException("Can't read the file %s" % filename)
    try:
        with open(filename, 'rt') as file_config:
            return yaml.safe_load(file_config)
    except yaml.YAMLError:
        raise SBackupException("Unable to parse config file, "
                               "config file has to have the YAML format")
    except Exception:
        raise SBackupException("Unexpected error with reading the config file.")
