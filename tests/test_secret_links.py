# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 BIG MAP Archive.
#
# BIG MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.


from io import BytesIO

import pytest
from flask import g
from flask_principal import AnonymousIdentity
from invenio_access.permissions import any_user, system_identity
from invenio_app.factory import create_app
from invenio_communities.generators import CommunityRoleNeed
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier
from invenio_rdm_records.records.api import RDMDraft, RDMRecord
from invenio_rdm_records.secret_links.permissions import LinkNeed
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_requests import current_requests_service

from .helpers import add_community_to_draft, get_community_id

app = create_app()
ctx = app.app_context()
ctx.push()


# @pytest.fixture()
# def service():
#     """RDM Record Service."""
#     return current_rdm_records.records_service


@pytest.fixture()
def restricted_draft(service, minimal_allowed_draft, identity_com1, com1_reader):
    """Restricted draft fixture."""
    data = minimal_allowed_draft.copy()
    data["metadata"]["title"] = "Test sharelinks draft"
    # data["files"]["enabled"] = True

    community1_id = get_community_id("com1")
    assert community1_id

    # Create
    draft = service.create(identity_com1, data)

    # Add a file
    service.draft_files.init_files(
        identity_com1, draft.id, data=[{"key": "test.pdf"}]
    )
    service.draft_files.set_file_content(
        identity_com1, draft.id, "test.pdf", BytesIO(b"test file")
    )
    service.draft_files.commit_file(identity_com1, draft.id, "test.pdf")

    # Add draft to community1: create community-submission request, ALLOW
    add_community_to_draft(com1_reader, community1_id, draft.id)

    # Get the draft
    pid = PersistentIdentifier.get(pid_type='recid', pid_value=draft.id)
    draft = RDMDraft.get_record(pid.object_uuid)

    return RDMDraft.get_record(draft.id)


@pytest.fixture()
def restricted_record(service, minimal_allowed_draft, identity_com1, identity2_com1, identity_com2, com1_reader):
    """Restricted record fixture."""
    data = minimal_allowed_draft.copy()
    data["metadata"]["title"] = "Test sharelinks"
    # data["files"]["enabled"] = True

    community1_id = get_community_id("com1")
    assert community1_id

    # Create
    draft = service.create(identity_com1, data)

    # Add a file
    service.draft_files.init_files(
        identity_com1, draft.id, data=[{"key": "test.pdf"}]
    )
    service.draft_files.set_file_content(
        identity_com1, draft.id, "test.pdf", BytesIO(b"test file")
    )
    service.draft_files.commit_file(identity_com1, draft.id, "test.pdf")

    # Add draft to community1: create community-submission request, ALLOW
    add_community_to_draft(com1_reader, community1_id, draft.id)

    # Submit community-submission review
    service.review.submit(identity_com1, draft.id)

    pid = PersistentIdentifier.get(pid_type='recid', pid_value=draft.id)
    draft = RDMDraft.get_record(pid.object_uuid)
    reqid = draft.parent.review.id

    # Accept the request and publish
    current_requests_service.execute_action(system_identity, reqid, "accept", {})

    # # Publish
    # record = service.publish(identity_com1, draft.id)

    # Get published record
    record = RDMRecord.get_record(draft.id)

    # Owner can read published record
    service.read(identity_com1, record.get("id"))

    # Member of community can read published record
    identity2_com1.provides.add(CommunityRoleNeed(community1_id, role="reader"))
    service.read(identity2_com1, record.get("id"))

    # Member of another community can not read published record
    community2_id = get_community_id("com2")
    assert community2_id
    identity_com2.provides.add(CommunityRoleNeed(community2_id, role="reader"))
    pytest.raises(PermissionDeniedError, service.read, identity_com2, record.get("id"))

    # Put published record in edit mode so that draft exists (this is for testing the preview secret link)
    draft = service.edit(identity_com1, record.get("id"))

    return RDMRecord.get_record(record.id)


