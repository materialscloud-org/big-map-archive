# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 BIG MAP Archive.
#
# BIG MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration."""

from datetime import datetime
from pathlib import Path

import pytest
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_accounts.proxies import current_datastore
from invenio_communities import current_communities
from invenio_communities.fixtures.tasks import create_demo_community
from invenio_communities.members.errors import AlreadyMemberError
from invenio_db import db
from invenio_oauth2server.models import Client, Token
from invenio_rdm_records.fixtures.communities import CommunitiesFixture
from invenio_rdm_records.fixtures.users import UsersFixture
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import NoResultFound

from .helpers import generate_pat_token


@pytest.fixture
def users():
    """Create users fixture"""
    dir_ = Path(__file__).parent
    users = UsersFixture(
        [dir_ / "fixtures"],
        "users.yaml",
    )
    users.load()
    return users


@pytest.fixture
def communities():
    """Create communities fixture"""
    dir_ = Path(__file__).parent

    try:
        communities = CommunitiesFixture(
            [dir_ / "fixtures"],
            "communities.yaml",
            create_demo_community,
            delay=False,
        )
        communities.load()
    except ValidationError:
        pass

    # Refresh to make changes live
    # service.record_cls.index.refresh()

    return communities


@pytest.fixture
def com3():
    return {
        "access": {
            "visibility": "restricted",
            "member_policy": "closed",
            "record_policy": "open",
            "review_policy": "open"
        },
        "slug": "com3",
        "metadata": {
            "title": "Community3",
            "description": "This is an example Community.",
            "type": {
                "id": "event"
            },
            "curation_policy": "This is the kind of records we accept.",
            "page": "Information for my community.",
            "website": "https://mysite.com",
            "organizations": [{
                    "name": "My Org"
            }]
        }
    }

@pytest.fixture
def com_public_open():
    return {
        "access": {
            "visibility": "public",
            "member_policy": "open",
            "record_policy": "open",
            "review_policy": "open"
        },
        "slug": "com_public_open",
        "metadata": {
            "title": "Public, open community",
            "description": "This is an example Community.",
            "type": {
                "id": "event"
            },
            "curation_policy": "This is the kind of records we accept.",
            "page": "Information for my community.",
            "website": "https://mysite.com",
            "organizations": [{
                    "name": "My Org"
            }]
        }
    }


@pytest.fixture()
def com1_reader(users, communities):
    """Create user fixture

    community: com1
    role: reader
    """
    assert communities
    community1 = current_communities.service.search(system_identity, q="slug:com1")
    assert community1.total == 1
    community1_id = list(community1.hits)[0]["id"]

    # reader, community1
    com1_reader = current_datastore.find_user(email="com1_reader@materialscloud.com")
    assert com1_reader

    data = {
        "members": [{"type": "user", "id": str(com1_reader.id)}],
        "role": "reader",
    }
    try:
        current_communities.service.members.add(system_identity, community1_id, data)
    except AlreadyMemberError:
        pass
    return com1_reader


@pytest.fixture()
def com1_reader2(users, communities):
    """Create user fixture

    community: com1
    role: reader
    """
    assert communities
    community1 = current_communities.service.search(system_identity, q="slug:com1")
    assert community1.total == 1
    community1_id = list(community1.hits)[0]["id"]

    # reader, community1
    com1_reader2 = current_datastore.find_user(email="com1_reader2@materialscloud.com")
    assert com1_reader2

    data = {
        "members": [{"type": "user", "id": str(com1_reader2.id)}],
        "role": "reader",
    }
    try:
        current_communities.service.members.add(system_identity, community1_id, data)
    except AlreadyMemberError:
        pass
    return com1_reader2


@pytest.fixture()
def com1_curator(users, communities):
    """Create user fixture

    community: com1
    role: curator
    """
    assert communities
    community1 = current_communities.service.search(system_identity, q="slug:com1")
    assert community1.total == 1
    community1_id = list(community1.hits)[0]["id"]

    # curator, community1
    com1_curator = current_datastore.find_user(email="com1_curator@materialscloud.com")
    assert com1_curator

    data = {
        "members": [{"type": "user", "id": str(com1_curator.id)}],
        "role": "curator",
    }
    try:
        current_communities.service.members.add(system_identity, community1_id, data)
    except AlreadyMemberError:
        pass
    return com1_curator


@pytest.fixture()
def com1_manager(users, communities):
    """Create user fixture

    community: com1
    role: manager
    """
    assert communities
    community1 = current_communities.service.search(system_identity, q="slug:com1")
    assert community1.total == 1
    community1_id = list(community1.hits)[0]["id"]

    # manager, community1
    com1_manager = current_datastore.find_user(email="com1_manager@materialscloud.com")
    assert com1_manager

    data = {
        "members": [{"type": "user", "id": str(com1_manager.id)}],
        "role": "manager",
    }
    try:
        current_communities.service.members.add(system_identity, community1_id, data)
    except AlreadyMemberError:
        pass
    return com1_manager


@pytest.fixture()
def com2_reader(users, communities):
    """Create user fixture

    community: com2
    role: reader
    """
    community2 = current_communities.service.search(system_identity, q="slug:com2")
    assert community2.total == 1
    community2_id = list(community2.hits)[0]["id"]

    # reader, community1
    com2_reader = current_datastore.find_user(email="com2_reader@materialscloud.com")
    assert com2_reader

    data = {
        "members": [{"type": "user", "id": str(com2_reader.id)}],
        "role": "reader",
    }
    try:
        current_communities.service.members.add(system_identity, community2_id, data)
    except AlreadyMemberError:
        pass
    return com2_reader


