# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 BIG MAP Archive.
#
# BIG MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Drafts/Records APIs tests"""

import json
from copy import deepcopy
from datetime import datetime, timedelta

import requests
from invenio_access.permissions import system_identity
from invenio_app.factory import create_app
from invenio_communities import current_communities

from .helpers import add_community_to_draft, add_file, delete_draft

app = create_app()
ctx = app.app_context()
ctx.push()

filepath = 'tests/fixtures/files/data.json'

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


def test_create_draft1(token_com1_reader, minimal_record):
    """
    Test 1: create minimal draft: missing publication date and access is public, DENY
    at list publication date should be in the metadata and access should be set to restricted
    this metadata cannot be changed in the upload form
    """
    h["Authorization"] = f"Bearer {token_com1_reader}"
    record = deepcopy(minimal_record)

    record["metadata"]["title"] = "Test draft: missing publication date and access is public"
    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 403

    id = r.json()['id']
    delete_draft(api, h, id)


def test_create_draft2(token_com1_reader, minimal_record):
    """
    Test 2: create draft: access is public, DENY
    if access is public and community is restricted: cannot select community in upload form
    """
    h["Authorization"] = f"Bearer {token_com1_reader}"
    record = deepcopy(minimal_record)

    record["metadata"]["title"] = "Test draft: access is public"
    record["metadata"]["publication_date"] = datetime.utcnow().strftime("%Y-%m-%d")
    record["metadata"]["resource_type"] = {"id": "dataset"}
    record["metadata"]["creators"] = [
        {
            "person_or_org": {
                "family_name": "Granata",
                "given_name": "Valeria",
                "type": "personal"
            }
        }
    ]
    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 403

    id = r.json()['id']
    delete_draft(api, h, id)


def test_create_draft3(token_com1_reader, minimal_record):
    """
    Test 3: create draft: access is restricted and embargo is active, DENY
    """
    h["Authorization"] = f"Bearer {token_com1_reader}"
    record = deepcopy(minimal_record)
    record["metadata"]["title"] = "Test draft: access is restricted, embargo is active"
    record["access"] = {
        "files": "restricted",
        "record": "restricted",
        "embargo": {
            "until": None,
            "active": True,
            "reason": None
        }
    }
    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 403

    id = r.json()['id']
    delete_draft(api, h, id)


def test_create_draft4(token_com1_reader, minimal_record):
    """
    Test 4: create draft: access is restricted and embargo is not active, ALLOW
    """
    h["Authorization"] = f"Bearer {token_com1_reader}"
    record = deepcopy(minimal_record)
    record["metadata"]["title"] = "Test draft: access is restricted, embargo is not active"
    record["access"] = {
        "files": "restricted",
        "record": "restricted",
        "embargo": {
            "until": None,
            "active": False,
            "reason": None
        }
    }
    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 201

    id = r.json()['id']
    delete_draft(api, h, id)


def test_create_draft5(com1_reader, token_com1_reader, minimal_allowed_draft, communities):
    """Test 4: create draft: no file and community com1."""

    # record header Authorisation
    h["Authorization"] = f"Bearer {token_com1_reader}"

    # file header Authorisation
    fh["Authorization"] = f"Bearer {token_com1_reader}"

    record = deepcopy(minimal_allowed_draft)

    assert communities

    community1 = current_communities.service.search(system_identity, q="slug:com1")
    assert community1
    community1_id = list(community1.hits)[0]["id"]
    assert community1_id

    # Create draft
    record["metadata"]["title"] = "Test draft: draft with no file and community com1"
    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 201
    id = r.json()['id']

    # Add draft to community1: create community-submission request, ALLOW
    add_community_to_draft(com1_reader, community1_id, id)
    delete_draft(api, h, id)

    # # Create draft
    # record["metadata"]["title"] = "Test draft: draft with no file and community com2"
    # r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    # assert r.status_code == 201
    # links = r.json()['links']
    # id = r.json()['id']

    # # Note: the following is not an API test, it succeeds even for token com1 and community com2, to check
    # # Try to add draft to community2: create community-submission request, DENY
    # community2 = current_communities.service.search(system_identity, q="slug:com2")
    # assert community2
    # community2_id = list(community2.hits)[0]["id"]
    # assert community2_id
    # add_community_to_draft(com1_reader, community2_id, id)


def test_publish_record1(com1_reader, token_com1_reader, minimal_allowed_draft):
    """Test 1: publish record with no files and no community, DENY"""

    # record header Authorisation
    h["Authorization"] = f"Bearer {token_com1_reader}"
    record = deepcopy(minimal_allowed_draft)

    record["metadata"]["title"] = "Test publish record: no files and no community"

    # Create draft
    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 201
    links = r.json()['links']
    id = r.json()['id']

    # Publish the record: do not allow publication with no community and no files
    r = requests.post(links["publish"], headers=h, verify=False)
    assert r.status_code in [400, 500]
    delete_draft(api, h, id)


def test_publish_record2(com1_reader, token_com1_reader, minimal_allowed_draft, communities):
    """Test 2: publish record with no file and with community, DENY"""

    # record header Authorisation
    h["Authorization"] = f"Bearer {token_com1_reader}"

    # file header Authorisation
    fh["Authorization"] = f"Bearer {token_com1_reader}"

    record = deepcopy(minimal_allowed_draft)

    assert communities
    community1 = current_communities.service.search(system_identity, q="slug:com1")
    assert community1
    community1_id = list(community1.hits)[0]["id"]
    assert community1_id

    record["metadata"]["title"] = "Test publish record4: with no file and with community"

    # Create draft
    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 201
    links = r.json()['links']
    id = r.json()['id']

    # Add draft to community: create community-submission request
    add_community_to_draft(com1_reader, community1_id, id)

    # Accept community-submission request and publish to community
    links["submit-review"] = f"{links['publish'].rstrip('publish')}submit-review"
    r = requests.post(links["submit-review"], headers=h, verify=False)
    assert r.status_code == 400
    delete_draft(api, h, id)


