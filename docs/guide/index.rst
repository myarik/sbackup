+++++
Usage
+++++

Create backup
=============
This command creates a backup

Example
-------
::

    sbackup create -c config.yml

*Config example*
::

    - name: site1
      type: 'dir'
      source: '/var/www/site1'
      dst_backend:
        s3:
           access_key_id: YOUR_ACCESS_KEY
           secret_access_key: YOUR_SECRET_KEY
           bucket: backup_bucket
           location: site1  # optional

List
====
This command lists of backups

::

    sbackup list -c config.yml


Restore
=======
This command extracts the contents of an archive to the source path.

::

    sbackup restore -c config.yml -f backup-test-2017-01-11-10-10.tar.gz

    OR restore from last backup

    sbackup restore -c config.yml

Delete
======
This command deletes an archive from the storage. Also, this command deletes older backups.

Delete backup
-------------

::

    sbackup delete -c config.yml -f backup-test-2017-01-11-10-10.tar.gz

Delete older than
-----------------
::

    sbackup delete -c config.yml --older 15

**Remember, if you run the command without option the files older 30 days will be deleted**

Download
========
This command upload an archive from the storage.
::

    sbackup download -f backup-test-2017-01-11-10-10.tar.gz -dst /home/data -c config.yml