# Record
def test_secret_links_anonymus(service, restricted_record, identity_com1):
    """Test permission level with and without secret link for anonymus users."""

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

    # ===
    # === ANONYMUS user ===
    # ===
    anon = AnonymousIdentity()
    anon.provides.add(any_user)
    setattr(g, "identity", anon)

    # Deny anonymous to read restricted record and draft
    pytest.raises(PermissionDeniedError, service.read, anon, id_)
    pytest.raises(PermissionDeniedError, service.files.list_files, anon, id_)
    pytest.raises(PermissionDeniedError, service.read_draft, anon, id_)
    with pytest.raises(PermissionDeniedError):
        service.draft_files.list_files(anon, id_)

    # Deny anonymous to update/delete/edit/publish draft
    pytest.raises(PermissionDeniedError, service.update_draft, anon, id_, {})
    pytest.raises(PermissionDeniedError, service.edit, anon, id_)
    pytest.raises(PermissionDeniedError, service.delete_draft, anon, id_)
    pytest.raises(PermissionDeniedError, service.new_version, anon, id_)
    pytest.raises(PermissionDeniedError, service.publish, anon, id_)
    with pytest.raises(PermissionDeniedError):
        service.draft_files.init_files(anon, id_, {})
    with pytest.raises(PermissionDeniedError):
        service.draft_files.update_file_metadata(anon, id_, "test.pdf", {})
    with pytest.raises(PermissionDeniedError):
        service.draft_files.commit_file(anon, id_, "test.pdf")
    with pytest.raises(PermissionDeniedError):
        service.draft_files.delete_file(anon, id_, "test.pdf")
    with pytest.raises(PermissionDeniedError):
        service.draft_files.delete_all_files(anon, id_)
    with pytest.raises(PermissionDeniedError):
        service.draft_files.set_file_content(anon, id_, "test.pdf", None)

    # ===
    # === ANONYMUS user with VIEW LINK ===
    # ===
    anon.provides.add(LinkNeed(view_link.id))

    # Allow anonymous with view link to read record
    service.read(anon, id_)
    service.files.list_files(anon, id_)
    service.files.get_file_content(anon, id_, "test.pdf")
    service.files.read_file_metadata(anon, id_, "test.pdf")

    # Deny anonymous with view link to read draft
    pytest.raises(PermissionDeniedError, service.read_draft, anon, id_)
    with pytest.raises(PermissionDeniedError):
        service.draft_files.list_files(anon, id_)
        service.draft_files.get_file_content(anon, id_, "test.pdf")
        service.draft_files.read_file_metadata(anon, id_, "test.pdf")

    # Deny anonymous with view link to update/delete/edit/publish draft
    pytest.raises(PermissionDeniedError, service.update_draft, anon, id_, {})
    pytest.raises(PermissionDeniedError, service.edit, anon, id_)
    pytest.raises(PermissionDeniedError, service.delete_draft, anon, id_)
    pytest.raises(PermissionDeniedError, service.new_version, anon, id_)
    pytest.raises(PermissionDeniedError, service.publish, anon, id_)
    with pytest.raises(PermissionDeniedError):
        service.draft_files.init_files(anon, id_, {})
    with pytest.raises(PermissionDeniedError):
        service.draft_files.update_file_metadata(anon, id_, "test.pdf", {})
    with pytest.raises(PermissionDeniedError):
        service.draft_files.commit_file(anon, id_, "test.pdf")
    with pytest.raises(PermissionDeniedError):
        service.draft_files.delete_file(anon, id_, "test.pdf")
    with pytest.raises(PermissionDeniedError):
        service.draft_files.delete_all_files(anon, id_)
    with pytest.raises(PermissionDeniedError):
        service.draft_files.set_file_content(anon, id_, "test.pdf", None)

    # ===
    # === ANONYMUS user with PREVIEW LINK ===
    # ===
    anon.provides.remove(LinkNeed(view_link.id))
    anon.provides.add(LinkNeed(preview_link.id))

    # Allow anonymous with preview link to read record and draft
    service.read(anon, id_)
    service.files.list_files(anon, id_)
    service.files.get_file_content(anon, id_, "test.pdf")
    service.files.read_file_metadata(anon, id_, "test.pdf")

    service.read_draft(anon, id_)
    service.draft_files.list_files(anon, id_)
    service.draft_files.get_file_content(anon, id_, "test.pdf")
    service.draft_files.read_file_metadata(anon, id_, "test.pdf")

    # Deny anonymous with preview link to update/delete/edit/publish draft
    pytest.raises(PermissionDeniedError, service.update_draft, anon, id_, {})
    pytest.raises(PermissionDeniedError, service.edit, anon, id_)
    pytest.raises(PermissionDeniedError, service.delete_draft, anon, id_)
    pytest.raises(PermissionDeniedError, service.new_version, anon, id_)
    pytest.raises(PermissionDeniedError, service.publish, anon, id_)
    with pytest.raises(PermissionDeniedError):
        service.draft_files.init_files(anon, id_, {})
    with pytest.raises(PermissionDeniedError):
        service.draft_files.update_file_metadata(anon, id_, "test.pdf", {})
    with pytest.raises(PermissionDeniedError):
        service.draft_files.commit_file(anon, id_, "test.pdf")
    with pytest.raises(PermissionDeniedError):
        service.draft_files.delete_file(anon, id_, "test.pdf")
    with pytest.raises(PermissionDeniedError):
        service.draft_files.delete_all_files(anon, id_)
    with pytest.raises(PermissionDeniedError):
        service.draft_files.set_file_content(anon, id_, "test.pdf", None)

    # ===
    # === ANONYMUS user with EDIT LINK ===
    # === can not read record, can not publish, can read and edit draft
    # ===
    anon.provides.remove(LinkNeed(preview_link.id))
    anon.provides.add(LinkNeed(edit_link.id))

    # Deny anonymous with edit link to read record
    with pytest.raises(PermissionDeniedError):
        service.read(anon, id_)
        service.files.list_files(anon, id_)
        service.files.get_file_content(anon, id_, "test.pdf")
        service.files.read_file_metadata(anon, id_, "test.pdf")
        service.new_version(anon, id_)

    # Deny anonymous with edit link to read draft
    with pytest.raises(PermissionDeniedError):
        service.read_draft(anon, id_)
        service.draft_files.list_files(anon, id_)
        service.draft_files.get_file_content(anon, id_, "test.pdf")
        service.draft_files.read_file_metadata(anon, id_, "test.pdf")

    # Deny anonymous with edit link to update/delete/edit draft
    with pytest.raises(PermissionDeniedError):
        service.update_draft(anon, id_, {})
        service.delete_draft(anon, id_)
        service.edit(anon, id_)
        service.draft_files.init_files(anon, id_, data=[{"key": "test2.pdf"}])
        service.draft_files.update_file_metadata(anon, id_, "test.pdf", {})
        service.draft_files.commit_file(anon, id_, "test.pdf")
        service.draft_files.set_file_content(anon, id_, "test.pdf", None)
        service.draft_files.delete_file(anon, id_, "test.pdf")
        service.draft_files.delete_all_files(anon, id_)

    # Deny publish
    with pytest.raises(PermissionDeniedError):
        service.publish(anon, id_)


