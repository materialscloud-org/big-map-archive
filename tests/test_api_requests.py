# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 BIG MAP Archive.
#
# BIG MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

import json
import time

import requests
from invenio_app.factory import create_app

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


def get_request(token_com1_reader, record):
    """ Get request id """
    payload = {"q": {f"topic.record: {record.get('id')}"}}

    # Give time for the record fixture to be created and indexed
    time.sleep(1)

    # Record owner
    h["Authorization"] = f"Bearer {token_com1_reader}"
    r = requests.get(f"{api}/api/requests/", params=payload, headers=h, verify=False)
    assert r.status_code == 200
    return r.json()["hits"]["hits"][0]["id"]


def test_api_requests_get(
    restricted_record,
    token_com1_reader,
    token_com1_reader2, token_com2_reader
):
    """ Test get/search requests via API """

    request_id = get_request(token_com1_reader, restricted_record)

    # Record owner
    h["Authorization"] = f"Bearer {token_com1_reader}"
    r = requests.get(f"{api}/api/requests/{request_id}", headers=h, verify=False)
    assert r.status_code == 200

    # Member of the same community of the record
    h["Authorization"] = f"Bearer {token_com1_reader2}"
    r = requests.get(f"{api}/api/requests", headers=h, verify=False)
    assert r.status_code == 200
    r = requests.get(f"{api}/api/requests/{request_id}", headers=h, verify=False)
    assert r.status_code == 200

    # Member of a different community of the record
    h["Authorization"] = f"Bearer {token_com2_reader}"
    r = requests.get(f"{api}/api/requests", headers=h, verify=False)
    assert r.status_code == 200  # can read owned requests
    r = requests.get(f"{api}/api/requests/{request_id}", headers=h, verify=False)
    assert r.status_code == 403  # cannot read request of another community

    # Anonymus
    h["Authorization"] = ""
    r = requests.get(f"{api}/api/requests", headers=h, verify=False)
    assert r.status_code == 403
    r = requests.get(f"{api}/api/requests/{request_id}", headers=h, verify=False)
    assert r.status_code == 403


