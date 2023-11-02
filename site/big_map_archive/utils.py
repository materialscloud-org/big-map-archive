# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 BIG MAP Archive.
#
# BIG MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""BIG-MAP Archive utils."""

from invenio_access.permissions import system_identity
from invenio_accounts.models import User
from invenio_communities.proxies import current_communities


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
