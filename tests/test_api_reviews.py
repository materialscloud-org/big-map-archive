# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 BIG MAP Archive.
#
# BIG MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Review APIs tests"""

import json
from copy import deepcopy

import requests
from invenio_access.permissions import system_identity
from invenio_app.factory import create_app
from invenio_communities import current_communities

from .helpers import add_file

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


def test_get_create_submit_review(token_com1_reader, minimal_allowed_draft):
    """
    Test get, create, submit review request:
        - create minimal draft
        - add review
        - add a file to draft
        - publish draft
    """
    h["Authorization"] = f"Bearer {token_com1_reader}"

    # File header Authorisation
    fh["Authorization"] = f"Bearer {token_com1_reader}"

    # Get communities 1 and 2
    community1 = current_communities.service.search(system_identity, q="slug:com1")
    assert community1
    community1_id = list(community1.hits)[0]["id"]
    assert community1_id

    community2 = current_communities.service.search(system_identity, q="slug:com2")
    assert community2
    community2_id = list(community2.hits)[0]["id"]
    assert community2_id

    for community_id in [community1_id, community2_id]:
        record = deepcopy(minimal_allowed_draft)

        record["metadata"]["title"] = f"Test draft: review {community_id}"
        r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)

        assert r.status_code == 201
        links = r.json()['links']
        id = r.json()['id']
        review = {
            "receiver": {
                "community": community_id
            },
            "type": "community-submission"
        }

        # Create review request
        r = requests.put(f"{api}/api/records/{id}/draft/review", data=json.dumps(review), headers=h, verify=False)
        assert r.status_code == 200
        assert r.json()["status"] == "created"
        assert r.json()["receiver"]["community"] == community_id
        assert r.json()["topic"]["record"] == id

        # Get review request
        r = requests.get(f"{api}/api/records/{id}/draft/review", headers=h, verify=False)
        assert r.status_code == 200

        # Add file
        add_file(h, fh, links, filepath)

        # Submit draft for review, accept review and publish the draft because the community has review_policy open
        r = requests.post(f"{api}/api/records/{id}/draft/actions/submit-review", headers=h, verify=False)

        # In case of com2 the draft is not published, the request is submitted but not accepted because identity
        # is not member of com2. The created draft for com2 can be accessed via api but not via ui.
        if community_id == community1_id:
            assert r.status_code == 202
        else:
            assert r.status_code == 403


def test_accept_review(token_com1_reader, token_com2_reader, minimal_allowed_draft):
    """ Test create and submit review request by member of a community different from the record """

    h["Authorization"] = f"Bearer {token_com1_reader}"

    # File header Authorisation
    fh["Authorization"] = f"Bearer {token_com1_reader}"

    community2 = current_communities.service.search(system_identity, q="slug:com2")
    assert community2
    community2_id = list(community2.hits)[0]["id"]
    assert community2_id

    record = deepcopy(minimal_allowed_draft)

    record["metadata"]["title"] = f"Test draft: review {community2_id}"
    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)

    assert r.status_code == 201
    links = r.json()['links']
    id = r.json()['id']
    review = {
        "receiver": {
            "community": community2_id
        },
        "type": "community-submission"
    }

    # Create review request
    r = requests.put(f"{api}/api/records/{id}/draft/review", data=json.dumps(review), headers=h, verify=False)
    assert r.status_code == 200
    assert r.json()["status"] == "created"
    assert r.json()["receiver"]["community"] == community2_id
    assert r.json()["topic"]["record"] == id

    # Add file
    add_file(h, fh, links, filepath)

    # Cannot accept review request because not member of records's community
    r = requests.post(f"{api}/api/records/{id}/draft/actions/submit-review", headers=h, verify=False)
    assert r.status_code == 403

    # Cannot accept review request because not owner of the record
    h["Authorization"] = f"Bearer {token_com2_reader}"
    r = requests.post(f"{api}/api/records/{id}/draft/actions/submit-review", headers=h, verify=False)
    assert r.status_code == 403

    # Cannot accept review request because not authenticated
    h["Authorization"] = ""
    r = requests.post(f"{api}/api/records/{id}/draft/actions/submit-review", headers=h, verify=False)
    assert r.status_code == 400


def test_publish(token_com1_reader, token_com2_reader, minimal_allowed_draft):
    """ Test create and submit review request by member of a community different from the record """

    h["Authorization"] = f"Bearer {token_com1_reader}"

    # File header Authorisation
    fh["Authorization"] = f"Bearer {token_com1_reader}"

    community1 = current_communities.service.search(system_identity, q="slug:com1")
    assert community1
    community1_id = list(community1.hits)[0]["id"]
    assert community1_id

    community2 = current_communities.service.search(system_identity, q="slug:com2")
    assert community2
    community2_id = list(community2.hits)[0]["id"]
    assert community2_id

    record = deepcopy(minimal_allowed_draft)

    record["metadata"]["title"] = f"Test draft: review {community2_id}"
    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)

    assert r.status_code == 201
    links = r.json()['links']
    id = r.json()['id']

    review = {
        "receiver": {
            "community": community1_id
        },
        "type": "community-submission"
    }

    # Add file
    add_file(h, fh, links, filepath)

    # Cannot publish because no community is selected
    r = requests.post(f"{api}/api/records/{id}/draft/actions/publish", headers=h, verify=False)
    assert r.status_code == 403

    h["Authorization"] = f"Bearer {token_com2_reader}"
    r = requests.post(f"{api}/api/records/{id}/draft/actions/publish", headers=h, verify=False)
    assert r.status_code == 403

    h["Authorization"] = ""
    r = requests.post(f"{api}/api/records/{id}/draft/actions/publish", headers=h, verify=False)
    assert r.status_code == 400

    # Create review request
    h["Authorization"] = f"Bearer {token_com1_reader}"
    r = requests.put(f"{api}/api/records/{id}/draft/review", data=json.dumps(review), headers=h, verify=False)
    assert r.status_code == 200
    assert r.json()["status"] == "created"
    assert r.json()["receiver"]["community"] == community1_id
    assert r.json()["topic"]["record"] == id

    # Cannot publish because review request has not been accepted
    r = requests.post(f"{api}/api/records/{id}/draft/actions/publish", headers=h, verify=False)
    assert r.status_code == 403

    h["Authorization"] = f"Bearer {token_com2_reader}"
    r = requests.post(f"{api}/api/records/{id}/draft/actions/publish", headers=h, verify=False)
    assert r.status_code == 403

    h["Authorization"] = ""
    r = requests.post(f"{api}/api/records/{id}/draft/actions/publish", headers=h, verify=False)
    assert r.status_code == 400