def test_owner(service, restricted_record, identity_com1):
    """Test permission level without secret link for record owner."""
    id_ = restricted_record.get("id")

    # Not needed to create links
    # Move this tests in another file

    # view_link = service.access.create_secret_link(
    #     identity_com1, id_, {"permission": "view"}
    # )
    # preview_link = service.access.create_secret_link(
    #     identity_com1, id_, {"permission": "preview"}
    # )
    # edit_link = service.access.create_secret_link(
    #     identity_com1, id_, {"permission": "edit"}
    # )

    # ===
    # === 1. AUTHENTICATED user, owner of record ===
    # ===
    i = identity_com1
    setattr(g, "identity", i)

    # Allow owner to read and edit record and draft
    # published record
    service.read(i, id_)
    service.files.list_files(i, id_)
    service.files.get_file_content(i, id_, "test.pdf")
    service.files.read_file_metadata(i, id_, "test.pdf")

    # draft
    service.read_draft(i, id_)
    service.draft_files.list_files(i, id_)
    service.draft_files.get_file_content(i, id_, "test.pdf")
    service.draft_files.read_file_metadata(i, id_, "test.pdf")

    # edit draft of published record
    draft = service.read_draft(i, id_)
    data = draft.data
    data["metadata"]["title"] = "allow it"
    service.update_draft(i, id_, data)

    # update publish record
    service.publish(i, id_)

    # create new version of record
    new_draft = service.new_version(i, id_)
    new_id = new_draft.id
    service.import_files(i, new_id)

    # publish new version
    service.publish(i, new_id)

    # create new version of record to test delete of files and draft
    new_draft = service.new_version(i, new_id)
    new_id = new_draft.id
    service.import_files(i, new_id)
    service.draft_files.delete_file(i, new_id, "test.pdf")
    service.delete_draft(i, new_id)
    pytest.raises(PIDDoesNotExistError, service.edit, i, new_id)


