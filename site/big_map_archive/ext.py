# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 BIG MAP Archive.
#
# BIG MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record Communities Service."""
from invenio_accounts.models import User
from invenio_rdm_records.fixtures.tasks import get_authenticated_identity
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.services.communities.service import \
    RecordCommunitiesService


class BMArchiveRecordCommunitiesService(RecordCommunitiesService):
    """BIG MAP Archive Record communities service for drafts.

    Note: rewrites the add method of RecordCommunitiesService
    because it does not work for drafts but only for records.
    This is needed in the v12 migration.
    """

    def add_draft_to_community(self, user, community_id, record):
        """Create review in parent and community-submission request in status created

        This will set by default the selected community in the upload form
        """
        user = User.query.filter_by(email=user.email).one()
        user_identity = get_authenticated_identity(user.id)

        review_service = current_rdm_records_service.review

        review = {
            "receiver": {
                "community": community_id
            },
            "type": "community-submission"
        }

        review_service.create(user_identity, review, record)