@pytest.fixture()
def com2_curator(users, communities):
    """Create user fixture

    community: com2
    role: curator
    """
    community2 = current_communities.service.search(system_identity, q="slug:com2")
    assert community2.total == 1
    community2_id = list(community2.hits)[0]["id"]

    # curator, community2
    com2_curator = current_datastore.find_user(email="com2_curator@materialscloud.com")
    assert com2_curator

    data = {
        "members": [{"type": "user", "id": str(com2_curator.id)}],
        "role": "curator",
    }
    try:
        current_communities.service.members.add(system_identity, community2_id, data)
    except AlreadyMemberError:
        pass
    return com2_curator


@pytest.fixture()
def com2_manager(users, communities):
    """Create user fixture

    community: com2
    role: manager
    """
    assert communities
    community2 = current_communities.service.search(system_identity, q="slug:com2")
    assert community2.total == 1
    community2_id = list(community2.hits)[0]["id"]

    # manager, community2
    com2_manager = current_datastore.find_user(email="com2_manager@materialscloud.com")
    assert com2_manager

    data = {
        "members": [{"type": "user", "id": str(com2_manager.id)}],
        "role": "manager",
    }
    try:
        current_communities.service.members.add(system_identity, community2_id, data)
    except AlreadyMemberError:
        pass
    return com2_manager


@pytest.fixture()
def client():
    return current_app.test_client()


@pytest.fixture()
def oauth2_client_com1_reader(com1_reader):
    try:
        client = Client.query.filter(Client.client_id == "client_test_com1_reader").one()
    except NoResultFound:
        with db.session.begin_nested():
            client = Client(
                client_id="client_test_com1_reader",
                client_secret="client_test_com1_reader",
                name="client_test_com1_reader",
                description="",
                is_confidential=False,
                user_id=com1_reader.id,
                _redirect_uris="",
                _default_scopes="",
            )
            db.session.add(client)
        db.session.commit()
    return client.client_id


@pytest.fixture()
def oauth2_client_com1_curator(com1_curator):
    try:
        client = Client.query.filter(Client.client_id == "client_test_com1_curator").one()
    except NoResultFound:
        with db.session.begin_nested():
            client = Client(
                client_id="client_test_com1_curator",
                client_secret="client_test_com1_curator",
                name="client_test_com1_curator",
                description="",
                is_confidential=False,
                user_id=com1_curator.id,
                _redirect_uris="",
                _default_scopes="",
            )
            db.session.add(client)
        db.session.commit()
    return client.client_id



@pytest.fixture()
def oauth2_client_com2_reader(com2_reader):
    try:
        client = Client.query.filter(Client.client_id == "client_test_com2_reader").one()
    except NoResultFound:
        with db.session.begin_nested():
            client = Client(
                client_id="client_test_com2_reader",
                client_secret="client_test_com2_reader",
                name="client_test_com2_reader",
                description="",
                is_confidential=False,
                user_id=com2_reader.id,
                _redirect_uris="",
                _default_scopes="",
            )
            db.session.add(client)
        db.session.commit()
    return client.client_id


@pytest.fixture()
def token_com1_reader(com1_reader, oauth2_client_com1_reader):
    try:
        token = Token.query.filter(Token.client_id == "client_test_com1_reader").one()
    except NoResultFound:
        token = generate_pat_token(db, com1_reader, oauth2_client_com1_reader, "rat_token_com1_reader", scope="user:email")["token"]
    assert token
    return token.access_token



@pytest.fixture()
def token_com1_curator(com1_curator, oauth2_client_com1_curator):
    try:
        token = Token.query.filter(Token.client_id == "client_test_com1_curator").one()
    except NoResultFound:
        token = generate_pat_token(db, com1_curator, oauth2_client_com1_curator, "rat_token_com1_curator", scope="user:email")["token"]
    assert token
    return token.access_token


@pytest.fixture()
def token_com2_reader(com2_reader, oauth2_client_com2_reader):
    try:
        token = Token.query.filter(Token.client_id == "client_test_com2_reader").one()
    except NoResultFound:
        token = generate_pat_token(db, com2_reader, oauth2_client_com2_reader, "rat_token_com2_reader", scope="user:email")["token"]
        assert token
    return token.access_token


@pytest.fixture()
def minimal_record():
    """Minimal record."""
    return {
        "metadata": {
            "title": "Test record",
        },
    }


@pytest.fixture()
def minimal_allowed_draft():
    """Minimal draft with no files, with publication date, access restricted and embargo not active."""
    return {
        "metadata": {
            "title": "Test record",
            "publication_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "resource_type": {"id": "dataset"},
            "creators": [
                {
                    "person_or_org": {
                        "family_name": "Granata",
                        "given_name": "Valeria",
                        "type": "personal"
                    }
                }
            ],
            "description": "This is a test record.",
        },
        "access": {
            "files": "restricted",
            "record": "restricted",
            "embargo": {
                "until": None,
                "active": False,
                "reason": None
            }
        },
        "pids": {}
    }
