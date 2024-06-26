# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 - 2024 BIG MAP Archive.
#
# BIG MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""BIG-MAP Archive CLI"""

from datetime import datetime

import click
from flask import current_app
from flask.cli import with_appcontext
from flask_security.confirmable import confirm_user
from invenio_access.permissions import system_identity
from invenio_accounts.models import User
from invenio_accounts.proxies import current_datastore
from invenio_communities.members.errors import (AlreadyMemberError,
                                                InvalidMemberError)
from invenio_communities.proxies import current_communities
from invenio_db import db
from invenio_drafts_resources.services.records.uow import ParentRecordCommitOp
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.errors import PIDDoesNotExistError, PIDUnregistered
from invenio_pidstore.models import PersistentIdentifier
from invenio_rdm_records.proxies import (current_rdm_records,
                                         current_rdm_records_service,
                                         current_record_communities_service)
from invenio_rdm_records.records.api import RDMDraft, RDMRecord
from invenio_rdm_records.requests.community_inclusion import CommunityInclusion
from invenio_rdm_records.services import RDMRecordCommunitiesConfig
from invenio_rdm_records.services.errors import (ReviewExistsError,
                                                 ReviewStateError)
from invenio_records_resources.services.uow import RecordCommitOp, UnitOfWork
from invenio_requests.proxies import current_requests_service
from invenio_requests.records.api import Request
from invenio_search.engine import dsl
# from invenio_users_resources.proxies import current_users_service
from marshmallow.exceptions import ValidationError
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.local import LocalProxy

from big_map_archive.ext import BMArchiveRecordCommunitiesService
from big_map_archive.utils import (change_owner, get_community_from_yaml,
                                   get_community_id, get_first_version,
                                   get_records, get_user_identity)

_datastore = LocalProxy(lambda: current_app.extensions["security"].datastore)


@click.group()
def bmarchive():
    """Invenio BIG-MAP Archive commands."""


################
# Community cli
################
@bmarchive.group()
def communities():
    """Invenio BIG-MAP Archive communities commands."""


def create_community(data):
    """Create a community and attribute the default owner of the community.

    @param data: data of the community
    """
    community_service = current_communities.service
    owner_email = current_app.config["DEFAULT_COMMUNITY_OWNER_MAIL"]
    user = _datastore.get_user(owner_email)

    if not user:
        click.secho(f"ERROR: user {owner_email} does not exist.", fg="red")
        return

    try:
        community = community_service.create(data=data, identity=system_identity)
        logo_path = data.get('logo', None)
        feature = data.get('feature', None)

        # upload logo for community if provided
        if logo_path:
            with open(logo_path, "rb") as filestream:
                community_service.update_logo(system_identity, community.id, filestream)

        if feature:
            featured_data = {"start_date": datetime.utcnow().isoformat()}
            community_service.featured_create(system_identity, community.id, featured_data)

        # add community owner
        member = {
            "type": "user",
            "id": f"{user.id}",
        }

        community_service.members.add(
            system_identity,
            community.id,
            {"members": [member], "role": "owner"},
        )

        click.secho(f"SUCCESS: Created community {data['metadata'].get('title')}.", fg="green")
    except ValidationError as e:
        click.secho(f"ERROR: the community with identifier '{data.get('slug', None)}' has NOT been created. {e}", fg="red")


# create a community
@communities.command("create")
@click.argument("slug", type=click.STRING, required=True)
@with_appcontext
def create(slug):
    """ Create a community and attribute the default owner to the community.

    Usage: invenio bmarchive communities create <slug>\n
    @param slug: community slug
    """
    community = get_community_from_yaml(slug)
    if not community:
        click.secho(f"ERROR: the community with identifier '{slug}' does not exist in file app_data/communities.yaml, add it to this file.", fg="red")
        return
    create_community(community)


