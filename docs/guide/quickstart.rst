Usage
=====

*Create a configuration file*
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

*Create a backup*
::

    sbackup create -c config.yml
