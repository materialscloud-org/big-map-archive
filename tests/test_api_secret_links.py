# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 BIG MAP Archive.
#
# BIG MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.


import json

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