# update data of a community
@communities.command("update")
@click.argument("slug", type=click.STRING, required=True)
@with_appcontext
def update(slug):
    """ Update data of a community.

    Usage: invenio bmarchive communities update <slug>\n
    @param slug: community slug
    """
    id = get_community_id(slug)
    if not id:
        click.secho(f"ERROR: the community with identifier '{slug}' does not exist.", fg="red")
        return

    community = get_community_from_yaml(slug)
    if not community:
        click.secho(f"ERROR: the community with identifier '{slug}' does not exist in file app_data/communities.yaml and it has NOT been updated.", fg="red")
        return
    community_service = current_communities.service
    community_service.update(identity=system_identity, id_=id, data=community)

    logo_path = community.get('logo', None)
    if logo_path:
        with open(logo_path, "rb") as filestream:
            community_service.update_logo(system_identity, id, filestream)
    click.secho(f"SUCCESS: the community with identifier '{slug}' has been updated.", fg="green")


# soft delete a community
@communities.command("delete")
@click.argument("slug", type=click.STRING, required=True)
@with_appcontext
def delete(slug):
    """ Delete a community.

    Soft delete: a tumbstone is set for the community.
    Usage: invenio bmarchive communities delete <slug>\n
    @param slug: community slug
    """
    id = get_community_id(slug)
    if not id:
        click.secho(f"ERROR: the community with identifier '{slug}' does not exist.", fg="red")
        return
    community_service = current_communities.service
    community_service.delete(identity=system_identity, id_=id)
    click.secho(f"SUCCESS: the community with identifier '{slug}' has been deleted.", fg="green")


# restore a deleted community
@communities.command("restore")
@click.argument("slug", type=click.STRING, required=True)
@with_appcontext
def restore_community(slug):
    """ Restore a soft deleted community.

    Usage: invenio bmarchive communities restore <slug>\n
    @param slug: community slug
    """
    id = get_community_id(slug, include_deleted=True)
    if not id:
        click.secho(f"ERROR: the community with identifier '{slug}' does not exist.", fg="red")
        return
    community_service = current_communities.service
    community_service.restore_community(identity=system_identity, id_=id)
    click.secho(f"SUCCESS: the community with identifier '{slug}' has been restored.", fg="green")


################
# Record cli
################
@bmarchive.group()
def records():
    """Invenio BIG-MAP Archive records commands."""


def _request(record, community_id):
    """ Get requests of type community-submission or community-inclusion

    @param record: record
    @param community_id: id of community
    returns: requests, type list
    """
    filters = []
    filters.append(dsl.Q("term", **{'topic.record': record.pid.pid_value}))
    filters.append(dsl.Q("term", **{'receiver.community': community_id}))
    filters.append(dsl.Q("terms", **{'type': ["community-submission", "community-inclusion"]}))
    filter_ = dsl.Q("bool", minimum_should_match=1, must=filters)
    requests = current_requests_service.scan(system_identity, extra_filter=filter_)
    return [r for r in requests]


def _commit_reindex_record_and_siblings(record, uow):
    """ Commit and reindex record and siblings (including drafts) """

    record_indexer_drafts = RecordIndexer(record_cls=RDMDraft, record_to_index=lambda r: (r.index._name, "_doc"))

    # Commit and re-index record siblings (including the record itself)
    siblings_records = RDMRecord.get_records_by_parent(record.parent)
    for child in siblings_records:
        uow.register(RecordCommitOp(child, indexer=RecordIndexer()))

    # Commit and re-index drafts siblings
    siblings_drafts = RDMDraft.get_records_by_parent(record.parent)
    for child in siblings_drafts:
        if child:
            uow.register(RecordCommitOp(child, indexer=record_indexer_drafts))


