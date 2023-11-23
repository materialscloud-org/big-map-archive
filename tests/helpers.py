# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 BIG MAP Archive.
#
# BIG MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests utils."""

import json

import requests
from flask import current_app
from invenio_oauth2server.models import Token
from invenio_pidstore.models import PersistentIdentifier
from invenio_rdm_records.records.api import RDMDraft
from invenio_rdm_records.services import RDMRecordCommunitiesConfig
from invenio_rdm_records.tokens.scopes import tokens_generate_scope

from big_map_archive.ext import BMArchiveRecordCommunitiesService


def generate_pat_token(
    db,
    uploader,
    client,
    access_token,
    scope=tokens_generate_scope.id,
):
    """Create a personal access token with no expiration data."""
    # expires=datetime.utcnow() + timedelta(hours=10)
    with db.session.begin_nested():
        token_ = Token(
            client_id=client,
            user_id=uploader.id,
            access_token=access_token,
            expires=None,
            is_personal=True,
            is_internal=False,
        )
        db.session.add(token_)
    db.session.commit()

    token_.scopes = [scope]
    return dict(
        token=token_,
        auth_header=[
            ("Authorization", "Bearer {0}".format(token_.access_token)),
        ],
    )


def delete_draft(api, h, id):
    """Delete draft after test"""
    r = requests.delete(f"{api}/api/records/{id}/draft", headers=h, verify=False)
    assert r.status_code == 204


def add_file(h, fh, links, filepath):
    """ Add file to draft """

    # Initiate the file
    filename = filepath.split("/")
    filename = filename[-1]
    data = json.dumps([{"key": filename}])
    r = requests.post(links["files"], data=data, headers=h, verify=False)
    assert r.status_code == 201
    file_links = r.json()["entries"][0]["links"]

    # Upload file content by streaming the data
    with open(filepath, 'rb') as fp:
        r = requests.put(file_links["content"], data=fp, headers=fh, verify=False)
    assert r.status_code == 200

    # Commit the file
    r = requests.post(file_links["commit"], headers=h, verify=False)
    assert r.status_code == 200


def add_community_to_draft(member, community_id, record_id):
    """Add community to draft: create community-submission request

    @param member: user, member of the community
    @param community_id: id of the community
    @param community_id: id of draft
    """

    pid = PersistentIdentifier.get('recid', record_id)
    obj_id = pid.get_assigned_object(object_type='rec')
    record = RDMDraft.get_record(obj_id)

    # Create community submission request and add review in parent
    BMArchiveRecordCommunitiesService(
        config=RDMRecordCommunitiesConfig.build(app=current_app)
    ).add_draft_to_community(member, community_id, record)
