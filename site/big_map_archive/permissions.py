# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 BIG MAP Archive.
#
# BIG MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Permissions for BIG-MAP Archive Records."""
from invenio_rdm_records.services.generators import (
    CommunityInclusionReviewers, IfFileIsLocal, IfRestricted,
    RecordCommunitiesAction, RecordOwners, ResourceAccessToken, SecretLinks,
    SubmissionReviewer)
from invenio_rdm_records.services.permissions import RDMRecordPermissionPolicy
from invenio_records_permissions.generators import (AuthenticatedUser,
                                                    IfConfig, SystemProcess)
from invenio_users_resources.services.permissions import UserManager

from big_map_archive.generators import BMASecretLinks_excludes


class BMARecordPermissionPolicy(RDMRecordPermissionPolicy):
    can_search = [AuthenticatedUser(), SystemProcess()]

    can_manage = [
        RecordOwners(),
        RecordCommunitiesAction("curate"),
        SystemProcess(),
    ]

    # view record
    can_view = can_manage + [
        # AccessGrant("view"),
        SecretLinks("view"),
        # SubmissionReviewer(),
        UserManager,
        CommunityInclusionReviewers(),
        RecordCommunitiesAction("view"),
    ]

    # view draft
    can_preview = can_manage + [
        # AccessGrant("preview"),
        SecretLinks("preview"),
        # SubmissionReviewer(),
        UserManager,
    ]

    # edit record/draft
    can_curate = can_manage + [
        SecretLinks("edit"),
        BMASecretLinks_excludes(),
    ]

    # can_review = can_curate + [SubmissionReviewer()]
    can_review = can_curate
    can_view_preview = can_view + can_preview

    # Record
    # Deny access to records and files if not restricted (it should actually never be the case as all records are restricted)
    can_read = [
        IfRestricted("record", then_=can_view_preview, else_=[SystemProcess()]),
    ]
    can_read_files = [
        IfRestricted("files", then_=can_view_preview, else_=[SystemProcess()]),
        ResourceAccessToken("read"),
    ]
    can_media_read_files = [
        IfRestricted("record", then_=can_view_preview, else_=[SystemProcess()]),
        ResourceAccessToken("read"),
    ]

    # Manage of ShareLinks can only be done by owners of the record
    can_manage_record_access = [
        IfConfig(
            "RDM_ALLOW_RESTRICTED_RECORDS",
            then_=[RecordOwners(), SystemProcess()],
            else_=[],
        )
    ]

    # Draft
    can_read_draft = can_preview + can_curate
    can_draft_read_files = can_read_draft + [ResourceAccessToken("read")]
    can_update_draft = can_review
    can_draft_create_files = can_review
    can_draft_set_content_files = [
        # review is the same as create_files
        IfFileIsLocal(then_=can_review, else_=[SystemProcess()])
    ]
    can_draft_commit_files = [
        # commit_files is the same as create_files
        IfFileIsLocal(then_=can_review, else_=[SystemProcess()])
    ]
    can_draft_get_content_files = [
        # preview is same as read_files
        IfFileIsLocal(then_=can_draft_read_files, else_=[SystemProcess()])
    ]
    can_draft_update_files = can_review
    can_draft_delete_files = can_review

    # Do not allow to publish using SecretLinks
    can_publish = [
        RecordOwners(),
        RecordCommunitiesAction("curate"),
        SystemProcess(),
    ]

    # Disable lift of embargo (embargo is not allowed)
    can_lift_embargo = [SystemProcess()]