def _add_to_record(slug, pid_value):
    """ Add record to community.

    @param slug: community's slug
    @param pid_value: record id, ex: 'tqea8-ag515'
    """
    community_id = get_community_id(slug)

    if not community_id:
        click.secho(f"ERROR: the community with identifier '{slug}' does not exist.", fg="red")
        return

    try:
        record = RDMRecord.pid.resolve(pid_value)
    except (PIDDoesNotExistError, PIDUnregistered):
        click.secho(f"ERROR: the community '{slug}' has NOT been added to record {pid_value}, PID does not exist or record is not published.", fg="red")
        return

    # Check if community is already added
    if record.parent["communities"]:
        if community_id in record.parent["communities"]["ids"]:
            click.secho(f"WARNING: the community '{slug}' is already added to record {pid_value}.", fg="yellow")
            return

    # Get first version of record (including retracted records)
    record = get_first_version(record)
    # siblings_records = RDMRecord.get_records_by_parent(record.parent)
    # record = [child for child in siblings_records if child.versions.index == 1]
    if not record:
        click.secho(f"ERROR: there is no first version for record {pid_value}.", fg="red")
        return

    # Get request for community_id
    requests = _request(record, community_id)

    # Get owner identity
    owner = record.parent.access.owner.resolve()
    identity = get_user_identity(owner)

    # Add community to record
    # Check a request exists, if not create a community-inclusion request
    if not requests:
        # Make a community-inclusion request
        data = {'communities': [{"id": community_id}]}
        _, errors = current_record_communities_service.add(
            identity, id_=record.pid.pid_value, data=data
        )
        if errors:
            click.secho(f"ERROR: the community '{slug}' has NOT been added to record {pid_value}, {errors}.", fg="red")
            return

        requests = _request(record, community_id)

    assert len(requests) == 1

    with UnitOfWork() as uow:
        request = Request.get_record(requests[0]["id"])

        # Case of first added community that was then deleted. To add it again
        # need to transform the community_submission request to community_inclusion
        # because the record is already published
        if str(request.type) == "community-submission":
            request.type = CommunityInclusion
            uow.register(RecordCommitOp(request, indexer=RecordIndexer()))

        # If the community was removed from the record, change status to submitted
        # otherwise cannot add it again
        if request.status == "declined":
            request.status = "submitted"
            request.commit()
            db.session.commit()
            request = Request.get_record(request.id)

        # Accept community-inclusion request
        # accept request and add row in table rdm_parents_community
        request_item = current_requests_service.execute_action(identity, request.id, "accept", "")
        request = request_item._request
        uow.register(RecordCommitOp(request, indexer=RecordIndexer()))

        if record.parent["communities"] == {}:
            record.parent["communities"] = {"ids": [community_id], "default": community_id}
        else:
            record.parent["communities"]["ids"].append(community_id)
            # set default community to community_id only if it is not yet set
            record.parent["communities"].setdefault("default", community_id)

        record.parent.commit()
        db.session.commit()

        uow.register(ParentRecordCommitOp(record.parent, indexer_context=dict(service=current_rdm_records_service)))
        uow.register(RecordCommitOp(record, indexer=RecordIndexer()))

        _commit_reindex_record_and_siblings(record, uow)

    click.secho(f"SUCCESS: the community '{slug}' has been added to record {pid_value} and all versions of this record, including drafts.", fg="green")


# add community to record
@records.command("add_community")
@click.argument("slug", type=click.STRING, required=True)
@click.argument("pid_value", type=click.STRING, required=False)
@with_appcontext
def add_to_record(slug, pid_value):
    """ Add record to community.

    Usage: invenio bmarchive records add_community <slug> <record_pid_value>
    @param slug: community's slug
    @param pid_value: record id, ex: 'tqea8-ag515', if None the community is added to all records
    Note the default community is the one that defines the permission access in the record ui.
    For the BIG-MAP archive there should be only one community per record and it should be set to default.
    """
    if not pid_value:
        click.secho("INFO: you did not specified a pid_value. "
                    "The command will be executed to all published records and their drafts, "
                    "it does not add the community to drafts never published (is_published=False).", fg="red")
        if click.confirm(f'The community {slug} will be added to ALL records. Do you want to continue? ', abort=True):
            records = get_records(RDMRecord)
            for record in records:
                pid_value = record.get("id", None)
                if pid_value:
                    _add_to_record(slug, pid_value)
        return
    _add_to_record(slug, pid_value)


