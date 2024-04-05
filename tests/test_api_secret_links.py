# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 BIG MAP Archive.
#
# BIG MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.


import json
from io import BytesIO

import pytest
import requests
from invenio_access.permissions import system_identity
from invenio_app.factory import create_app
from invenio_pidstore.models import PersistentIdentifier
from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.records.api import RDMDraft, RDMRecord
from invenio_requests import current_requests_service

from .helpers import add_community_to_draft, get_community_id

app = create_app()
ctx = app.app_context()
ctx.push()

api = "https://127.0.0.1:5000"
h = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Bearer <token>"
}
fh = {
    "Accept": "application/json",
    "Content-Type": "application/octet-stream",
    "Authorization": "Bearer <token>"
}


@pytest.fixture()
def service():
    """RDM Record Service."""
    return current_rdm_records.records_service


@pytest.fixture()
def restricted_record(service, minimal_allowed_draft, identity_com1, identity2_com1, identity_com2, com1_reader):
    """Restricted record fixture."""
    data = minimal_allowed_draft.copy()
    data["metadata"]["title"] = "Test api sharelinks"
    # data["files"]["enabled"] = True

    community1_id = get_community_id("com1")
    assert community1_id

    # Create
    draft = service.create(identity_com1, data)

    # Add a file
    service.draft_files.init_files(
        identity_com1, draft.id, data=[{"key": "test.pdf"}]
    )
    service.draft_files.set_file_content(
        identity_com1, draft.id, "test.pdf", BytesIO(b"test file")
    )
    service.draft_files.commit_file(identity_com1, draft.id, "test.pdf")

    # Add draft to community1: create community-submission request, ALLOW
    add_community_to_draft(com1_reader, community1_id, draft.id)

    # Submit community-submission review
    service.review.submit(identity_com1, draft.id)

    # draft = RDMDraft.pid.resolve(draft.id)
    pid = PersistentIdentifier.get(pid_type='recid', pid_value=draft.id)
    draft = RDMDraft.get_record(pid.object_uuid)
    reqid = draft.parent.review.id

    # Accept the request and publish
    current_requests_service.execute_action(system_identity, reqid, "accept", {})

    # # Publish
    # record = service.publish(identity_com1, draft.id)

    # Get published record
    record = RDMRecord.get_record(draft.id)

    # Put published record in edit mode so that draft exists (this is for testing the preview secret link)
    draft = service.edit(identity_com1, record.get("id"))

    return RDMRecord.get_record(record.id)


