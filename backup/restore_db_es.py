#!/usr/bin/env python -W ignore::DeprecationWarning
"""Restore Prostgres database from dump and Elasticsearch indexes.
Run this in the virtual environment (workon archive)"""

import os
from invenio_app.factory import create_app
from sqlalchemy import create_engine
from invenio_db import db
from sqlalchemy import text

def restore_db(app):
    """ Restore postgres database """
    with app.app_context():
        SQL_USER = app.config.get('SQL_USER')
        SQL_DB = app.config.get('SQL_DB')
        SQL_PASSWORD = app.config.get('SQL_PASSWORD')

        # connect to database template1
        engine = create_engine('postgresql+psycopg2://{}:{}@localhost/template1'.format(SQL_USER, SQL_PASSWORD))
        print(engine)
        # terminate database sessions
        q = text("SELECT pg_terminate_backend(pg_stat_activity.pid)\
        FROM pg_stat_activity\
        WHERE pg_stat_activity.datname = '{}'\
        AND pid <> pg_backend_pid();".format(SQL_DB))
        print(q)
        engine.execute(q)
        print("\033[32m\033[1m" + "Database sessions have been terminated" + "\033[0m")

        # drop database
        q = text('drop database if exists "{}";'.format(SQL_DB))
        engine.execution_options(isolation_level="AUTOCOMMIT").execute(q)
        print("\033[32m\033[1m" + "Database {} has been dropped".format(SQL_DB) + "\033[0m")

        # create database
        q = text('create database "{}";'.format(SQL_DB))
        engine.execution_options(isolation_level="AUTOCOMMIT").execute(q)
        print("\033[32m\033[1m" + "Database {} has been created".format(SQL_DB) + "\033[0m")

        # restore database from dump
        os.system('./restore_db.sh {} {}'.format(SQL_USER, SQL_DB))
        print("\033[32m\033[1m" + "Database dump has been restored" + "\033[0m")


def restore_es():
    """Restore Elastisearch indexes"""
    # destroy indexes if they exist
    os.system('invenio index destroy --force --yes-i-know')

    # create indexes
    os.system('invenio index init')

    # create documents from the database
    # eg, one document per (published) record in rdm_records_metadata table
    os.system('invenio rdm-records rebuild-index')
    os.system('invenio communities rebuild-index')
    print("\033[32m\033[1m" + "Elasticsearch indexes have been restored" + "\033[0m")

def update_files_location(app):
    """Set files location to Object Store container"""
    from datetime import datetime

    with app.app_context():
        db.create_all()
        S3_CONTAINER = app.config.get('S3_CONTAINER')
        now = datetime.now()

        q = text("update files_location set updated='{}', uri='s3://{}' where name='default-location';".format(now, S3_CONTAINER))
        db.engine.execute(q)

        # check update was successful
        q = text("select count(*) from files_location where uri='s3://{}' and name='default-location';".format(S3_CONTAINER))
        results = db.engine.execute(q)
        if results.fetchall()[0][0] == 1:
            print("\033[32m\033[1m" + "Files location has been updated to {}".format(S3_CONTAINER) + "\033[0m")
        else:
            print("\033[32m\033[91m\033[1m" + "ERROR: Files location has NOT been updated to {}".format(S3_CONTAINER) +
                  "\033[0m")


if __name__ == '__main__':
    app = create_app()
    restore_db(app)
    restore_es()
    update_files_location(app)
    print("\033[32m\033[1m"+"Database and elasticsearch indexes have been restored"+"\033[0m")
