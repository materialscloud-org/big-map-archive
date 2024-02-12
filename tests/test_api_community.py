# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 BIG MAP Archive.
#
# BIG MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Communities APIs tests"""

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

# Tests get/add/delete/update community


def test_get_community(token_com1_reader, communities):
    # record header Authorisation
    h["Authorization"] = f"Bearer {token_com1_reader}"

    slug = 'com1'
    r = requests.get(f"{api}/api/communities/{slug}", headers=h, verify=False)
    assert r.status_code == 200

    # can read also info of communities not belonging to because
    # CommunityPermissionPolicy.can_read is set to AnyUser()
    slug = 'com2'
    r = requests.get(f"{api}/api/communities/{slug}", headers=h, verify=False)
    assert r.status_code == 200

    # anuthorised user
    # can read info of community because
    # CommunityPermissionPolicy.can_read is set to AnyUser()
    h["Authorization"] = ""
    r = requests.get(f"{api}/api/communities/{slug}", headers=h, verify=False)
    assert r.status_code == 200


def test_add_community(token_com1_reader, com3):
    # record header Authorisation
    h["Authorization"] = f"Bearer {token_com1_reader}"

    # Create community
    r = requests.post(f"{api}/api/communities", data=json.dumps(com3), headers=h, verify=False)
    assert r.status_code == 403


def test_add_community_public(token_com1_reader, com_public_open):
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

    slug = 'bigmap'
    r = requests.delete(
        f"{api}/api/communities/{slug}", headers=h, verify=False)
    assert r.status_code == 403


def test_update_community(token_com1_reader):
    """Change title and access of community.

    Check it is not possible to update community
    """
    h["Authorization"] = f"Bearer {token_com1_reader}"

    slug = 'com1'

    community1 = current_communities.service.search(system_identity, q=f"slug:{slug}")
    assert community1
    community1_id = list(community1.hits)[0]["id"]
    assert community1_id

    r = requests.get(f"{api}/api/communities/{slug}", headers=h, verify=False)
    assert r.status_code == 200

    com1_new = {}
    # change title
    com1_new["metadata"] = r.json()["metadata"]
    com1_new["metadata"]["title"] = "com1_new"

    # change access
    com1_new["access"] = r.json()["access"]
    com1_new["access"]["visibility"] = "public"
    com1_new["access"]["member_policy"] = "open"

    r = requests.put(
        f"{api}/api/communities/{slug}", data=json.dumps(com1_new), headers=h, verify=False)
    assert r.status_code == 403


def test_rename_slug_community(token_com1_reader):
    """Change slug of community.

    Check it is not possible to change slug
    """
    h["Authorization"] = f"Bearer {token_com1_reader}"

    slug = 'com1'

    community1 = current_communities.service.search(system_identity, q=f"slug:{slug}")
    assert community1
    community1_id = list(community1.hits)[0]["id"]
    assert community1_id

    r = requests.get(f"{api}/api/communities/{slug}", headers=h, verify=False)
    assert r.status_code == 200
    com1_new = {}
    com1_new["slug"] = "com1_new"
    com1_new["metadata"] = r.json()["metadata"]
    com1_new["access"] = r.json()["access"]

    r = requests.post(
        f"{api}/api/communities/{community1_id}/rename", data=json.dumps(com1_new), headers=h, verify=False)
    assert r.status_code == 403


def test_get_communities(token_com1_reader):
    """Get communities.

    CommunityPermissionPolicy.can_read is set to AnyUser() therefore anyone can see communities infos.
    """
    # record header Authorisation
    h["Authorization"] = f"Bearer {token_com1_reader}"

    r = requests.get(f"{api}/api/communities", headers=h, verify=False)
    assert r.status_code == 200
    assert r.json()["hits"]["total"] == 1
    assert r.json()["hits"]["hits"][0]["slug"] == "com1"

    # anuthorised user
    # can not read info of communities even if
    # CommunityPermissionPolicy.can_read is set to AnyUser()
    h["Authorization"] = ""
    r = requests.get(f"{api}/api/communities", headers=h, verify=False)
    assert r.status_code == 403


