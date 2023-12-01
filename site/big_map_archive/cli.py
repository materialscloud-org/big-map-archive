# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 BIG MAP Archive.
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
from invenio_accounts.proxies import current_datastore
from invenio_communities.members.errors import (AlreadyMemberError,
                                                InvalidMemberError)
from invenio_communities.proxies import current_communities
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.errors import PIDDoesNotExistError, PIDUnregistered
from invenio_pidstore.models import PersistentIdentifier
from invenio_rdm_records.proxies import current_record_communities_service
from invenio_rdm_records.records.api import RDMDraft, RDMRecord
from invenio_rdm_records.services import RDMRecordCommunitiesConfig
from invenio_rdm_records.services.errors import (ReviewExistsError,
                                                 ReviewStateError)
from invenio_records_resources.services.uow import RecordCommitOp, UnitOfWork
from invenio_requests.customizations.actions import RequestActions
from invenio_requests.proxies import current_requests_service
from invenio_requests.records.api import Request
from invenio_search.engine import dsl
# from invenio_users_resources.proxies import current_users_service
from marshmallow.exceptions import ValidationError
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.local import LocalProxy

from big_map_archive.ext import BMArchiveRecordCommunitiesService
from big_map_archive.utils import (change_owner, get_community_from_yaml,
                                   get_community_id, get_user_identity)

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


# add community to record
@records.command("add_community")
@click.argument("slug", type=click.STRING, required=True)
@click.argument("pid_value", type=click.STRING, required=True)
@with_appcontext
def add_to_record(slug, pid_value):
    """ Add record to community.

    Usage: invenio bmarchive records add_community <slug> <record_pid_value>
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
        record = RDMRecord.pid.resolve(pid_value)
    except (PIDDoesNotExistError, PIDUnregistered):
        click.secho(f"ERROR: the community '{slug}' has NOT been added to record {pid_value}, PID does not exist or record is not published.", fg="red")
        return

    # Get owner identity
    owner = record.parent.access.owner.resolve()
    identity = get_user_identity(owner)

    # Make a community-inclusion request
    data = {'communities': [{"id": community_id}]}
    _, errors = current_record_communities_service.add(
        identity, id_=record.pid.pid_value, data=data
    )
    if errors:
        click.secho(f"ERROR: the community '{slug}' has NOT been added to record {pid_value}, {errors}.", fg="red")
        return

    filter_ = dsl.Q("term", **{'topic.record': record.pid.pid_value})
    requests = current_requests_service.scan(system_identity, extra_filter=filter_)

    request_ids = [r["id"] for r in requests]
    assert len(request_ids) == 1
    request_id = request_ids[0]
    request = Request.get_record(request_id)

    with UnitOfWork() as uow:
        # Accept community-inclusion request
        RequestActions.execute(identity, request, "accept", uow=uow)
        request.commit()
        db.session.commit()

        if record.parent["communities"] == {}:
            record.parent["communities"] = {"ids": [community_id], "default": community_id}
        else:
            record.parent["communities"]["ids"].add(community_id)

        record.parent.commit()
        record.commit()
        db.session.commit()

        # re-index record and siblings
        siblings_records = RDMRecord.get_records_by_parent(record.parent)
        for child in siblings_records:
            RecordIndexer().index(child, arguments={"refresh": True})

        # Commit and re-index drafts siblings
        siblings_drafts = RDMDraft.get_records_by_parent(record.parent)
        for child in siblings_drafts:
            if child:
                uow.register(RecordCommitOp(child, indexer=record_indexer_drafts))

    click.secho(f"SUCCESS: the community '{slug}' has been added to record {pid_value}.", fg="green")


@records.command("owner")
@click.argument("pid_value", type=click.STRING, required=True)
@click.argument("email", type=click.STRING, required=True)
@with_appcontext
def change_record_owner(pid_value, email):
    """ Change owner of record.

    Usage: invenio bmarchive records owner <pid_value> <email>
    @param pid_value: record id, ex: 'tqea8-ag515'
    @param email: user email
    """
    if change_owner(pid_value, email, "RDMRecord"):
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


# add user to community
@users.command("add_community")
@click.argument("slug", type=click.STRING, required=True)
@click.argument("role", type=click.Choice(['reader', 'curator', 'owner', 'manager']), required=True)
@click.argument("user_email", type=click.STRING, required=True)
@with_appcontext
def add_community(slug, role, user_email):
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


# update role of a user
@users.command("role")
@click.argument("slug", type=click.STRING, required=True)
@click.argument("role", type=click.Choice(['reader', 'curator', 'owner', 'manager']), required=True)
@click.argument("user_email", type=click.STRING, required=True)
@with_appcontext
def role(slug, role, user_email):
    """Update user role.

    User should already be a member of the community.\n
    Usage: invenio bmarchive users role <slug> <role> <user_email>
    Ex: invenio bmarchive users role bigmap curator myname@materialscloud.org\n
    @param role: user role, type string
    @param user_mail: user email, type string
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
