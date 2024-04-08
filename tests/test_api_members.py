# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 BIG MAP Archive.
#
# BIG MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

import json

import requests
from invenio_access.permissions import system_identity
from invenio_app.factory import create_app
from invenio_communities import current_communities

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


def get_community1(communities):
    assert communities
    community1 = current_communities.service.search(system_identity, q="slug:com1")
    assert community1
    community1_id = list(community1.hits)[0]["id"]
    assert community1_id
    return community1_id


def test_members_get(token_com1_reader, token_com1_reader2, token_com2_reader, communities):
    """ Test get members """

    id = get_community1(communities)

    for auth in [f"Bearer {token_com1_reader}", f"Bearer {token_com2_reader}", f"Bearer {token_com1_reader2}", ""]:
        h["Authorization"] = auth
        r = requests.get(f"{api}/api/communities/{id}/members", headers=h, verify=False)
        assert r.status_code == 403

        r = requests.get(f"{api}/api/communities/{id}/members/public", headers=h, verify=False)
        assert r.status_code == 403

        r = requests.get(f"{api}/api/communities/{id}/invitations", headers=h, verify=False)
        assert r.status_code == 403


def test_members_post(token_com1_reader, token_com1_reader2, token_com2_reader, communities):
    """ Test post members """

    id = get_community1(communities)

    data = {
        "members": [
            {
                "id": "admin",
                "type": "group"
            }
        ],
        "role": "curator"
    }

    for auth in [f"Bearer {token_com1_reader}", f"Bearer {token_com2_reader}", f"Bearer {token_com1_reader2}"]:
        h["Authorization"] = auth
        r = requests.post(f"{api}/api/communities/{id}/members", data=json.dumps(data), headers=h, verify=False)
        assert r.status_code == 403

    data = {
        "members": [
            {
                "id": "100",
                "type": "user"
            }
        ],
        "role": "reader",
        "message": "<p>Hi</p>"
    }

    for auth in [f"Bearer {token_com1_reader}", f"Bearer {token_com2_reader}", f"Bearer {token_com1_reader2}"]:
        h["Authorization"] = auth
        r = requests.post(f"{api}/api/communities/{id}/invitations", data=json.dumps(data), headers=h, verify=False)
        assert r.status_code == 403


def test_members_delete(token_com1_reader, token_com1_reader2, token_com2_reader, communities):
    """ Test delete members """

    id = get_community1(communities)

    data = {
        "members": [
            {
                "type": "user",
                "id": "1"
            }
        ]
    }

    for auth in [f"Bearer {token_com1_reader}", f"Bearer {token_com2_reader}", f"Bearer {token_com1_reader2}"]:
        h["Authorization"] = auth
        r = requests.delete(f"{api}/api/communities/{id}/members", data=json.dumps(data), headers=h, verify=False)
        assert r.status_code == 403


def test_members_put(token_com1_reader, token_com1_reader2, token_com2_reader, communities):
    """ Test update members """

    id = get_community1(communities)

    data = {
        "members": [
            {
                "id": "1",
                "type": "user"
            }
        ],
        "role": "admin"
    }

    for auth in [f"Bearer {token_com1_reader}", f"Bearer {token_com2_reader}", f"Bearer {token_com1_reader2}"]:
        h["Authorization"] = auth
        r = requests.put(f"{api}/api/communities/{id}/members", data=json.dumps(data), headers=h, verify=False)
        assert r.status_code == 403

    for auth in [f"Bearer {token_com1_reader}", f"Bearer {token_com2_reader}", f"Bearer {token_com1_reader2}"]:
        h["Authorization"] = auth
        r = requests.put(f"{api}/api/communities/{id}/invitations", data=json.dumps(data), headers=h, verify=False)
        assert r.status_code == 403
