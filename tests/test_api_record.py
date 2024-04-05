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


# Drafts
def test_get_draft_minimal(token_com1_reader, token_com1_reader2, token_com2_reader, minimal_record):
    """
    Test: get minimal draft from different identites
    """
    h["Authorization"] = f"Bearer {token_com1_reader}"
    record = deepcopy(minimal_record)

    record["metadata"]["title"] = "Test draft"
    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 201
    id = r.json()['id']

    r = requests.get(f"{api}/api/records/{id}/draft", headers=h, verify=False)
    assert r.status_code == 200

    h["Authorization"] = f"Bearer {token_com1_reader2}"
    r = requests.get(f"{api}/api/records/{id}/draft", headers=h, verify=False)
    assert r.status_code == 403

    h["Authorization"] = f"Bearer {token_com2_reader}"
    r = requests.get(f"{api}/api/records/{id}/draft", headers=h, verify=False)
    assert r.status_code == 403

    h["Authorization"] = ""
    r = requests.get(f"{api}/api/records/{id}/draft", headers=h, verify=False)
    assert r.status_code == 403

    h["Authorization"] = f"Bearer {token_com1_reader}"
    delete_draft(api, h, id)


def test_create_draft_minimal(token_com1_reader, minimal_record):
    """
    Test: create minimal draft: missing publication date and access is public,
    test access is set to restricted, embargo to false and publication_date is set to today.
    At list publication date and access should be in the metadata and access should be set to restricted,
    this metadata cannot be changed from the upload form
    """
    h["Authorization"] = f"Bearer {token_com1_reader}"
    record = deepcopy(minimal_record)

    record["metadata"]["title"] = "Test draft: missing publication date and access is public"
    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)

    assert r.json()['access']['record'] == "restricted"
    assert r.json()['access']['files'] == "restricted"
    assert r.json()['access']['embargo']['active'] == False
    assert r.json()['access']['embargo']['reason'] == None

    assert r.json()['metadata']['publication_date'] == datetime.now().strftime("%Y-%m-%d")

    assert r.status_code == 201
    id = r.json()['id']

    # owner can read the draft
    r = requests.get(f"{api}/api/records/{id}/draft", headers=h, verify=False)
    assert r.status_code == 200

    delete_draft(api, h, id)


def test_create_draft_access(token_com1_reader, minimal_record):
    """
    Test: create draft: with access public and embargo,
    test access is reset to restricted and embargo is set to False
    """
    h["Authorization"] = f"Bearer {token_com1_reader}"
    record = deepcopy(minimal_record)

    record["metadata"]["title"] = "Test draft: reset access and embargo"
    record["metadata"]["access"] = {
        "files": "public",
        "record": "public",
        "embargo": {
            "until": "2124-01-10",
            "active": True,
            "reason": "Test"
        }
    }

    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.json()['access']['record'] == "restricted"
    assert r.json()['access']['files'] == "restricted"
    assert r.json()['access']['embargo']['active'] == False
    assert r.json()['access']['embargo']['reason'] == None

    assert r.status_code == 201

    id = r.json()['id']
    delete_draft(api, h, id)


def test_create_draft_resource_type(token_com1_reader, minimal_record):
    """
    Test: create draft: test resource_type is dataset, software or other
    """
    h["Authorization"] = f"Bearer {token_com1_reader}"

    # invalid resource_type
    record = deepcopy(minimal_record)
    record["metadata"]["title"] = "Test draft: resource_type"
    record["metadata"]["resource_type"] = {
        "id": "image-photo"
    }

    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 400
    assert r.json()["message"] == 'Invalid value image-photo.'

    # valid resource_type
    record = deepcopy(minimal_record)
    record["metadata"]["resource_type"] = {
        "id": "dataset"
    }

    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 201

    id = r.json()['id']
    delete_draft(api, h, id)

    # valid resource_type
    record = deepcopy(minimal_record)
    record["metadata"]["resource_type"] = {
        "id": "software"
    }

    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 201

    id = r.json()['id']
    delete_draft(api, h, id)

    # valid resource_type
    record = deepcopy(minimal_record)
    record["metadata"]["resource_type"] = {
        "id": "other"
    }

    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 201

    id = r.json()['id']
    delete_draft(api, h, id)