def test_api_requests_put(
    restricted_record,
    token_com1_reader,
    token_com1_reader2, token_com2_reader
):
    """ Test update requests via API

    Denied for all.
    """
    request_id = get_request(token_com1_reader, restricted_record)

    # Record owner
    h["Authorization"] = f"Bearer {token_com1_reader}"
    r = requests.get(f"{api}/api/requests/{request_id}", headers=h, verify=False)
    assert r.status_code == 200
    request = r.json()
    assert request["status"] == "accepted"
    data = {
        "created_by": request["created_by"],
        "expires_at": request["expires_at"],
        "id": request["id"],
        "number": request["number"],
        "receiver": request["receiver"],
        "revision_id": request["revision_id"],
        "status": request["status"],
        "title": "Changed title",
        "topic": request["topic"],
        "type": request["type"],
    }
    r = requests.put(f"{api}/api/requests/{request_id}", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 403

    # Member of the same community of the record
    h["Authorization"] = f"Bearer {token_com1_reader2}"
    r = requests.put(f"{api}/api/requests/{request_id}", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 403

    # Member of a different community of the record
    h["Authorization"] = f"Bearer {token_com2_reader}"
    r = requests.put(f"{api}/api/requests/{request_id}", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 403

    # Anonymus
    h["Authorization"] = ""
    r = requests.put(f"{api}/api/requests/{request_id}", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 400


def test_api_requests_actions_owner_cancel(
    restricted_draft,
    token_com1_reader
):
    """ Test owner requests actions via API """
    data_cancelled = {
        "payload": {"content": "cancel", "format": "html"}
    }
    request_id = get_request(token_com1_reader, restricted_draft)

    # Record owner
    h["Authorization"] = f"Bearer {token_com1_reader}"
    r = requests.get(f"{api}/api/requests/{request_id}", headers=h, verify=False)
    assert r.status_code == 200
    request = r.json()
    assert request["status"] == "submitted"

    r = requests.post(f"{api}/api/requests/{request_id}/actions/cancel", data=json.dumps(data_cancelled), headers=h, verify=False)
    assert r.status_code == 200
    assert r.json()["status"] == "cancelled"


def test_api_requests_actions_owner_accept(
    restricted_draft,
    token_com1_reader,
):
    """ Test owner requests actions via API """
    data_accepted = {
        "payload": {"content": "accept", "format": "html"}
    }
    request_id = get_request(token_com1_reader, restricted_draft)

    # Record owner
    h["Authorization"] = f"Bearer {token_com1_reader}"
    r = requests.get(f"{api}/api/requests/{request_id}", headers=h, verify=False)
    assert r.status_code == 200
    request = r.json()
    assert request["status"] == "submitted"

    r = requests.post(f"{api}/api/requests/{request_id}/actions/accept", data=json.dumps(data_accepted), headers=h, verify=False)
    assert r.status_code == 200
    assert r.json()["status"] == "accepted"


def test_api_requests_actions_owner_decline(
    restricted_draft,
    token_com1_reader,
):
    """ Test owner requests actions via API """
    data_declined = {
        "payload": {"content": "declined", "format": "html"}
    }
    request_id = get_request(token_com1_reader, restricted_draft)

    # Record owner
    h["Authorization"] = f"Bearer {token_com1_reader}"
    r = requests.get(f"{api}/api/requests/{request_id}", headers=h, verify=False)
    assert r.status_code == 200
    request = r.json()
    assert request["status"] == "submitted"

    r = requests.post(f"{api}/api/requests/{request_id}/actions/decline", data=json.dumps(data_declined), headers=h, verify=False)
    assert r.status_code == 200
    assert r.json()["status"] == "declined"


def test_api_requests_actions_owner_expire(
    restricted_draft,
    token_com1_reader,
):
    """ Test owner requests actions via API """
    data_expired = {
        "payload": {"content": "expired", "format": "html"}
    }
    request_id = get_request(token_com1_reader, restricted_draft)

    # Record owner
    h["Authorization"] = f"Bearer {token_com1_reader}"
    r = requests.get(f"{api}/api/requests/{request_id}", headers=h, verify=False)
    assert r.status_code == 200
    request = r.json()
    assert request["status"] == "submitted"

    r = requests.post(f"{api}/api/requests/{request_id}/actions/expire", data=json.dumps(data_expired), headers=h, verify=False)
    assert r.status_code == 403


def test_api_requests_actions_owner_delete(
    restricted_draft1,
    token_com1_reader,
):
    """ Test owner requests actions via API """
    data_deleted = {
        "payload": {"content": "delete", "format": "html"}
    }
    request_id = get_request(token_com1_reader, restricted_draft1)

    # Record owner
    h["Authorization"] = f"Bearer {token_com1_reader}"
    r = requests.get(f"{api}/api/requests/{request_id}", headers=h, verify=False)
    assert r.status_code == 200
    request = r.json()
    assert request["status"] == "created"

    r = requests.post(f"{api}/api/requests/{request_id}/actions/delete", data=json.dumps(data_deleted), headers=h, verify=False)
    assert r.status_code == 200


def test_api_requests_actions_not_owner(
    restricted_draft,
    token_com1_reader, token_com1_reader2, token_com2_reader
):
    """ Test not owner requests actions via API """
    data = {
        "payload": {"content": "Make this action", "format": "html"}
    }
    request_id = get_request(token_com1_reader, restricted_draft)

    # Record owner
    h["Authorization"] = f"Bearer {token_com1_reader}"
    r = requests.get(f"{api}/api/requests/{request_id}", headers=h, verify=False)
    assert r.status_code == 200
    request = r.json()
    assert request["status"] == "submitted"

    # Member of the same community of the record
    h["Authorization"] = f"Bearer {token_com1_reader2}"
    r = requests.post(f"{api}/api/requests/{request_id}/actions/cancel", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 403

    r = requests.post(f"{api}/api/requests/{request_id}/actions/accept", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 403

    r = requests.post(f"{api}/api/requests/{request_id}/actions/decline", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 403

    r = requests.post(f"{api}/api/requests/{request_id}/actions/expire", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 403

    # Member of a different community of the record
    h["Authorization"] = f"Bearer {token_com2_reader}"
    r = requests.post(f"{api}/api/requests/{request_id}/actions/cancel", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 403

    r = requests.post(f"{api}/api/requests/{request_id}/actions/accept", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 403

    r = requests.post(f"{api}/api/requests/{request_id}/actions/decline", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 403

    r = requests.post(f"{api}/api/requests/{request_id}/actions/expire", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 403

    # Anonymus
    h["Authorization"] = ""
    r = requests.post(f"{api}/api/requests/{request_id}/actions/cancel", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 400

    r = requests.post(f"{api}/api/requests/{request_id}/actions/accept", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 400

    r = requests.post(f"{api}/api/requests/{request_id}/actions/decline", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 400

    r = requests.post(f"{api}/api/requests/{request_id}/actions/expire", data=json.dumps(data), headers=h, verify=False)
    assert r.status_code == 400


def test_api_requests_actions_not_owner_delete(
    restricted_draft1,
    token_com1_reader, token_com1_reader2, token_com2_reader
):
    """ Test not owner requests actions via API """
    data_deleted = {
        "payload": {"content": "delete", "format": "html"}
    }
    request_id = get_request(token_com1_reader, restricted_draft1)

    # Record owner
    h["Authorization"] = f"Bearer {token_com1_reader}"
    r = requests.get(f"{api}/api/requests/{request_id}", headers=h, verify=False)
    assert r.status_code == 200
    request = r.json()
    assert request["status"] == "created"

    # Member of the same community of the record
    h["Authorization"] = f"Bearer {token_com1_reader2}"
    r = requests.post(f"{api}/api/requests/{request_id}/actions/delete", data=json.dumps(data_deleted), headers=h, verify=False)
    assert r.status_code == 403

    # Member of a different community of the record
    h["Authorization"] = f"Bearer {token_com2_reader}"
    r = requests.post(f"{api}/api/requests/{request_id}/actions/delete", data=json.dumps(data_deleted), headers=h, verify=False)
    assert r.status_code == 403

    # Anonymus
    h["Authorization"] = ""
    r = requests.post(f"{api}/api/requests/{request_id}/actions/delete", data=json.dumps(data_deleted), headers=h, verify=False)
    assert r.status_code == 400