def test_secret_links_communitymember(service, restricted_record, identity_com1, identity2_com1):
    """Test permission level with and without secret link for member of the same record's community."""

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

    community1_id = get_community_id("com1")
    assert community1_id

    # ===
    # === AUTHENTICATED user, member of the same community of record ===
    # ===
    i = identity2_com1
    i.provides.add(CommunityRoleNeed(community1_id, role="reader"))
    setattr(g, "identity", i)

    # Allow to read record without secret link
    service.read(i, id_)
    service.files.list_files(i, id_)
    service.files.get_file_content(i, id_, "test.pdf")
    service.files.read_file_metadata(i, id_, "test.pdf")

    # Deny to read draft
    with pytest.raises(PermissionDeniedError):
        service.read_draft(i, id_)
        service.draft_files.list_files(i, id_)
        service.draft_files.get_file_content(i, id_, "test.pdf")
        service.draft_files.read_file_metadata(i, id_, "test.pdf")

    # Deny to update/delete/edit/publish record and draft
    with pytest.raises(PermissionDeniedError):
        service.update_draft(i, id_, {})
        service.edit(i, id_)
        service.delete_draft(i, id_)
        service.new_version(i, id_)
        service.publish(i, id_)

    with pytest.raises(PermissionDeniedError):
        service.draft_files.init_files(i, id_, {})
        service.draft_files.update_file_metadata(i, id_, "test.pdf", {})
        service.draft_files.commit_file(i, id_, "test.pdf")
        service.draft_files.delete_file(i, id_, "test.pdf")
        service.draft_files.delete_all_files(i, id_)
        service.draft_files.set_file_content(i, id_, "test.pdf", None)

    # ===
    # === AUTHENTICATED user with VIEW LINK ===
    # ===
    i.provides.add(LinkNeed(view_link.id))

    # Allow authenticated with view link to read record
    service.read(i, id_)
    service.files.list_files(i, id_)
    service.files.get_file_content(i, id_, "test.pdf")
    service.files.read_file_metadata(i, id_, "test.pdf")

    # Deny authenticated with view link to read draft
    with pytest.raises(PermissionDeniedError):
        service.read_draft(i, id_)
        service.draft_files.list_files(i, id_)
        service.draft_files.get_file_content(i, id_, "test.pdf")
        service.draft_files.read_file_metadata(i, id_, "test.pdf")

    # Deny authenticated with view link to update/delete/edit/publish draft
    with pytest.raises(PermissionDeniedError):
        service.update_draft(i, id_, {})
        service.edit(i, id_)
        service.delete_draft(i, id_)
        service.new_version(i, id_)
        service.publish(i, id_)

    with pytest.raises(PermissionDeniedError):
        service.draft_files.init_files(i, id_, {})
        service.draft_files.update_file_metadata(i, id_, "test.pdf", {})
        service.draft_files.commit_file(i, id_, "test.pdf")
        service.draft_files.delete_file(i, id_, "test.pdf")
        service.draft_files.delete_all_files(i, id_)
        service.draft_files.set_file_content(i, id_, "test.pdf", None)

    # ===
    # === AUTHENTICATED user with PREVIEW LINK ===
    # ===
    i.provides.remove(LinkNeed(view_link.id))
    i.provides.add(LinkNeed(preview_link.id))

    # Allow authenticated with preview link to read record and draft
    service.read(i, id_)
    service.files.list_files(i, id_)
    service.files.get_file_content(i, id_, "test.pdf")
    service.files.read_file_metadata(i, id_, "test.pdf")

    service.read_draft(i, id_)
    service.draft_files.list_files(i, id_)
    service.draft_files.get_file_content(i, id_, "test.pdf")
    service.draft_files.read_file_metadata(i, id_, "test.pdf")

    # Deny authenticated with preview link to update/delete/edit/publish draft
    with pytest.raises(PermissionDeniedError):
        service.update_draft(i, id_, {})
        service.edit(i, id_)
        service.delete_draft(i, id_)
        service.new_version(i, id_)
        service.publish(i, id_)

    with pytest.raises(PermissionDeniedError):
        service.draft_files.init_files(i, id_, {})
        service.draft_files.update_file_metadata(i, id_, "test.pdf", {})
        service.draft_files.commit_file(i, id_, "test.pdf")
        service.draft_files.delete_file(i, id_, "test.pdf")
        service.draft_files.delete_all_files(i, id_)
        service.draft_files.set_file_content(i, id_, "test.pdf", None)

    # ===
    # === AUTHENTICATED user with EDIT LINK ===
    # ===
    i.provides.remove(LinkNeed(preview_link.id))
    i.provides.add(LinkNeed(edit_link.id))

    # Allow authenticated with edit link to read record and draft
    service.read(i, id_)
    service.files.list_files(i, id_)
    service.files.get_file_content(i, id_, "test.pdf")
    service.files.read_file_metadata(i, id_, "test.pdf")
    service.read_draft(i, id_)
    service.draft_files.list_files(i, id_)
    service.draft_files.get_file_content(i, id_, "test.pdf")
    service.draft_files.read_file_metadata(i, id_, "test.pdf")

    # Allow authenticated with edit link to update/delete/edit/publish draft
    # draft
    service.read_draft(i, id_)
    service.draft_files.list_files(i, id_)
    service.draft_files.get_file_content(i, id_, "test.pdf")
    service.draft_files.read_file_metadata(i, id_, "test.pdf")
    service.draft_files.update_file_metadata(i, id_, "test.pdf", {})
    service.draft_files.commit_file(i, id_, "test.pdf")
    # service.draft_files.set_file_content(i, id_, "test.pdf", None)

    # edit draft of published record
    service.edit(i, id_)
    draft = service.read_draft(i, id_)
    data = draft.data
    data["metadata"]["title"] = "allow it"
    service.update_draft(i, id_, data)

    # add new file to draft
    # service.draft_files.init_files(i, draft.id, data=[{"key": "test2.pdf"}])

    # deny publish record
    pytest.raises(PermissionDeniedError, service.publish, i, id_)

    # create new version of record
    new_draft = service.new_version(i, id_)
    new_id = new_draft.id
    service.read_draft(i, new_id)
    service.import_files(i, new_id)

    # deny publish new version
    pytest.raises(PermissionDeniedError, service.publish, i, new_id)

    # delete files of new version
    service.draft_files.delete_file(i, new_id, "test.pdf")
    service.draft_files.delete_all_files(i, new_id)
    service.delete_draft(i, new_id)