# remove community from record
@records.command("remove_community")
@click.argument("slug", type=click.STRING, required=True)
@click.argument("pid_value", type=click.STRING, required=True)
@with_appcontext
def remove_from_record(slug, pid_value):
    """ Remove community from record.

    Usage: invenio bmarchive records remove_community <slug> <record_pid_value>
    @param slug: community's slug
    @param pid_value: record id, ex: 'tqea8-ag515'
    Note that the default community is the one that define the permission access to the record ui.
    For the BIG-MAP archive there should be only one community per record and it should be set to default.
    """
    community_id = get_community_id(slug)

    if not community_id:
        click.secho(f"ERROR: the community with identifier '{slug}' does not exist.", fg="red")
        return

    try:
        record = RDMRecord.pid.resolve(pid_value)
    except (PIDDoesNotExistError, PIDUnregistered):
        click.secho(f"ERROR: the community '{slug}' has NOT been added to record {pid_value}, PID does not exist or record is not published.", fg="red")
        return

    if not record.parent["communities"]:
        click.secho(f"WARNING: The record {pid_value} has no communities.", fg="yellow")
        return

    if community_id not in record.parent["communities"]["ids"]:
        click.secho(f"WARNING: The record {pid_value} has no community {slug}.", fg="yellow")
        return

    # Get first version of record (including retracted records)
    record = get_first_version(record)
    if not record:
        click.secho(f"ERROR: there is no first version for record {pid_value}.", fg="red")
        return

    # Check there is a request for the community
    requests = _request(record, community_id)
    if not requests:
        click.secho(f"WARNING: Cannot remove community '{slug}', the record {pid_value} has no request for this community.", fg="yellow")
        return

    assert len(requests) == 1

    # Get owner identity
    owner = record.parent.access.owner.resolve()
    identity = get_user_identity(owner)

    # Remove community from record
    data = {'communities': [{"id": community_id}]}
    _, errors = current_record_communities_service.remove(
        identity, id_=record.pid.pid_value, data=data
    )
    if errors:
        click.secho(f"ERROR: the community '{slug}' has NOT been removed from record {pid_value}, {errors}.", fg="red")
        return

    with UnitOfWork() as uow:
        request = Request.get_record(requests[0]["id"])

        # Case of first added community. Transform the community_submission request
        # to community_inclusion otherwise ince declined it cannot be added again
        # because it creates a review request
        if str(request.type) == "community-submission":
            request.type = CommunityInclusion
            uow.register(RecordCommitOp(request, indexer=RecordIndexer()))

        # If the community was accepted, change status to submitted
        # otherwise cannot remove it
        if request.status == "accepted":
            request.status = "submitted"
            request.commit()
            db.session.commit()
            request = Request.get_record(request.id)

        # Set status declined for community-inclusion requests
        request_item = current_requests_service.execute_action(identity, request.id, "decline", "")
        request = request_item._request
        uow.register(RecordCommitOp(request, indexer=RecordIndexer()))

        # remove community from parent
        record.parent["communities"]["ids"].remove(community_id)

        # remove/update default community in parent
        if not record.parent["communities"]["ids"]:
            record.parent["communities"] = {}
        else:
            # set default to first community of the list
            record.parent["communities"].setdefault("default", record.parent["communities"]["ids"][0])

            if record.parent["communities"]["default"] == community_id:
                record.parent["communities"]["default"] = record.parent["communities"]["ids"][0]

        record.parent.commit()
        db.session.commit()

        uow.register(ParentRecordCommitOp(record.parent, indexer_context=dict(service=current_rdm_records_service)))
        uow.register(RecordCommitOp(record, indexer=RecordIndexer()))

        _commit_reindex_record_and_siblings(record, uow)

    click.secho(f"SUCCESS: the community '{slug}' has been removed from record {pid_value} and all versions of this record, including drafts.", fg="green")