def test_publish_record3(com1_reader, token_com1_reader, minimal_allowed_draft, communities):
    """Test 3: publish record with file and community, ALLOW"""

    # record header Authorisation
    h["Authorization"] = f"Bearer {token_com1_reader}"

    # file header Authorisation
    fh["Authorization"] = f"Bearer {token_com1_reader}"

    record = deepcopy(minimal_allowed_draft)

    assert communities
    community1 = current_communities.service.search(system_identity, q="slug:com1")
    assert community1
    community1_id = list(community1.hits)[0]["id"]
    assert community1_id

    record["metadata"]["title"] = "Test publish record: with file and community"

    # Create draft
    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 201
    links = r.json()['links']
    id = r.json()['id']

    # Add draft to community: create community-submission request
    add_community_to_draft(com1_reader, community1_id, id)

    # Add file
    add_file(h, fh, links, filepath)

    # Accept review and publish to community
    links["submit-review"] = f"{links['publish'].rstrip('publish')}submit-review"
    r = requests.post(links["submit-review"], headers=h, verify=False)
    assert r.status_code == 202


def test_update_published_record1(com1_reader, token_com1_reader, minimal_allowed_draft, communities):
    """Test 1: edit published record and set access to public, DENY"""

    # record header Authorisation
    h["Authorization"] = f"Bearer {token_com1_reader}"

    # file header Authorisation
    fh["Authorization"] = f"Bearer {token_com1_reader}"

    record = deepcopy(minimal_allowed_draft)

    assert communities
    community1 = current_communities.service.search(system_identity, q="slug:com1")
    assert community1
    community1_id = list(community1.hits)[0]["id"]
    assert community1_id

    record["metadata"]["title"] = "Test update published record: change access"

    # Create draft
    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 201
    links = r.json()['links']
    id = r.json()['id']

    # Add draft to community: create community-submission request
    add_community_to_draft(com1_reader, community1_id, id)

    # Add file
    add_file(h, fh, links, filepath)

    # Accept review and publish to community
    links["submit-review"] = f"{links['publish'].rstrip('publish')}submit-review"
    r = requests.post(links["submit-review"], headers=h, verify=False)
    assert r.status_code == 202

    # Get the published record
    r = requests.get(f"{api}/api/records/{id}", headers=h, verify=False)
    assert r.status_code == 200
    record = r.json()
    links = record["links"]

    # Update published record and change access to public
    # Create draft from published record
    r = requests.post(links["draft"], headers=h, verify=False)
    assert r.status_code == 201

    # Change access and save the draft
    record["metadata"]["title"] = f'{record["metadata"]["title"]} updated!'
    record["access"] = {
        "files": "public",
        "record": "public",
        "embargo": {
            "until": None,
            "active": False,
            "reason": None
        }
    }
    r = requests.put(links["draft"], data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 403

    # Publish the draft: this will never be executed
    r = requests.post(f"{api}/api/records/{id}/draft/actions/publish", headers=h, verify=False)
    assert r.status_code == 403


def test_update_published_record2(com1_reader, token_com1_reader, minimal_allowed_draft, communities):
    """Test 2: edit published record and set embargo, DENY"""

    # record header Authorisation
    h["Authorization"] = f"Bearer {token_com1_reader}"

    # file header Authorisation
    fh["Authorization"] = f"Bearer {token_com1_reader}"

    record = deepcopy(minimal_allowed_draft)

    assert communities
    community1 = current_communities.service.search(system_identity, q="slug:com1")
    assert community1
    community1_id = list(community1.hits)[0]["id"]
    assert community1_id

    record["metadata"]["title"] = "Test update published record: set embargo"

    # Create draft
    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 201
    links = r.json()['links']
    id = r.json()['id']

    # Add draft to community: create community-submission request
    add_community_to_draft(com1_reader, community1_id, id)

    # Add file to draft
    add_file(h, fh, links, filepath)

    # Accept review and publish to community
    links["submit-review"] = f"{links['publish'].rstrip('publish')}submit-review"
    r = requests.post(links["submit-review"], headers=h, verify=False)
    assert r.status_code == 202

    # Get the published record
    r = requests.get(f"{api}/api/records/{id}", headers=h, verify=False)
    assert r.status_code == 200
    record = r.json()
    links = record["links"]

    # Create draft from published record
    r = requests.post(links["draft"], headers=h, verify=False)
    assert r.status_code == 201

    # Update published record and change access to public, save the draft
    embargo_date = datetime.utcnow() + timedelta(days=1)
    record["metadata"]["title"] = f'{record["metadata"]["title"]} updated!'
    record["access"] = {
        "files": "restricted",
        "record": "restricted",
        "embargo": {
            "until": embargo_date.strftime("%Y-%m-%d"),
            "active": True,
            "reason": "Test embargo"
        }
    }
    r = requests.put(links["draft"], data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 403

    # Publish the draft: this will never be executed
    r = requests.post(f"{api}/api/records/{id}/draft/actions/publish", headers=h, verify=False)
    assert r.status_code == 403


def test_update_published_record3():
    """Test 2: create new version of published record and set access to public, DENY"""
    pass