def api_secret_links_get(token_com1_reader, token_com1_reader2, token_com2_reader, id, link):
    """ Test secret links permissions via API """
    # secret link token
    token = link.data["token"]

    if link.data["permission"] == "view":
        # Record owner
        h["Authorization"] = f"Bearer {token_com1_reader}"
        r = requests.get(f"{api}/api/records/{id}?token={token}", headers=h, verify=False)
        assert r.status_code == 200
        assert r.json()['id'] == id

        # Member of the same community of the record
        h["Authorization"] = f"Bearer {token_com1_reader2}"
        r = requests.get(f"{api}/api/records/{id}?token={token}", headers=h, verify=False)
        assert r.status_code == 200
        assert r.json()['id'] == id

        # Member of a different community of the record
        h["Authorization"] = f"Bearer {token_com2_reader}"
        r = requests.get(f"{api}/api/records/{id}?token={token}", headers=h, verify=False)
        assert r.status_code == 200
        assert r.json()['id'] == id

        # Anonymus
        h["Authorization"] = ""
        r = requests.get(f"{api}/api/records/{id}?token={token}", headers=h, verify=False)
        assert r.status_code == 200
        assert r.json()['id'] == id

    elif link.data["permission"] == "preview":
        # Record owner
        h["Authorization"] = f"Bearer {token_com1_reader}"
        r = requests.get(f"{api}/api/records/{id}?token={token}", headers=h, verify=False)
        assert r.status_code == 200
        assert r.json()['id'] == id

        r = requests.get(f"{api}/api/records/{id}/draft?token={token}", headers=h, verify=False)
        assert r.status_code == 200
        assert r.json()['id'] == id
        assert r.json()['is_draft'] == True

        # Member of the same community of the record
        h["Authorization"] = f"Bearer {token_com1_reader2}"
        r = requests.get(f"{api}/api/records/{id}?token={token}", headers=h, verify=False)
        assert r.status_code == 200
        assert r.json()['id'] == id

        r = requests.get(f"{api}/api/records/{id}/draft?token={token}", headers=h, verify=False)
        assert r.status_code == 200
        assert r.json()['id'] == id
        assert r.json()['is_draft'] == True

        # Member of a different community of the record
        h["Authorization"] = f"Bearer {token_com2_reader}"
        r = requests.get(f"{api}/api/records/{id}?token={token}", headers=h, verify=False)
        assert r.status_code == 200
        assert r.json()['id'] == id

        r = requests.get(f"{api}/api/records/{id}/draft?token={token}", headers=h, verify=False)
        assert r.status_code == 200
        assert r.json()['id'] == id
        assert r.json()['is_draft'] == True

        # Anonymus
        h["Authorization"] = ""
        r = requests.get(f"{api}/api/records/{id}?token={token}", headers=h, verify=False)
        assert r.status_code == 200
        assert r.json()['id'] == id

        r = requests.get(f"{api}/api/records/{id}/draft?token={token}", headers=h, verify=False)
        assert r.status_code == 200
        assert r.json()['id'] == id
        assert r.json()['is_draft'] == True

    elif link.data["permission"] == "edit":
        # Record owner
        h["Authorization"] = f"Bearer {token_com1_reader}"
        r = requests.get(f"{api}/api/records/{id}?token={token}", headers=h, verify=False)
        assert r.status_code == 200
        assert r.json()['id'] == id

        r = requests.get(f"{api}/api/records/{id}/draft?token={token}", headers=h, verify=False)
        assert r.status_code == 200
        assert r.json()['id'] == id
        assert r.json()['is_draft'] == True

        # Member of the same community of the record
        h["Authorization"] = f"Bearer {token_com1_reader2}"
        r = requests.get(f"{api}/api/records/{id}?token={token}", headers=h, verify=False)
        assert r.status_code == 200
        assert r.json()['id'] == id

        r = requests.get(f"{api}/api/records/{id}/draft?token={token}", headers=h, verify=False)
        assert r.status_code == 200
        assert r.json()['id'] == id
        assert r.json()['is_draft'] == True

        # Member of a different community of the record
        h["Authorization"] = f"Bearer {token_com2_reader}"
        r = requests.get(f"{api}/api/records/{id}?token={token}", headers=h, verify=False)
        assert r.status_code == 403

        r = requests.get(f"{api}/api/records/{id}/draft?token={token}", headers=h, verify=False)
        assert r.status_code == 403

        # Anonymus
        h["Authorization"] = ""
        r = requests.get(f"{api}/api/records/{id}?token={token}", headers=h, verify=False)
        assert r.status_code == 403

        r = requests.get(f"{api}/api/records/{id}/draft?token={token}", headers=h, verify=False)
        assert r.status_code == 403


def test_api_secret_links_get(
    service, restricted_record, identity_com1,
    token_com1_reader, token_com1_reader2, token_com2_reader
):
    """ Test secret links permissions via API """
    id_ = restricted_record.get("id")

    view_link = service.access.create_secret_link(
        identity_com1, id_, {"permission": "view"}
    )
    preview_link = service.access.create_secret_link(
        identity_com1, id_, {"permission": "preview"}
    )
    edit_link = service.access.create_secret_link(
        identity_com1, id_, {"permission": "edit"}
    )

    api_secret_links_get(token_com1_reader, token_com1_reader2, token_com2_reader, id_, view_link)
    api_secret_links_get(token_com1_reader, token_com1_reader2, token_com2_reader, id_, preview_link)
    api_secret_links_get(token_com1_reader, token_com1_reader2, token_com2_reader, id_, edit_link)