def test_create_draft_license(token_com1_reader, minimal_record):
    """
    Test: create draft: test license
    """
    h["Authorization"] = f"Bearer {token_com1_reader}"
    record = deepcopy(minimal_record)
    record["metadata"]["title"] = "Test draft: license"
    record["metadata"]["rights"] = [
        {
            "id": "cc-by-sa-5.0"
        }
    ]

    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 400
    assert r.json()["message"] == 'Invalid value cc-by-sa-5.0.'

    record["metadata"]["rights"] = [
        {
            "id": "mit"
        }
    ]

    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 201

    id = r.json()['id']
    delete_draft(api, h, id)


def test_create_draft_references(token_com1_reader, minimal_record):
    """
    Test: create draft: test references (related_identifiers)
    """
    h["Authorization"] = f"Bearer {token_com1_reader}"
    record = deepcopy(minimal_record)
    record["metadata"]["title"] = "Test draft: references (related_identifiers)"

    # valid reference
    record["metadata"]["related_identifiers"] = [
        {
            "identifier": "https://archive.big-map.eu/",
            "scheme": "url",
            "relation_type": {
                "id": "references",
                "title": {
                    "en": "References"
                }
            }
        }
    ]
    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 201
    id = r.json()['id']
    delete_draft(api, h, id)

    # not valid scheme
    record["metadata"]["related_identifiers"] = [
        {
            "identifier": "10.24435/materialscloud:h2-x6",
            "scheme": "invalid",
            "relation_type": {
                "id": "references"
            }
        }
    ]
    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 400
    assert r.json()["message"] == 'Invalid scheme.'

    record["metadata"]["related_identifiers"] = [
        {
            "identifier": "10.24435/materialscloud:h2-x6",
            "scheme": "",
            "relation_type": {
                "id": "references"
            }
        }
    ]
    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 201
    r.json()["metadata"]["related_identifiers"][0]["scheme"] == "doi"
    id = r.json()['id']
    delete_draft(api, h, id)

    record["metadata"]["related_identifiers"] = [
        {
            "identifier": "10.24435/materialscloud:h2-x6",
            "scheme": " ",
            "relation_type": {
                "id": "references"
            }
        }
    ]
    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 400
    assert r.json()["message"] == 'Invalid scheme.'

    record["metadata"]["related_identifiers"] = [
        {
            "identifier": "10.24435/materialscloud:h2-x6",
            "scheme": None,
            "relation_type": {
                "id": "references"
            }
        }
    ]
    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 201
    r.json()["metadata"]["related_identifiers"][0]["scheme"] == "doi"
    id = r.json()['id']
    delete_draft(api, h, id)

    # None is valid scheme
    record["metadata"]["related_identifiers"] = [
        {
            "identifier": "123",
            "scheme": None,
            "relation_type": {
                "id": "references"
            }
        }
    ]
    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 201
    assert "scheme" not in r.json()["metadata"]["related_identifiers"][0]
    id = r.json()['id']
    delete_draft(api, h, id)

    # not valid identifier
    record["metadata"]["related_identifiers"] = [
        {
            "identifier": "123",
            "scheme": "doi",
            "relation_type": {
                "id": "references"
            }
        }
    ]

    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 400

    record["metadata"]["related_identifiers"] = [
        {
            "identifier": "123",
            "scheme": "arxiv",
            "relation_type": {
                "id": "references"
            }
        }
    ]

    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 400

    record["metadata"]["related_identifiers"] = [
        {
            "identifier": "123",
            "scheme": "isbn",
            "relation_type": {
                "id": "references"
            }
        }
    ]

    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 400

    record["metadata"]["related_identifiers"] = [
        {
            "identifier": "123",
            "scheme": "url",
            "relation_type": {
                "id": "references"
            }
        }
    ]

    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 400


def test_create_draft_with_community(com1_reader, token_com1_reader, minimal_allowed_draft, communities):
    """Test: create draft: with community com1."""

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

    # Attribute draft to com2
    record = deepcopy(minimal_allowed_draft)
    community2 = current_communities.service.search(system_identity, q="slug:com2")
    assert community2
    community2_id = list(community2.hits)[0]["id"]
    assert community2_id

    # Create draft
    record["metadata"]["title"] = "Test draft: draft with no file and community com2"
    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 201
    id = r.json()['id']

    # Add draft to community2: create community-submission request
    # Note: cannot deny to create draft for a community of which the owner does not belong,
    # but can deny to publish it. The draft is accessible via api but not via ui.
    add_community_to_draft(com1_reader, community2_id, id)
    delete_draft(api, h, id)


# Records
# Publish record with no files and no community
def test_publish_record1(com1_reader, token_com1_reader, minimal_allowed_draft):
    """Test: publish record with no files and no community, DENY"""

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
    assert r.status_code == 403
    delete_draft(api, h, id)