@records.command("delete")
@click.argument("pid_value", type=click.STRING, required=True)
@click.argument("removal_reason", type=click.STRING, required=False)
@click.argument("removal_note", type=click.STRING, required=False)
@click.argument("is_visible", type=click.BOOL, required=False)
@with_appcontext
def delete_record(pid_value, removal_reason, removal_note, is_visible):
    """ Delete published record, put the tumbstone

    REMOVAL_REASON is by default equal to rectracted\n
    IS_VISIBLE is by default equal to True\n
    Usage: invenio bmarchive records delete <record_pid_value> <removal_reason> <removal_note> is_visible\n
    Example: invenio bmarchive records delete vcvw6-yhy88 "retracted" "my note" True\n
    List of removal reasons is here:
    https://github.com/inveniosoftware/invenio-rdm-records/blob/23e3023adde565f53734f61dc1de03234e2e4ff1/invenio_rdm_records/fixtures/data/vocabularies/removal_reasons.yaml#L1
    """
    service = current_rdm_records.records_service
    data = {}
    data["removal_reason"] = {"id": "retracted"}
    if removal_reason:
        data["removal_reason"] = {"id": removal_reason}
    if removal_note:
        data["note"] = removal_note
    if is_visible and isinstance(is_visible, bool):
        data["is_visible"] = is_visible
    try:
        service.delete_record(system_identity, pid_value, data)
    except (PIDDoesNotExistError, PIDUnregistered):
        click.secho(f"ERROR: Cannot delete record '{pid_value}', it is a draft or it does not exist.", fg="red")
        return
    click.secho(f"SUCCESS: the record '{pid_value}' has been deleted.", fg="green")


@records.command("owner")
@click.argument("pid_value", type=click.STRING, required=True)
@click.argument("email", type=click.STRING, required=True)
@click.argument("record_type", type=click.STRING, required=True)
@with_appcontext
def change_record_owner(pid_value, email, record_type):
    """ Change owner of record.

    Usage: invenio bmarchive records owner <pid_value> <email> <record_type>
    @param pid_value: record id, ex: 'tqea8-ag515'
    @param email: user email
    @param record_type: record type: record or draft
    """
    if change_owner(pid_value, email, record_type):
        click.secho(f"SUCCESS: {email} is now owner of record {pid_value} and all versions of this record.", fg="green")
    else:
        click.secho(f"ERROR: an error occured, {email} has NOT been set as owner of record {pid_value} and all versions of this record.", fg="red")


################
# Draft cli
################
@bmarchive.group()
def drafts():
    """Invenio BIG-MAP Archive drafts commands."""


# add community to draft
@drafts.command("add_community")
@click.argument("slug", type=click.STRING, required=True)
@click.argument("pid_value", type=click.STRING, required=True)
@with_appcontext
def add_to_draft(slug, pid_value):
    """ Add draft to community.

    Usage: invenio bmarchive drafts add_community <slug> <record_pid_value>
    @param slug: community's slug
    @param pid_value: record id, ex: 'tqea8-ag515'
    Note: this works only if the community visibility is public
    """
    community_id = get_community_id(slug)
    record_indexer_drafts = RecordIndexer(record_cls=RDMDraft, record_to_index=lambda r: (r.index._name, "_doc"))

    if not community_id:
        click.secho(f"ERROR: the community with identifier '{slug}' does not exist.", fg="red")
        return

    try:
        pid = PersistentIdentifier.get('recid', pid_value)
    except PIDDoesNotExistError:
        click.secho(
            f"ERROR: the community '{slug}' has NOT been added to record {pid_value}. Draft with pid_value: {pid_value} does not exist.", fg="red"
        )
        return

    obj_id = pid.get_assigned_object(object_type='rec')
    try:
        record = RDMDraft.get_record(obj_id)
    except NoResultFound as e:
        click.secho(f"ERROR: the community '{slug}' has NOT been added to record {pid_value}. {e}.", fg="red")
        return

    if not record.metadata.get("title", None):
        click.secho(f"ERROR: the community '{slug}' has NOT been added to record {pid_value}. Draft has no title.", fg="red")
        return

    owner = record.parent.access.owner.resolve()

    # Create community submission request and add review in parent
    try:
        BMArchiveRecordCommunitiesService(
            config=RDMRecordCommunitiesConfig.build(app=current_app)
        ).add_draft_to_community(owner, community_id, record)
    except (ReviewExistsError, ReviewStateError) as e:
        click.secho(f"ERROR: the community '{slug}' has NOT been added to record {pid_value}. {e}", fg="red")
        return

    with UnitOfWork() as uow:
        record.parent.commit()
        record.commit()
        db.session.commit()

        # re-index published siblings, if any
        siblings_records = RDMRecord.get_records_by_parent(record.parent)
        for child in siblings_records:
            if child:
                uow.register(RecordCommitOp(child, indexer=RecordIndexer()))
                # RecordIndexer().index(child, arguments={"refresh": True})

        # Commit and re-index drafts siblings, if any
        siblings_drafts = RDMDraft.get_records_by_parent(record.parent)
        for child in siblings_drafts:
            if child:
                uow.register(RecordCommitOp(child, indexer=record_indexer_drafts))

    click.secho(f"SUCCESS: the community '{slug}' has been added to record {pid_value}.", fg="green")