def test_secret_links_not_communitymember(service, restricted_record, identity_com1, identity_com2):
    """Test permission level with and without secret link for member of not the same record's community."""

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

    community2_id = get_community_id("com2")
    assert community2_id

    # ===
    # === 2. AUTHENTICATED user, member of the different community of record ===
    # ===
    i = identity_com2
    i.provides.add(CommunityRoleNeed(community2_id, role="reader"))
    setattr(g, "identity", i)

    # Deny to read record without secret link
    with pytest.raises(PermissionDeniedError):
        service.read(i, id_)
        service.files.list_files(i, id_)
        service.files.get_file_content(i, id_, "test.pdf")
        service.files.read_file_metadata(i, id_, "test.pdf")

    # Deny to read draft
    with pytest.raises(PermissionDeniedError):
        service.read_draft(i, id_)
        service.draft_files.list_files(i, id_)
        service.draft_files.get_file_content(i, id_, "test.pdf")
        service.draft_files.read_file_metadata(i, id_, "test.pdf")

    # Deny to update/delete/edit/publish record and draft
    with pytest.raises(PermissionDeniedError):
        service.update_draft(i, id_, {})
        service.edit(i, id_)
        service.delete_draft(i, id_)
        service.new_version(i, id_)
        service.publish(i, id_)

    with pytest.raises(PermissionDeniedError):
        service.draft_files.init_files(i, id_, {})
        service.draft_files.update_file_metadata(i, id_, "test.pdf", {})
        service.draft_files.commit_file(i, id_, "test.pdf")
        service.draft_files.delete_file(i, id_, "test.pdf")
        service.draft_files.delete_all_files(i, id_)
        service.draft_files.set_file_content(i, id_, "test.pdf", None)

    # ===
    # === AUTHENTICATED user with VIEW LINK ===
    # ===
    i.provides.add(LinkNeed(view_link.id))

    # Allow authenticated with view link to read record
    service.read(i, id_)
    service.files.list_files(i, id_)
    service.files.get_file_content(i, id_, "test.pdf")
    service.files.read_file_metadata(i, id_, "test.pdf")

    # Deny authenticated with view link to read draft
    with pytest.raises(PermissionDeniedError):
        service.read_draft(i, id_)
        service.draft_files.list_files(i, id_)
        service.draft_files.get_file_content(i, id_, "test.pdf")
        service.draft_files.read_file_metadata(i, id_, "test.pdf")

    # Deny to update/delete/edit/publish record and draft
    with pytest.raises(PermissionDeniedError):
        service.update_draft(i, id_, {})
        service.edit(i, id_)
        service.delete_draft(i, id_)
        service.new_version(i, id_)
        service.publish(i, id_)

    with pytest.raises(PermissionDeniedError):
        service.draft_files.init_files(i, id_, {})
        service.draft_files.update_file_metadata(i, id_, "test.pdf", {})
        service.draft_files.commit_file(i, id_, "test.pdf")
        service.draft_files.delete_file(i, id_, "test.pdf")
        service.draft_files.delete_all_files(i, id_)
        service.draft_files.set_file_content(i, id_, "test.pdf", None)

    # ===
    # === AUTHENTICATED user with PREVIEW LINK ===
    # ===
    i.provides.remove(LinkNeed(view_link.id))
    i.provides.add(LinkNeed(preview_link.id))

    # Allow authenticated with preview link to read record and draft
    service.read(i, id_)
    service.files.list_files(i, id_)
    service.files.get_file_content(i, id_, "test.pdf")
    service.files.read_file_metadata(i, id_, "test.pdf")

    service.read_draft(i, id_)
    service.draft_files.list_files(i, id_)
    service.draft_files.get_file_content(i, id_, "test.pdf")
    service.draft_files.read_file_metadata(i, id_, "test.pdf")

    # Deny authenticated with preview link to update/delete/edit/publish draft
    with pytest.raises(PermissionDeniedError):
        service.update_draft(i, id_, {})
        service.edit(i, id_)
        service.delete_draft(i, id_)
        service.new_version(i, id_)
        service.publish(i, id_)

    with pytest.raises(PermissionDeniedError):
        service.draft_files.init_files(i, id_, {})
        service.draft_files.update_file_metadata(i, id_, "test.pdf", {})
        service.draft_files.commit_file(i, id_, "test.pdf")
        service.draft_files.delete_file(i, id_, "test.pdf")
        service.draft_files.delete_all_files(i, id_)
        service.draft_files.set_file_content(i, id_, "test.pdf", None)

    # ===
    # === AUTHENTICATED user with EDIT LINK ===
    # ===
    i.provides.remove(LinkNeed(preview_link.id))
    i.provides.add(LinkNeed(edit_link.id))

    # Deny authenticated with edit link to read record and draft
    with pytest.raises(PermissionDeniedError):
        service.read(i, id_)
        service.files.list_files(i, id_)
        service.files.get_file_content(i, id_, "test.pdf")
        service.files.read_file_metadata(i, id_, "test.pdf")

        service.read_draft(i, id_)
        service.draft_files.list_files(i, id_)
        service.draft_files.get_file_content(i, id_, "test.pdf")
        service.draft_files.read_file_metadata(i, id_, "test.pdf")

    # Deny authenticated with edit link to update/delete/edit/publish draft
    with pytest.raises(PermissionDeniedError):
        service.update_draft(i, id_, {})
        service.edit(i, id_)
        service.delete_draft(i, id_)
        service.new_version(i, id_)
        service.publish(i, id_)

    with pytest.raises(PermissionDeniedError):
        service.draft_files.init_files(i, id_, {})
        service.draft_files.update_file_metadata(i, id_, "test.pdf", {})
        service.draft_files.commit_file(i, id_, "test.pdf")
        service.draft_files.delete_file(i, id_, "test.pdf")
        service.draft_files.delete_all_files(i, id_)
        service.draft_files.set_file_content(i, id_, "test.pdf", None)


