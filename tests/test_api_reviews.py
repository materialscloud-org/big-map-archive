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


def test_add_review(token_com1_reader, minimal_allowed_draft):
    """
    Test:
        - create minimal draft
        - add review
        - add a file to draft
        - publish draft
    """
    h["Authorization"] = f"Bearer {token_com1_reader}"

    # file header Authorisation
    fh["Authorization"] = f"Bearer {token_com1_reader}"

    record = deepcopy(minimal_allowed_draft)

    record["metadata"]["title"] = "Test draft: review"
    r = requests.post(f"{api}/api/records", data=json.dumps(record), headers=h, verify=False)

    assert r.status_code == 201
    links = r.json()['links']
    id = r.json()['id']

    # add review for community com1
    community1 = current_communities.service.search(system_identity, q="slug:com1")
    assert community1
    community1_id = list(community1.hits)[0]["id"]
    assert community1_id

    review = {
        "receiver": {
            "community": community1_id
        },
        "type": "community-submission"
    }

    r = requests.put(f"{api}/api/records/{id}/draft/review", data=json.dumps(review), headers=h, verify=False)
    assert r.status_code == 200
    assert r.json()["status"] == "created"
    assert r.json()["receiver"]["community"] == community1_id
    assert r.json()["topic"]["record"] == id

    # Add file
    add_file(h, fh, links, filepath)

    # Submit draft for review, accept review and publish the draft because the community has review_policy open
    links["submit-review"] = f"{links['publish'].rstrip('publish')}submit-review"
    r = requests.post(links["submit-review"], headers=h, verify=False)
    assert r.status_code == 202
