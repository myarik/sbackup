Create backup
=============
This command creates a backup archive containing all paths specified

Example
-------
::

    sbackup create -s /var/www/site1 -s /var/www/site2
    Choice backup type: dir
    Choice destination backend: s3
    Enter a Amazon AccessKey: YOUR_ACCESS_KEY
    Enter a Amazon SecretKey: YOUR_SECRET_KEY
    Enter a Amazon BucketName: mybucket

Use a config file
-----------------
::

    sbackup create -s config.yml

*Config example*
::

    - task: Backup dirs
      type: 'dir'
      sources:
        - /var/www/site1
        - /var/www/site2
      dst_backend:
        s3:
           access_key_id: YOUR_ACCESS_KEY
           secret_access_key: YOUR_SECRET_KEY
           bucket: mybucket

