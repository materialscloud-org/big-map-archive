# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 BIG MAP Archive.
#
# BIG MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record Communities Service."""
from invenio_accounts.models import User
from invenio_i18n import lazy_gettext as _
from invenio_notifications.services.uow import NotificationOp
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_rdm_records.fixtures.tasks import get_authenticated_identity
from invenio_rdm_records.notifications.builders import \
    CommunityInclusionSubmittedNotificationBuilder
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.services.communities.service import \
    RecordCommunitiesService
from invenio_rdm_records.services.errors import (CommunityAlreadyExists,
                                                 InvalidAccessRestrictions,
                                                 OpenRequestAlreadyExists)
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_records_resources.services.uow import IndexRefreshOp, unit_of_work
from sqlalchemy.orm.exc import NoResultFound


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

    @unit_of_work()
    def add(self, identity, record, data, uow):
        """Include the record in the given communities."""
        valid_data, errors = self.schema.load(
            data,
            context={
                "identity": identity,
                "max_number": self.config.max_number_of_additions,
            },
            raise_errors=True,
        )
        communities = valid_data["communities"]

        # record = self.record_cls.pid.resolve(id_)
        self.require_permission(identity, "add_community", record=record)

        processed = []
        for community in communities:
            community_id = community["id"]
            comment = community.get("comment", None)
            require_review = community.get("require_review", False)

            result = {
                "community_id": community_id,
            }
            try:
                request_item = self._include(
                    identity, community_id, comment, require_review, record, uow
                )
                result["request_id"] = str(request_item.data["id"])
                result["request"] = request_item.to_dict()
                processed.append(result)
                uow.register(
                    NotificationOp(
                        CommunityInclusionSubmittedNotificationBuilder.build(
                            request_item._request
                        )
                    )
                )
            except (NoResultFound, PIDDoesNotExistError):
                result["message"] = _("Community not found.")
                errors.append(result)
            except (
                CommunityAlreadyExists,
                OpenRequestAlreadyExists,
                InvalidAccessRestrictions,
                PermissionDeniedError,
            ) as ex:
                result["message"] = ex.description
                errors.append(result)

        uow.register(IndexRefreshOp(indexer=self.indexer))
        return processed, errors