# Draft
def draft_deny_read_write(service, i, id_):
    """ Deny read and write access to draft and files """
    # Deny to read restricted draft
    with pytest.raises(PermissionDeniedError):
        service.read_draft(i, id_)
        service.draft_files.list_files(i, id_)
        service.draft_files.get_file_content(i, id_, "test.pdf")
        service.draft_files.read_file_metadata(i, id_, "test.pdf")

    # Deny to update/delete/edit/publish draft
    with pytest.raises(PermissionDeniedError):
        service.update_draft(i, id_, {})
        service.edit(i, id_)
        service.delete_draft(i, id_)
        service.new_version(i, id_)
        service.publish(i, id_)

    with pytest.raises(PermissionDeniedError):
        service.draft_files.init_files(i, id_, {})
        service.draft_files.update_file_metadata(i, id_, "test.pdf", {})
        service.draft_files.commit_file(i, id_, "test.pdf")
        service.draft_files.delete_file(i, id_, "test.pdf")
        service.draft_files.delete_all_files(i, id_)
        service.draft_files.set_file_content(i, id_, "test.pdf", None)


def draft_deny_write(service, i, id_):
    """ Allow read access to draft and files, deny write access """
    # Allow to read restricted draft
    service.read_draft(i, id_)
    service.draft_files.list_files(i, id_)
    service.draft_files.get_file_content(i, id_, "test.pdf")
    service.draft_files.read_file_metadata(i, id_, "test.pdf")

    # Deny to update/delete/edit/publish draft
    with pytest.raises(PermissionDeniedError):
        service.update_draft(i, id_, {})
        # service.edit(i, id_)
        service.delete_draft(i, id_)
        service.new_version(i, id_)
        service.publish(i, id_)

    with pytest.raises(PermissionDeniedError):
        service.draft_files.init_files(i, id_, {})
        service.draft_files.update_file_metadata(i, id_, "test.pdf", {})
        service.draft_files.commit_file(i, id_, "test.pdf")
        service.draft_files.delete_file(i, id_, "test.pdf")
        service.draft_files.delete_all_files(i, id_)
        service.draft_files.set_file_content(i, id_, "test.pdf", None)