@drafts.command("owner")
@click.argument("pid_value", type=click.STRING, required=True)
@click.argument("email", type=click.STRING, required=True)
@with_appcontext
def change_draft_owner(pid_value, email):
    """ Change owner of draft.

    Usage: invenio bmarchive drafts owner <pid_value> <email>
    @param pid_value: draft id, ex: 'tqea8-ag515'
    @param email: user email
    """
    if change_owner(pid_value, email, "RDMDraft"):
        click.secho(f"SUCCESS: '{email}' is now owner of draft {pid_value} and all versions of this record.", fg="green")
    else:
        click.secho(f"ERROR: an error occured, '{email}' has NOT been set as owner of draft {pid_value} and all versions of this record.", fg="red")


################
# User cli
################
@bmarchive.group()
def users():
    """Invenio BIG-MAP Archive users commands."""


def _add_community(slug, role, user_email):
    """Add user to community with specified role.

    Usage: invenio bmarchive users add_community <slug> <role> <user_email>\n
    Ex: invenio bmarchive users add_community bigmap reader myname@materialscloud.org\n
    @param slug: community slug, type string\n
    @param user_email: user email, type string\n
    @param role: user role, type string, options: 'reader', 'curator'\n
    """
    community_service = current_communities.service
    member_service = community_service.members

    user = _datastore.get_user(user_email)
    try:
        user.id
    except AttributeError:
        click.secho(f'ERROR: user {user_email} does not exist.', fg="red")
        return

    community_id = get_community_id(slug)
    if not community_id:
        click.secho(f'ERROR: community {slug} does not exist.', fg="red")
        return

    data = {
        "members": [{"type": "user", "id": f"{user.id}"}],
        "role": role,
    }

    try:
        member_service.add(system_identity, community_id, data)
        click.secho(f'SUCCESS: {user_email} has been attributed to community {slug} with role {role}.', fg="green")
    except AlreadyMemberError:
        click.secho(f'WARNING: {user_email} is already a member of the community {slug}.', fg="yellow")


# add user to community
@users.command("add_community")
@click.argument("slug", type=click.STRING, required=True)
@click.argument("role", type=click.Choice(['reader', 'curator', 'owner', 'manager']), required=True)
@click.argument("user_email", type=click.STRING, required=False)
@with_appcontext
def add_community(slug, role, user_email):
    """Add user to community with specified role.

    Usage: invenio bmarchive users add_community <slug> <role> <user_email>\n
    Ex: invenio bmarchive users add_community bigmap reader myname@materialscloud.org\n
    @param slug: community slug, type string\n
    @param user_email: user email, type string\n
    @param role: user role, type string, options: 'reader', 'curator'\n
    """
    if not user_email:
        click.secho("INFO: you did not specified a user email. "
                    "The command will be executed for all users", fg="red")
        if click.confirm(f'The community {slug} will be added to ALL users. Do you want to continue? ', abort=True):
            for user in User.query.all():
                print(user.email)
                user_email = user.email
                if user_email:
                    _add_community(slug, role, user_email)
        return
    _add_community(slug, role, user_email)


