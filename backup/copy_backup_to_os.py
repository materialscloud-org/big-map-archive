""" Copy dump file of database from container and backup file of indexes
    to Object store.
    For both database dump and backup file of indexes, this script
    : checks daily dump exists
    : checks daily dump was successfull
    : copies daily dump to the Object store
    : deletes old dumps => keep latest 30 days dumps 
                       => for previous months keep first available dump of the month
"""
import datetime
from datetime import timedelta, date
from invenio_app.factory import create_app
from invenio_db import db

import boto3
import botocore
import hashlib
import urllib.parse
import os
import sys
import subprocess

from dateutil.relativedelta import *

# With botocore version 1.34.0
# need to set addressing_style to virtual and remove the signature_version to execute the actions
# list objects in bucket and delete objects.
# For the operation such as put_object and head_object needs instead to specify signature_version.
def get_s3_client():
    session = boto3.session.Session()
    s3_client = session.client(
        service_name=app.config.get('S3_SIGNATURE_VERSION'),
        aws_access_key_id=app.config.get('S3_ACCESS_KEY_ID'),
        aws_secret_access_key=app.config.get('S3_SECRET_ACCESS_KEY'),
        #aws_session_token=...,  # only used for temporary keys
        endpoint_url=app.config.get('S3_ENDPOINT_URL'),
        region_name='Castor',  # seems optional
        config=botocore.client.Config(s3={'addressing_style': 'virtual'}), # for botocore v1.34.0
    )
    return s3_client


def get_s3_client_with_sig_version():
    session = boto3.session.Session()
    s3_client = session.client(
        service_name=app.config.get('S3_SIGNATURE_VERSION'),
        aws_access_key_id=app.config.get('S3_ACCESS_KEY_ID'),
        aws_secret_access_key=app.config.get('S3_SECRET_ACCESS_KEY'),
        #aws_session_token=...,  # only used for temporary keys
        endpoint_url=app.config.get('S3_ENDPOINT_URL'),
        region_name='Castor',  # seems optional
        config=botocore.client.Config(signature_version=app.config.get('S3_SIGNATURE_VERSION')),
    )
    return s3_client


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def key_exists(bucket, key):
    """Check object exists"""
    s3_client = get_s3_client_with_sig_version()
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            print(f"{key} does not exist.")
        else:
            print(f"Something else went wrong: {e}.")

def copy_dump(app, date):
    """Copy database dump to the Object Store"""

    # dump filepath in docker
    dump_filepath = 'var/lib/postgresql/data'

    # dump filename in docker
    dump_filename = 'big_map_archive_dump.bak'

    # add date to dump filename
    dump_os_filepath = "dump/big_map_archive_dump_{}.bak".format(date)

    with app.app_context():
        db.create_all()

        # get docker id of postgres
        DOCKER_CONTAINER_ID = os.popen('docker ps -aqf "name=big-map-archive-db-1"').read()
        DOCKER_CONTAINER_ID = DOCKER_CONTAINER_ID.rstrip("\n\r")

        # get dump from docker container
        dump = subprocess.check_output('docker exec -i {} pg_restore -l {}/{}'.format(
            DOCKER_CONTAINER_ID, dump_filepath, dump_filename),
                                       shell=True)

        # check dump is the latest
        if "Archive created at {}".format(date) in str(dump):
            print("SUCCESS: dump of day {} exists".format(date))
        else:
            sys.exit("ERROR: dump of day {} does not exist".format(date))

        # copy dump from docker to host
        output = os.system('docker cp {}:{}/big_map_archive_dump.bak .'.format(DOCKER_CONTAINER_ID, dump_filepath))
        if output:
            sys.exit("ERROR: dump of day {} not copied from docker to host".format(date))

        # check dump was successfull
        with open(dump_filename, 'rb') as f:
            fdump = f.read()
            if "PostgreSQL database dump complete" in str(fdump):
                print("SUCCESS: dump of day {} was successfully completed".format(date))
            else:
                sys.exit("ERROR: dump of day {} was not successfully completed".format(date))
        f.close()

        s3_client = get_s3_client_with_sig_version()

        # upload dump on OS
        with open('big_map_archive_dump.bak', 'rb') as f:
            s3_client.put_object(Bucket=app.config.get('S3_CONTAINER'), Key=dump_os_filepath, Body=f)
            print("SUCCESS: dump file '{}' has been successfully uploaded on Object Store".format(dump_os_filepath))
        f.close()


