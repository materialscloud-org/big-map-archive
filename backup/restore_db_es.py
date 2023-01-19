#!/usr/bin/env python -W ignore::DeprecationWarning
"""Restore Prostgres database from dump and Elasticsearch indexes.
Run this in the virtual environment (workon archive)"""

import os
from invenio_app.factory import create_app
from sqlalchemy import create_engine
from invenio_db import db

def restore_db(app):
    """ Restore postgres database """
    with app.app_context():
        SQL_USER = app.config.get('SQL_USER')
        SQL_DB = app.config.get('SQL_DB')
        SQL_PASSWORD = app.config.get('SQL_PASSWORD')

        # connect to database template1
        engine = create_engine('postgresql+psycopg2://{}:{}@localhost/template1'.format(SQL_USER, SQL_PASSWORD))

        # terminate database sessions
        q = "SELECT pg_terminate_backend(pg_stat_activity.pid)\
        FROM pg_stat_activity\
        WHERE pg_stat_activity.datname = '{}'\
        AND pid <> pg_backend_pid();".format(SQL_DB)
        engine.execute(q)
        print("\033[32m\033[1m" + "Database sessions have been terminated" + "\033[0m")

        # drop database
        q = 'drop database if exists "{}";'.format(SQL_DB)
        engine.execution_options(isolation_level="AUTOCOMMIT").execute(q)
        print("\033[32m\033[1m" + "Database {} has been dropped".format(SQL_DB) + "\033[0m")

        # create database
        q = 'create database "{}";'.format(SQL_DB)
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
    print("\033[32m\033[1m" + "Elasticsearch indexes have been restored" + "\033[0m")


if __name__ == '__main__':
    app = create_app()
    restore_db(app)
    restore_es()
    print("\033[32m\033[1m"+"Database and elasticsearch indexes have been restored"+"\033[0m")