def test_draft_secret_links_anonymus(service, restricted_draft, identity_com1):
    """Test permission level with and without secret link for anonymus users."""
    id_ = restricted_draft.get("id")

    view_link = service.access.create_secret_link(
        identity_com1, id_, {"permission": "view"}
    )
    preview_link = service.access.create_secret_link(
        identity_com1, id_, {"permission": "preview"}
    )
    edit_link = service.access.create_secret_link(
        identity_com1, id_, {"permission": "edit"}
    )

    # ===
    # === ANONYMUS user ===
    # ===
    anon = AnonymousIdentity()
    anon.provides.add(any_user)
    setattr(g, "identity", anon)
    draft_deny_read_write(service, anon, id_)

    # ===
    # === ANONYMUS user with VIEW LINK ===
    # ===
    anon.provides.add(LinkNeed(view_link.id))
    draft_deny_read_write(service, anon, id_)

    # ===
    # === ANONYMUS user with PREVIEW LINK ===
    # ===
    anon.provides.remove(LinkNeed(view_link.id))
    anon.provides.add(LinkNeed(preview_link.id))
    draft_deny_write(service, anon, id_)

    # ===
    # === ANONYMUS user with EDIT LINK ===
    # ===
    anon.provides.remove(LinkNeed(preview_link.id))
    anon.provides.add(LinkNeed(edit_link.id))
    service.edit(anon, id_)
    draft_deny_read_write(service, anon, id_)