def copy_indexes_dump(app, date):
    """Copy indexes backup to the Object Store"""

    filepath = f"{os.environ['HOME']}/backup_indexes.tar.gz"

    # add date to dump filename
    dump_os_filepath = f"dump/big_map_archive_dump_indexes_{date}.tar.gz"

    s3_client = get_s3_client_with_sig_version()

    # upload indexes backup to OS
    with open(filepath, 'rb') as f:
        s3_client.put_object(Bucket=app.config.get('S3_CONTAINER'), Key=dump_os_filepath, Body=f)
        print("SUCCESS: dump file '{}' has been successfully uploaded on Object Store".format(dump_os_filepath))
    f.close()


def delete_dump(object_path_prefix, object_path_format):
    """ Delete backup of database or indexes older than 30 days ago
        : keep first available dump of every month

    @param object_path_prefix: filename prefix, different for database dump and indexes dump
    @param object_path_format: file extension, different for database dump and indexes dump
    """

    s3_client = get_s3_client()
    dump_times = []

    # date of today
    today = datetime.date.today()
    # TEST
    # today = datetime.datetime.strptime("2023-04-02", '%Y-%m-%d')
    # today = today.date()

    today_backup = f"{object_path_prefix}{today}{object_path_format}"

    # Delete old backups only if today backup has been copied to Object store
    if key_exists(app.config.get('S3_CONTAINER'), today_backup):

        paginator = s3_client.get_paginator('list_objects_v2')

        response_iterator = paginator.paginate(
            Bucket=app.config.get('S3_CONTAINER'),
            Delimiter='/',
            Prefix='dump/',
        )

        for page in response_iterator:
            for key in page['Contents']:
                if "dump/" in key['Key'] and key['Key'] != "dump/":
                    if object_path_prefix in key['Key']:
                        dump_date = key['Key'].replace(object_path_prefix, "").replace(object_path_format, "")
                        try:
                            dump_date = datetime.datetime.strptime(dump_date, '%Y-%m-%d').date()
                            dump_times.append(dump_date)
                        except ValueError:
                            print(f"Filename {key['Key']} does not corresponds to prefix, skipped.")

        dump_times.sort()

        # date of 30 days ago
        today_minus_30d = today - datetime.timedelta(days=30)

        dumps_to_keep = []
        t0 = dump_times[0]

        # keep first dump
        dumps_to_keep.append(t0)

        for i, t in enumerate(dump_times):
            if t < today_minus_30d:
                t1 = t0 + relativedelta(months=+1)
                t1 = t1.strftime('%Y-%m-%d')

                if t1[:t1.rfind('-')] in t.strftime('%Y-%m-%d'):
                    # keep first dump of month after t0
                    dumps_to_keep.append(t)
                    t0 = t
            else:
                dumps_to_keep.append(t)

        dumps_to_remove = list(set(dump_times) - set(dumps_to_keep))
        dumps_to_remove.sort()

        # delete file in OS
        for t in dumps_to_remove:
            t = t.strftime('%Y-%m-%d')
            object_path = f"{object_path_prefix}{t}{object_path_format}"
            s3_client.delete_object(Bucket=app.config.get('S3_CONTAINER'), Key=object_path)
            print("Successfully deleted object {}".format(object_path))
    else:
        print(f"Nothing was deleted because {today_backup} backup does not exist.")


def test_copy_dump():
    start_date = date(2023, 1, 1)
    end_date = date(2023, 4, 3)
    for today in daterange(start_date, end_date):
        copy_indexes_dump(app, today)
        copy_dump(app, today)


if __name__ == '__main__':
    today = datetime.datetime.today()
    today = today.strftime('%Y-%m-%d')
    # today = "2022-02-22" # test

    app = create_app()
    # test_copy_dump()

    # database
    print("Copying dump on Object Store ...")
    copy_dump(app, today)
    print("Latest dump copied on Object Store")
    print("Deleting old dumps from Object Store ...")
    delete_dump("dump/big_map_archive_dump_", ".bak")
    print("Old dumps deleted from Object Store")

    # indexes
    print("Copying indexes backup to Object Store ...")
    copy_indexes_dump(app, today)
    print("Latest indexes backup copied to Object Store")
    print("Deleting old indexes backup from Object Store ...")
    delete_dump("dump/big_map_archive_dump_indexes_", ".tar.gz")
    print("Old indexes backup deleted from Object Store")