def test_get_user_communities(token_com1_reader):
    """Get user communities.

    Check user can see only the user communities.
    """
    # record header Authorisation
    h["Authorization"] = f"Bearer {token_com1_reader}"

    r = requests.get(f"{api}/api/user/communities", headers=h, verify=False)
    assert r.status_code == 200
    assert r.json()["hits"]["total"] == 1
    assert r.json()["hits"]["hits"][0]["slug"] == "com1"

    # anuthorised user
    h["Authorization"] = ""
    r = requests.get(f"{api}/api/user/communities", headers=h, verify=False)
    assert r.status_code == 403


def test_update_community_logo(token_com1_reader, token_com2_reader):
    """Update community logo.

    Check user can not update logo.
    """
    # record header Authorisation
    h["Content-Type"] = "application/octet-stream"
    slug = 'com1'

    community1 = current_communities.service.search(system_identity, q=f"slug:{slug}")
    assert community1
    community1_id = list(community1.hits)[0]["id"]
    assert community1_id

    # member of com1
    h["Authorization"] = f"Bearer {token_com1_reader}"
    r = requests.put(f"{api}/api/communities/{community1_id}/logo", headers=h, verify=False)
    assert r.status_code == 403

    # not member of com1
    h["Authorization"] = f"Bearer {token_com2_reader}"
    r = requests.put(f"{api}/api/communities/{community1_id}/logo", headers=h, verify=False)
    assert r.status_code == 403

    # anuthorised user
    h["Authorization"] = ""
    r = requests.put(f"{api}/api/communities/{community1_id}/logo", headers=h, verify=False)
    assert r.status_code == 400

    # reset content-type for next tests
    h["Content-Type"] = "application/json"


# def test_get_community_logo(token_com1_reader, token_com2_reader):
#     """Get community logo.

#     Check user can see logo.
#     To run this test need to upload logo of com1.
#     """
#     # record header Authorisation
#     slug = 'com1'

#     community1 = current_communities.service.search(system_identity, q=f"slug:{slug}")
#     assert community1
#     community1_id = list(community1.hits)[0]["id"]
#     assert community1_id

#     # member of com1
#     h["Authorization"] = f"Bearer {token_com1_reader}"
#     r = requests.get(f"{api}/api/communities/{community1_id}/logo", headers=h, verify=False)
#     assert r.status_code == 200

#     # not member of com1
#     h["Authorization"] = f"Bearer {token_com2_reader}"
#     r = requests.get(f"{api}/api/communities/{community1_id}/logo", headers=h, verify=False)
#     assert r.status_code == 403

#     # anuthorised user
#     h["Authorization"] = ""
#     r = requests.get(f"{api}/api/communities/{community1_id}/logo", headers=h, verify=False)
#     assert r.status_code == 400


# def test_delete_community_logo(token_com1_reader, token_com2_reader):
#     """Delete community logo.

#     Check user can not delete logo.
#     To run this test need to upload logo of com1.
#     """
#     # record header Authorisation
#     slug = 'com1'

#     community1 = current_communities.service.search(system_identity, q=f"slug:{slug}")
#     assert community1
#     community1_id = list(community1.hits)[0]["id"]
#     assert community1_id

#     # member of com1
#     h["Authorization"] = f"Bearer {token_com1_reader}"
#     r = requests.delete(f"{api}/api/communities/{community1_id}/logo", headers=h, verify=False)
#     assert r.status_code == 403

#     # not member of com1
#     h["Authorization"] = f"Bearer {token_com2_reader}"
#     r = requests.delete(f"{api}/api/communities/{community1_id}/logo", headers=h, verify=False)
#     assert r.status_code == 403

#     # anuthorised user
#     h["Authorization"] = ""
#     r = requests.delete(f"{api}/api/communities/{community1_id}/logo", headers=h, verify=False)
#     assert r.status_code == 400


def test_search_communities_featured(token_com1_reader, token_com2_reader):
    """Search communities featured.

    Check user can not search communities featured.
    """
    # member of com1
    h["Authorization"] = f"Bearer {token_com1_reader}"
    r = requests.get(f"{api}/api/communities/featured", headers=h, verify=False)
    assert r.status_code == 200
    assert r.json()["hits"]["total"] == 0

    # not member of com1
    h["Authorization"] = f"Bearer {token_com2_reader}"
    r = requests.get(f"{api}/api/communities/featured", headers=h, verify=False)
    assert r.status_code == 200
    assert r.json()["hits"]["total"] == 0

    # anuthorised user
    h["Authorization"] = ""
    r = requests.get(f"{api}/api/communities/featured", headers=h, verify=False)
    assert r.status_code == 403


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
