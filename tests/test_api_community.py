# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 BIG MAP Archive.
#
# BIG MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Communities APIs tests"""

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

# Tests get/add/delete/update community

def test_get_community(token_com1_reader, communities):
    # record header Authorisation
    h["Authorization"] = f"Bearer {token_com1_reader}"

    slug = 'com1'
    r = requests.get(f"{api}/api/communities/{slug}", headers=h, verify=False)
    assert r.status_code == 200

    slug = 'com2'
    r = requests.get(f"{api}/api/communities/{slug}", headers=h, verify=False)
    assert r.status_code == 403


def test_add_community(token_com1_reader, com_public_open):
    # record header Authorisation
    h["Authorization"] = f"Bearer {token_com1_reader}"

    # Create community
    r = requests.post(f"{api}/api/communities", data=json.dumps(com_public_open), headers=h, verify=False)
    assert r.status_code == 403


def test_delete_community(token_com1_reader):
    # record header Authorisation
    h["Authorization"] = f"Bearer {token_com1_reader}"

    slug = 'com1'
    r = requests.delete(
        f"{api}/api/communities/{slug}", headers=h, verify=False)
    assert r.status_code == 403


# def test_update_community():
#     """Update settings of community not owned"""
#     pass


# Tests records

def test_remove_records_community1(token_com1_reader):
    """Test 1: remove records from community1, DENY"""
    # record header Authorisation
    h["Authorization"] = f"Bearer {token_com1_reader}"

    r = requests.delete(f"{api}/api/communities/com1/records", headers=h, verify=False)
    assert r.status_code == 403

# # Tests members of community

# def test_member_leave_community():
#     pass

# def test_member_update_role():
#     pass

# def test_member_invite():
#     pass


# # Tests groups

# def test_create_group():
#     pass


# def test_add_group_members():
#     pass