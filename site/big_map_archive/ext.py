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
from invenio_rdm_records.services.schemas.metadata import (
    RelatedIdentifierSchema, record_identifiers_schemes)
from invenio_records.systemfields.relations.errors import InvalidRelationValue
from invenio_vocabularies.services.schema import \
    VocabularyRelationSchema as VocabularySchema
from marshmallow import ValidationError, fields, validates_schema


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


# Validate related_identifiers (references)
class BMARelatedIdentifierSchema(RelatedIdentifierSchema):
    """Related identifier schema."""

    relation_type = fields.Nested(VocabularySchema)
    resource_type = fields.Nested(VocabularySchema)

    @validates_schema
    def validate_related_identifier(self, data, **kwargs):
        """Validate the related identifiers."""
        relation_type = data.get("relation_type")
        errors = dict()

        if not relation_type:
            errors["relation_type"] = self.error_messages["required"]

        if errors:
            raise ValidationError(errors)

        scheme = data.get('scheme', None)
        identifier = data.get('identifier', None)

        if scheme and scheme not in record_identifiers_schemes.keys():
            raise InvalidRelationValue(self.error_messages["invalid_scheme"])

        if identifier and scheme.strip() == "":
            raise InvalidRelationValue(self.error_messages["invalid_scheme"])

        if scheme and identifier:
            validator = record_identifiers_schemes[scheme]["validator"]
            if not validator(identifier):
                raise InvalidRelationValue(f'Invalid {scheme} identifier.')