def test_draft_secret_links_communitymember(service, restricted_draft, identity_com1, identity2_com1):
    """Test permission level with and without secret link for member of the same draft's community."""
    id_ = restricted_draft.get("id")

    view_link = service.access.create_secret_link(
        identity_com1, id_, {"permission": "view"}
    )
    preview_link = service.access.create_secret_link(
        identity_com1, id_, {"permission": "preview"}
    )
    edit_link = service.access.create_secret_link(
        identity_com1, id_, {"permission": "edit"}
    )

    community1_id = get_community_id("com1")
    assert community1_id

    # ===
    # === AUTHENTICATED user, member of the same community of record ===
    # ===
    i = identity2_com1
    i.provides.add(CommunityRoleNeed(community1_id, role="reader"))
    setattr(g, "identity", i)
    draft_deny_read_write(service, i, id_)

    # ===
    # === AUTHENTICATED user with VIEW LINK ===
    # ===
    i.provides.add(LinkNeed(view_link.id))
    draft_deny_read_write(service, i, id_)

    # ===
    # === AUTHENTICATED user with PREVIEW LINK ===
    # ===
    i.provides.remove(LinkNeed(view_link.id))
    i.provides.add(LinkNeed(preview_link.id))
    draft_deny_write(service, i, id_)

    # ===
    # === AUTHENTICATED user with EDIT LINK ===
    # ===
    i.provides.remove(LinkNeed(preview_link.id))
    i.provides.add(LinkNeed(edit_link.id))

    # Allow to read restricted draft
    service.read_draft(i, id_)

    # Allow to read restricted draft files
    service.draft_files.list_files(i, id_)
    service.draft_files.get_file_content(i, id_, "test.pdf")
    service.draft_files.read_file_metadata(i, id_, "test.pdf")

    # Allow to update/edit draft
    service.update_draft(i, id_, {})
    service.edit(i, id_)

    # Deny to delete/publish draft
    with pytest.raises(PermissionDeniedError):
        service.delete_draft(i, id_)
    with pytest.raises(PermissionDeniedError):
        service.publish(i, id_)

    # Allow to edit files
    service.draft_files.delete_file(i, id_, "test.pdf")
    service.draft_files.delete_all_files(i, id_)
    service.draft_files.init_files(i, id_, data=[{"key": "test2.pdf"}])
    service.draft_files.update_file_metadata(i, id_, "test2.pdf", {})
    service.draft_files.set_file_content(i, id_, "test2.pdf", None)
    # service.draft_files.commit_file(i, id_, "test2.pdf")


def test_draft_secret_links_not_communitymember(service, restricted_draft, identity_com1, identity_com2):
    """Test permission level with and without secret link for member of the same draft's community."""
    id_ = restricted_draft.get("id")

    view_link = service.access.create_secret_link(
        identity_com1, id_, {"permission": "view"}
    )
    preview_link = service.access.create_secret_link(
        identity_com1, id_, {"permission": "preview"}
    )
    edit_link = service.access.create_secret_link(
        identity_com1, id_, {"permission": "edit"}
    )

    community2_id = get_community_id("com2")
    assert community2_id

    # ===
    # === AUTHENTICATED user, not member of the same community of record ===
    # ===
    i = identity_com2
    i.provides.add(CommunityRoleNeed(community2_id, role="reader"))
    setattr(g, "identity", i)
    draft_deny_read_write(service, i, id_)

    # ===
    # === AUTHENTICATED user with VIEW LINK ===
    # ===
    i.provides.add(LinkNeed(view_link.id))
    draft_deny_read_write(service, i, id_)

    # ===
    # === AUTHENTICATED user with PREVIEW LINK ===
    # ===
    i.provides.remove(LinkNeed(view_link.id))
    i.provides.add(LinkNeed(preview_link.id))
    draft_deny_write(service, i, id_)

    # ===
    # === AUTHENTICATED user with EDIT LINK ===
    # ===
    i.provides.remove(LinkNeed(preview_link.id))
    i.provides.add(LinkNeed(edit_link.id))
    draft_deny_read_write(service, i, id_)
