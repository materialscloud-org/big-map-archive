# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 BIG MAP Archive.
#
# BIG MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""BIG-MAP Archive utils."""

from invenio_access.permissions import authenticated_user, system_identity
from invenio_access.utils import get_identity
from invenio_accounts.models import User
from invenio_communities.proxies import current_communities
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.errors import PIDDoesNotExistError, PIDUnregistered
from invenio_pidstore.models import PersistentIdentifier
from invenio_rdm_records.records.api import RDMDraft, RDMRecord
from invenio_rdm_records.secret_links import SecretLink
from invenio_rdm_records.services.generators import SecretLinks
from invenio_records_resources.services.uow import RecordCommitOp, unit_of_work
from invenio_requests.proxies import current_requests_service
from invenio_requests.records.api import Request
from invenio_search.engine import dsl
from itsdangerous import SignatureExpired
from sqlalchemy.exc import NoResultFound


def get_communities(include_deleted=False):
    """Get communities."""
    return current_communities.service.search(system_identity, include_deleted=include_deleted)


def get_community_id(slug, include_deleted=False):
    """Get community by slug."""
    # TODO: try this
    # current_communities.service.record_cls.pid.resolve(slug)

    communities = get_communities(include_deleted)
    community_id = None
    for hit in communities.hits:
        community_id = [hit.get('id') for hit in communities.hits if hit.get('slug') == slug]
    return community_id[0] if community_id else None


def get_community_from_yaml(slug):
    """Get community data from app_data/communities.yaml.

    @param slug: slug of community
    returns: data of community as in file app_data/communities.yaml
    """
    import yaml
    communities_vocabulary = open('./app_data/communities.yaml', 'r')
    communities = yaml.safe_load(communities_vocabulary)
    community = next((x for x in communities if x['slug'] == slug), None)
    return community


def get_records(record_cls):
    """Get all records (published or draft).

    record_cls = RDMdraft => for drafts
    record_cls = RDMrecord => for records (published)
    """
    records = []
    for record_metadata in record_cls.model_cls.query.all():
        record = record_cls(record_metadata.data, model=record_metadata)
        records.append(record)
    return records


def get_emails(active=True):
    """Get all users email.

    @param active: True/False to get all active/not active users
    returns: list of emails
    """

    users = User.query.filter_by(active=active).all()
    emails = []
    if users is not None:
        for user in users:
            emails.append(user.email)
    return emails


def get_user_identity(user):
    """Get user identity."""
    identity = get_identity(user)
    identity.provides.add(authenticated_user)
    return identity


def get_secret_link_permission(token):
    """ Get permission level of token

    @param token: token
    @returns: permission level
    """
    try:
        secretlink = SecretLink.get_by_token(token)
    except SignatureExpired:
        return
    return secretlink.permission_level


def record_identity_token_match(record, identity):
    """ Check if any of the identity edit secret links is equal to one of the record.

    @param record: record
    @param identity: identity
    @returns: ids of secret links of identity that match those of the record
    """
    secret_link_need = SecretLinks("edit").needs(record=record)
    secret_links_ids = [n.value for n in secret_link_need if n.method == "link"]
    identity_secret_links_ids = [n.value for n in identity.provides if n.method == "link"]
    return [id_ for id_ in identity_secret_links_ids if id_ in secret_links_ids]


def record_identity_communities_match(record, identity):
    """ Check if any of the identity communities is equal to one of the record communities.

    @param record: record
    @param identity: identity
    @returns: ids of communities of identity that match those of the record
    """
    identity_roles = [n.value for n in identity.provides if n.method == "system_role"]
    if "authenticated_user" not in identity_roles:
        return []

    identity_communities = [n.value for n in identity.provides if n.method == "community"]

    if getattr(record.parent.communities, "ids", None):
        record_communities = record.parent.communities.ids
    else:
        # draft (deny access when review is not set, this is the case of draft with not yet a community selected)
        record_communities = [] if "review" not in record.parent else [str(record.parent.review.receiver.resolve().id)]

    return [identity_community for identity_community in identity_communities
            if identity_community in record_communities]


@unit_of_work()
def change_owner(pid_value, email, record_type, uow):
    """Change owner of record (draft or published record).

    @param pid_value: record id, ex: 'tqea8-ag515'
    @param email: user email
    @param record_type: type of record (record or draft)
    """
    # Get record owner identity
    user = User.query.filter_by(email=email).one()
    identity = get_user_identity(user)
    record_indexer = RecordIndexer()
    record_indexer_drafts = RecordIndexer(record_cls=RDMDraft, record_to_index=lambda r: (r.index._name, "_doc"))
    if record_type == "record":
        try:
            record = RDMRecord.pid.resolve(pid_value)
        except (PIDDoesNotExistError, PIDUnregistered):
            return

    if record_type == "draft":
        try:
            pid = PersistentIdentifier.get('recid', pid_value)
            obj_id = pid.get_assigned_object(object_type='rec')
            record = RDMDraft.get_record(obj_id)
        except (PIDDoesNotExistError, NoResultFound):
            return

    # Update parent
    record.parent.access.owner = {"user": identity.id}

    # Commit parent
    record.parent.commit()

    # Update request with new owner
    filter_ = dsl.Q("term", **{'topic.record': pid_value})
    requests = current_requests_service.scan(system_identity, extra_filter=filter_)

    request_ids = [r["id"] for r in requests]
    if len(request_ids) == 1:
        request_id = request_ids[0]
        request = Request.get_record(request_id)
        request["created_by"] = {"user": str(identity.id)}
        current_requests_service.run_components("update", system_identity, data=request, record=request, uow=uow)
        # Commit and re-index request
        uow.register(RecordCommitOp(request, indexer=current_requests_service.indexer))

    # Commit and re-index records siblings (including record)
    siblings_records = RDMRecord.get_records_by_parent(record.parent)
    for child in siblings_records:
        if child:
            uow.register(RecordCommitOp(child, indexer=record_indexer))

    # Commit and re-index drafts siblings (including record)
    siblings_drafts = RDMDraft.get_records_by_parent(record.parent)
    for child in siblings_drafts:
        if child:
            uow.register(RecordCommitOp(child, indexer=record_indexer_drafts))

    return True


def get_first_version(record):
    """ Get first version of record (including retracted siblings)

    @param record: any sibling of the record
    @returns: first version of record
    """
    siblings = RDMRecord.get_records_by_parent(record.parent)
    record = [child for child in siblings if child.versions.index == 1]
    if not record:
        return
    return record[0]