# remove user from community
@users.command("remove_community")
@click.argument("slug", type=click.STRING, required=True)
@click.argument("user_email", type=click.STRING, required=True)
@with_appcontext
def remove_from_user(slug, user_email):
    """Remove user from community.

    Usage: invenio bmarchive users remove_community <slug> <user_email>\n
    Ex: invenio bmarchive users remove_community bigmap myname@materialscloud.org\n
    @param slug: community slug, type string\n
    @param user_email: user email, type string\n
    """
    community_service = current_communities.service
    member_service = community_service.members

    user = _datastore.get_user(user_email)
    try:
        user.id
    except AttributeError:
        click.secho(f'ERROR: user {user_email} does not exist.', fg="red")
        return

    community_id = get_community_id(slug)
    if not community_id:
        click.secho(f'ERROR: community {slug} does not exist.', fg="red")
        return

    data = {
        "members": [{"type": "user", "id": f"{user.id}"}],
    }

    try:
        member_service.delete(system_identity, community_id, data)
        click.secho(f'SUCCESS: {user_email} has been removed from community {slug}.', fg="green")
    except InvalidMemberError:
        click.secho(f'WARNING: {user_email} is already not a member of the community {slug}.', fg="yellow")


# list user communities
@users.command("communities")
@click.argument("user_email", type=click.STRING, required=True)
@with_appcontext
def list_user_communities(user_email):
    """List user communities.

    Usage: invenio bmarchive users communities <user_email>\n
    Ex: invenio bmarchive users communities myname@materialscloud.org\n
    @param user_email: user email, type string\n
    """
    community_service = current_communities.service
    member_service = community_service.members

    user = _datastore.get_user(user_email)
    try:
        user.id
    except AttributeError:
        click.secho(f'ERROR: user {user_email} does not exist.', fg="red")
        return

    member_cls = member_service.config.record_cls
    user_communities = member_cls.get_memberships(user)
    if not user_communities:
        click.secho(f'WARNING: {user_email} does not belong to any community.', fg="yellow")

    for user_community in user_communities:
        community_id = user_community[0]
        role = user_community[1]
        community_cls = community_service.record_cls
        slug = community_cls.pid.resolve(community_id).slug
        click.secho(f'{user_email} belongs to community {slug} with role {role}.', fg="green")


# update role of a user
@users.command("role")
@click.argument("slug", type=click.STRING, required=True)
@click.argument("role", type=click.Choice(['reader', 'curator', 'owner', 'manager']), required=True)
@click.argument("user_email", type=click.STRING, required=True)
@with_appcontext
def role(slug, role, user_email):
    """Update user role in community.

    User should already be a member of the community.\n
    Usage: invenio bmarchive users role <slug> <role> <user_email>\n
    Ex: invenio bmarchive users role bigmap curator myname@materialscloud.org\n
    @param role: user role, type string\n
    @param user_mail: user email, type string\n
    https://github.com/inveniosoftware/invenio-communities/blob/890e3e35f98b1a8b55c6817ebcb926b53c91b3e6/invenio_communities/config.py#LL84C1-L84C18
    """
    community_service = current_communities.service
    member_service = community_service.members

    user = _datastore.get_user(user_email)
    try:
        user.id
    except AttributeError:
        click.secho(f'ERROR: User {user_email} does not exist.', fg="red")
        return

    community_id = get_community_id(slug)
    if not community_id:
        click.secho(f'ERROR: community {slug} does not exist.', fg="red")
        return

    data = {
        "members": [{"type": "user", "id": f"{user.id}"}],
        "role": f"{role}"
    }

    try:
        member_service.update(system_identity, community_id, data)
        click.secho(f'SUCCESS: Role {role} has been attributed to {user_email}.', fg="green")
    except ValidationError as e:
        click.secho(f'ERROR: Role {role} has NOT been assigned to {user_email}. {e}', fg="red")
    except InvalidMemberError:
        click.secho(f'ERROR: Role {role} has NOT been assigned to {user_email}. User is not member of the community.', fg="red")


# confirm user
# TODO: check why the reindex_user does not work
# from invenio_users_resources.services.users.tasks import reindex_user
@users.command("confirm_user")
@click.argument("user_email", type=click.STRING, required=True)
@with_appcontext
def confirm_user_cli(user_email):
    """Confirm user email.

    Usage: invenio bmarchive users confirm_user <user_email>
    """
    user = current_datastore.get_user(user_email)
    confirm_user(user)
    db.session.commit()
    # reindex_user([user.id])
    click.secho(f'SUCCESS: User email {user_email} has been confirmed.', fg="green")
