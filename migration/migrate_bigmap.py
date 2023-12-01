# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 BIG MAP Archive.
#
# BIG MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

""" Data migration scripts """

import os

from invenio_app.factory import create_app
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.errors import PIDDeletedError, PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier
from invenio_rdm_records.records.api import RDMDraft, RDMRecord

from big_map_archive.utils import get_emails, get_records


def set_records_access_restricted(record_cls):
    """ Set access restricted to all records (RDMDraft or RDMRecord)

    @param record_cls: class of record (RDMDraft or RDMRecord)
    """
    records = get_records(record_cls)
    for record in records:
        pid_value = record.get("id", None)
        if pid_value:
            set_record_access_restricted(pid_value, record_cls)
            print(f"Record {pid_value} has been set with 'restricted' access to metadata and files.")


def set_record_access_restricted(pid_value, record_cls):
    """ Set access restricted to record (RDMDraft or RDMRecord)

    @param pid_value: pid_value of record
    @param record_cls: class of record (RDMDraft or RDMRecord)
    #TODO move this to utils
    """
    try:
        if record_cls == RDMDraft:
            record_indexer = RecordIndexer(record_cls=RDMDraft, record_to_index=lambda r: (r.index._name, "_doc"))
            record = record_cls.pid.resolve(pid_value, registered_only=False)
        else:
            record_indexer = RecordIndexer()
            record = record_cls.pid.resolve(pid_value)
    except PIDDoesNotExistError:
        print(f"ERROR: record pid {pid_value} does not exist")
        return
    except PIDDeletedError:
        # for deleted drafts the pid does not resolve,
        # need to get the record uuid through the PersistentIdentifier
        # print(f"WARNING: record pid: {pid_value} has pid in status deleted")
        pid = PersistentIdentifier.get('recid', pid_value)
        obj_id = pid.get_assigned_object(object_type='rec')
        record = record_cls.get_record(obj_id)

    access = record.get("access", {})
    access['record'] = 'restricted'
    access['files'] = 'restricted'
    access['embargo'] = {
        "until": None,
        "active": False,
        "reason": None
    }

    record.update({"access": access})
    record.access.refresh_from_dict(record.get("access"))

    record.commit()
    db.session.commit()

    record_indexer.index(record, arguments={"refresh": True})


def set_records_to_community(slug):
    """ Set all records (RDMRecord) to community.

    @param slug: community's slug
    """
    records = get_records(RDMRecord)
    for record in records:
        pid_value = record.get("id", None)
        if pid_value:
            os.system(f'invenio bmarchive records add_community {slug} {pid_value}')


def set_drafts_to_community(slug):
    """ Set all drafts (RDMDraft) to community.

    @param slug: community's slug
    """
    records = get_records(RDMDraft)
    for record in records:
        pid_value = record.get("id", None)
        if pid_value:
            os.system(f'invenio bmarchive drafts add_community {slug} {pid_value}')


def set_users_to_community(slug):
    """Set all users to community.

    @param slug: community's slug
    """
    emails = get_emails()
    for email in emails:
        os.system(f'invenio bmarchive users add_community {slug} reader {email}')


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        if input("\
        This script:\n\
        - sets all records (RDMRecord and RDMDraft) to restricted access \n\
        - sets all records (RDMRecord and RDMDraft) to community bigmap \n\
        - sets all users to community bigmap \n\
        This might take some time.\n\
        Are you sure you want to continue ? (y/n)") != "y":
            exit()

        print("---------------")
        print("Set all records/drafts and files to restricted access")
        print("---------------")
        set_records_access_restricted(RDMRecord)
        set_records_access_restricted(RDMDraft)

        print("---------------")
        print("Set all records to community bigmap")
        print("---------------")
        set_records_to_community(slug='bigmap')
        set_drafts_to_community(slug='bigmap')

        print("---------------")
        print("Set all users to community bigmap")
        print("---------------")
        set_users_to_community(slug='bigmap')
        set_users_to_community(slug='battery2030')
