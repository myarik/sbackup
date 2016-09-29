# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os

import pytest
from sbackup.sbackup import SBackupCLI, SBackupException


@pytest.fixture(scope='session')
def fake_dir(tmpdir_factory):
    dir = tmpdir_factory.mktemp('data')
    return dir


def test_validate_setting_file(fake_dir):
    obj = SBackupCLI('some_fake_name')
    with pytest.raises(SBackupException):
        obj.run()
    obj = SBackupCLI(fake_dir.dirname)
    with pytest.raises(SBackupException):
        obj.run()
    here = os.path.dirname(__file__)
    fconfig = os.path.join(here, 'fixture/fake_config.yml')
    obj = SBackupCLI(fconfig)
    with pytest.raises(SBackupException):
        obj.run()
    # # TEST
    # fconfig = os.path.join(here, 'fixture/config.yml')
    # obj = SBackupCLI(fconfig)
    # obj.run()
