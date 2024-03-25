# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 BIG MAP Archive.
#
# BIG MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Permissions for BIG-MAP Archive Records."""
from invenio_communities.generators import (CommunityMembers,
                                            IfCommunityDeleted, IfPolicyClosed)
from invenio_communities.generators import \
    IfRestricted as CommunityIfRestricted
from invenio_communities.permissions import CommunityPermissionPolicy
from invenio_rdm_records.services.generators import (
    CommunityInclusionReviewers, IfFileIsLocal, IfRestricted,
    RecordCommunitiesAction, RecordOwners, ResourceAccessToken, SecretLinks)
from invenio_rdm_records.services.permissions import RDMRecordPermissionPolicy
from invenio_records_permissions.generators import (AuthenticatedUser, Disable,
                                                    IfConfig, SystemProcess)
from invenio_users_resources.services.permissions import UserManager

from big_map_archive.generators import (AnyUserWithSecretLink,
                                        BMASecretLinks_excludes)


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


class BMACommunityPermissionPolicy(CommunityPermissionPolicy):

    # Important for community selection prior to record sharing
    # Allow AnyUser with secret link to read communities info - needed to make records accessible via SecretLink by anyone
    can_read = [AnyUserWithSecretLink(), CommunityMembers(), SystemProcess()]
    # CommunityPermissionPolicy.can_read = [CommunityMembers(), SystemProcess()]

    # Important for record sharing
    # All communities should have an open record policy (possibility for publishing directly without review) and a restricted visibility
    # record_policy is open => CommunityMembers
    can_submit_record = [
        IfPolicyClosed(
            "record_policy",
            then_=[Disable()],
            else_=[
                CommunityIfRestricted(
                    "visibility",
                    then_=[CommunityMembers()],
                    else_=[Disable()],
                ),
            ],
        ),
    ]

    # Community members are allowed to publish directly without review
    # review_policy is open => CommunityMembers
    can_include_directly = [
        IfPolicyClosed(
            "review_policy",
            then_=[Disable()],
            else_=[CommunityMembers()],
        ),
    ]

    # Used for search filtering of deleted records
    # CommunityPermissionPolicy.can_read_deleted = [
    #     IfCommunityDeleted(then_=[SystemProcess()], else_=[SystemProcess()])
    # ]
    can_search = [AuthenticatedUser(), SystemProcess()]
    can_search_invites = [SystemProcess()]
    can_search_requests = [SystemProcess()]
    can_rename = [SystemProcess()]
    can_create = [SystemProcess()]
    can_update = [SystemProcess()]
    can_delete = [SystemProcess()]
    can_purge = [SystemProcess()]
    can_featured_search = [SystemProcess()]
    can_featured_list = [SystemProcess()]
    can_featured_create = [SystemProcess()]
    can_featured_update = [SystemProcess()]
    can_featured_delete = [SystemProcess()]
    can_members_add = [SystemProcess()]
    can_members_invite = [SystemProcess()]
    can_members_manage = [SystemProcess()]
    can_members_search = [SystemProcess()]
    can_members_search_public = [SystemProcess()]
    can_members_bulk_update = [SystemProcess()]
    can_members_bulk_delete = [SystemProcess()]
    can_members_update = [SystemProcess()]
    can_members_delete = [SystemProcess()]
    can_invite_owners = [SystemProcess()]
    can_moderate = [Disable()]
    can_manage_access = [SystemProcess()]
    can_create_restricted = [SystemProcess()]