# Publish record with no files
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


# Publish record with files and community
def test_publish_record3(com1_reader, token_com1_reader, token_com1_reader2,
                         token_com2_reader, minimal_allowed_draft, communities):
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

    # Member of community can read record
    h["Authorization"] = f"Bearer {token_com1_reader2}"
    r = requests.get(f"{api}/api/records/{id}", headers=h, verify=False)
    assert r.status_code == 200

    # Member not of the same community can not read record
    h["Authorization"] = f"Bearer {token_com2_reader}"
    r = requests.get(f"{api}/api/records/{id}", headers=h, verify=False)
    assert r.status_code == 403


# Publish record with files and community but not description
def test_publish_record4(com1_reader, token_com1_reader, minimal_allowed_draft, communities):
    """Test 4: publish record with file and community without description, DENY.

    Check it is not possible to create record with no description.
    """

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

    record["metadata"]["description"] = ""

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
    assert r.text == '{"status": 400, "message": "A validation error occurred.", "errors": [{"field": "metadata.description", "messages": ["Missing data for required field."]}]}'
    assert r.status_code == 400
    delete_draft(api, h, id)


# Publish record with files and community not the same as the owner
def test_publish_record5(com1_reader, token_com1_reader, token_com1_reader2,
                         token_com2_reader, minimal_allowed_draft, communities):
    """Test 3: publish record with file and community, ALLOW"""

    # record header Authorisation
    h["Authorization"] = f"Bearer {token_com1_reader}"

    # file header Authorisation
    fh["Authorization"] = f"Bearer {token_com1_reader}"

    record = deepcopy(minimal_allowed_draft)

    assert communities
    community2 = current_communities.service.search(system_identity, q="slug:com2")
    assert community2
    community2_id = list(community2.hits)[0]["id"]
    assert community2_id

    record["metadata"]["title"] = "Test publish record: with file and community"

    # Create draft
    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 201
    links = r.json()['links']
    id = r.json()['id']

    # Add draft to community: create community-submission request
    add_community_to_draft(com1_reader, community2_id, id)

    # Add file
    add_file(h, fh, links, filepath)

    # Accept review and publish to community
    links["submit-review"] = f"{links['publish'].rstrip('publish')}submit-review"
    r = requests.post(links["submit-review"], headers=h, verify=False)
    assert r.status_code == 403


# Published record: update access, set access to public
def test_published_record_update_access(com1_reader, token_com1_reader, minimal_allowed_draft, communities):
    """Test: edit published record and set access to public and embargo to True.
    Check access is reset to restricted and embargo to false.
    """

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
    embargo_date = datetime.utcnow() + timedelta(days=1)
    record["access"] = {
        "files": "public",
        "record": "public",
        "embargo": {
            "until": embargo_date.strftime("%Y-%m-%d"),
            "active": True,
            "reason": "Test embargo"
        }
    }
    r = requests.put(links["draft"], data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 200
    # check access is reset to restricted
    assert r.json()['access']['record'] == "restricted"
    assert r.json()['access']['files'] == "restricted"
    assert r.json()['access']['embargo']['active'] == False
    assert r.json()['access']['embargo']['reason'] == None

    # Publish the draft
    r = requests.post(f"{api}/api/records/{id}/draft/actions/publish", headers=h, verify=False)
    assert r.status_code == 202
    assert r.json()['access']['record'] == "restricted"
    assert r.json()['access']['files'] == "restricted"
    assert r.json()['access']['embargo']['active'] == False
    assert r.json()['access']['embargo']['reason'] == None


# Published record: remove community
def test_published_record_update_remove_community(com1_reader, token_com1_reader, minimal_allowed_draft, communities):
    """Test: edit published record and remove community.
    Check it is not possible to remove community.
    """

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

    record["metadata"]["title"] = "Test update published record: remove community"

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

    # Update published record and remove community
    # Create draft from published record
    r = requests.post(links["draft"], headers=h, verify=False)
    assert r.status_code == 201

    # Remove community
    record["metadata"]["title"] = f'{record["metadata"]["title"]} updated3!'
    record["parent"]["communities"] = {}

    r = requests.put(links["draft"], data=json.dumps(record), headers=h, verify=False)
    assert r.status_code == 200
    assert r.json()["parent"]["communities"]["ids"][0] == community1_id
    delete_draft(api, h, id)


# Versions
# New versions of record
# def test_update_published_record3():
#     """Test 2: create new version of published record and set access to public, DENY"""
#     pass

# Access links

# User Records
