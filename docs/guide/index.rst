+++++
Usage
+++++

Create backup
=============
This command creates a backup archive containing all paths specified

Example
-------
::

    sbackup create -s /var/www/site1
    Choice backup type (dir): dir
    Choice destination backend (s3): s3
    Enter a Amazon AccessKey: YOUR_ACCESS_KEY
    Enter a Amazon SecretKey: YOUR_SECRET_KEY
    Enter a Amazon BucketName: mybucket

Use a config file
-----------------
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

List
====

::

    sbackup list                                                                                                                                                                                                                                              (env: simple_backup)
    Choice destination backend (s3): s3
    Enter a Amazon AccessKey: YOUR_ACCESS_KEY
    Enter a Amazon SecretKey: YOUR_SECRET_KEY
    Enter a Amazon BucketName: backup_bucket

or config file:
::

    sbackup list -c config.yml

Restore
=======

::

    sbackup restore -c config.yml
    Please, choose a restore task: (site1|site2): site1
    OR
    sbackup restore -f backup-site1.tar.gz -c config.yml                                                                                                                                        (env: simple_backup)
    Please, choose a restore task: (site1|site2): site1

Delete
======

Delete backup
-------------

::

    sbackup delete -c config.yml -f backup-2017-01-16-20-20.tar.gz

Delete older than
-----------------
::

    sbackup delete -c config.yml --older 15

**Remember, if you run the command without option the files older 30 days will be deleted**

Download
========

::

    sbackup download -f backup.tar.gz -dst /home/data -c config.yml
    or
    sbackup download -f backup.tar.gz -dst /home/data
    Choice destination backend (s3): s3
    Enter a Amazon AccessKey: YOUR_ACCESS_KEY
    Enter a Amazon SecretKey: YOUR_SECRET_KEY
    Enter a Amazon BucketName: backup_bucket