def test_api_secret_links_create(
    restricted_record, token_com1_reader,
    token_com1_reader2, token_com2_reader
):
    """ Test create secret link via API """
    id_ = restricted_record.get("id")
    data = {"permission": "view"}

    # Record owner
    h["Authorization"] = f"Bearer {token_com1_reader}"
    r = requests.post(f"{api}/api/records/{id_}/access/links", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 201

    # Member of the same community of the record
    h["Authorization"] = f"Bearer {token_com1_reader2}"
    r = requests.post(f"{api}/api/records/{id_}/access/links", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 403

    # Member of a different community of the record
    h["Authorization"] = f"Bearer {token_com2_reader}"
    r = requests.post(f"{api}/api/records/{id_}/access/links", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 403

    # Anonymus
    h["Authorization"] = ""
    r = requests.post(f"{api}/api/records/{id_}/access/links", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 400


def test_api_secret_links_update(
    restricted_record, token_com1_reader,
    token_com1_reader2, token_com2_reader
):
    """ Test update secret link via API """
    id_ = restricted_record.get("id")
    data = {"permission": "view"}

    # Record owner
    h["Authorization"] = f"Bearer {token_com1_reader}"

    # create the link as view
    r = requests.post(f"{api}/api/records/{id_}/access/links", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 201
    link_id = r.json()['id']

    # update the link as preview
    data = {"permission": "preview"}
    r = requests.patch(f"{api}/api/records/{id_}/access/links/{link_id}", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 200

    # update the link as edit
    data = {"permission": "edit"}
    # Member of the same community of the record
    h["Authorization"] = f"Bearer {token_com1_reader2}"
    r = requests.patch(f"{api}/api/records/{id_}/access/links/{link_id}", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 403

    # Member of a different community of the record
    h["Authorization"] = f"Bearer {token_com2_reader}"
    r = requests.patch(f"{api}/api/records/{id_}/access/links/{link_id}", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 403

    # Anonymus
    h["Authorization"] = ""
    r = requests.patch(f"{api}/api/records/{id_}/access/links/{link_id}", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 400


def test_api_secret_links_delete(
    restricted_record, token_com1_reader,
    token_com1_reader2, token_com2_reader
):
    """ Test delete secret link via API """
    id_ = restricted_record.get("id")
    data = {"permission": "view"}

    # Record owner
    h["Authorization"] = f"Bearer {token_com1_reader}"

    # create the link as view
    r = requests.post(f"{api}/api/records/{id_}/access/links", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 201
    link_id = r.json()['id']

    # delete the link as preview
    r = requests.delete(f"{api}/api/records/{id_}/access/links/{link_id}", headers=h, verify=False)
    assert r.status_code == 204

    # create the link as view
    r = requests.post(f"{api}/api/records/{id_}/access/links", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 201
    link_id = r.json()['id']

    # Member of the same community of the record
    h["Authorization"] = f"Bearer {token_com1_reader2}"
    r = requests.delete(f"{api}/api/records/{id_}/access/links/{link_id}", headers=h, verify=False)
    assert r.status_code == 403

    # Member of a different community of the record
    h["Authorization"] = f"Bearer {token_com2_reader}"
    r = requests.delete(f"{api}/api/records/{id_}/access/links/{link_id}", headers=h, verify=False)
    assert r.status_code == 403

    # Anonymus
    h["Authorization"] = ""
    r = requests.delete(f"{api}/api/records/{id_}/access/links/{link_id}", headers=h, verify=False)
    assert r.status_code == 400


def test_api_secret_links_list(
    restricted_record, token_com1_reader,
    token_com1_reader2, token_com2_reader
):
    """ Test list secret links via API """
    id_ = restricted_record.get("id")
    data = {"permission": "view"}

    # Record owner
    h["Authorization"] = f"Bearer {token_com1_reader}"

    # create the link
    r = requests.post(f"{api}/api/records/{id_}/access/links", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 201

    # get links
    r = requests.get(f"{api}/api/records/{id_}/access/links", headers=h, verify=False)
    assert r.status_code == 200

    # Member of the same community of the record
    h["Authorization"] = f"Bearer {token_com1_reader2}"
    r = requests.get(f"{api}/api/records/{id_}/access/links", headers=h, verify=False)
    assert r.status_code == 403

    # Member of a different community of the record
    h["Authorization"] = f"Bearer {token_com2_reader}"
    r = requests.get(f"{api}/api/records/{id_}/access/links", headers=h, verify=False)
    assert r.status_code == 403

    # Anonymus
    h["Authorization"] = ""
    r = requests.get(f"{api}/api/records/{id_}/access/links", headers=h, verify=False)
    assert r.status_code == 403
