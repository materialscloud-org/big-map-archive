# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 BIG MAP Archive.
#
# BIG MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record Communities Service."""
import warnings
from datetime import datetime
from functools import partial

from flask import current_app
from invenio_accounts.models import User
from invenio_app_rdm.records_ui.utils import set_default_value
from invenio_drafts_resources.services.records.schema import RecordSchema
from invenio_drafts_resources.services.records.uow import ParentRecordCommitOp
from invenio_i18n import lazy_gettext as _
from invenio_rdm_records.fixtures.tasks import get_authenticated_identity
from invenio_rdm_records.proxies import (current_rdm_records,
                                         current_rdm_records_service)
from invenio_rdm_records.requests.decorators import request_next_link
from invenio_rdm_records.services.communities.service import \
    RecordCommunitiesService
from invenio_rdm_records.services.errors import ReviewNotFoundError
from invenio_rdm_records.services.schemas import RDMRecordSchema
from invenio_rdm_records.services.schemas.access import AccessSchema
from invenio_rdm_records.services.schemas.files import FilesSchema
from invenio_rdm_records.services.schemas.metadata import (
    ContributorSchema, CreatorSchema, DateSchema, DescriptionSchema,
    FeatureSchema, FundingSchema, ReferenceSchema, RelatedIdentifierSchema,
    RightsSchema, TitleSchema, _not_blank, record_identifiers_schemes)
from invenio_rdm_records.services.schemas.parent import RDMParentSchema
from invenio_rdm_records.services.schemas.pids import PIDSchema
from invenio_rdm_records.services.schemas.record import validate_scheme
from invenio_rdm_records.services.schemas.stats import StatsSchema
from invenio_rdm_records.services.schemas.tombstone import (
    DeletionStatusSchema, TombstoneSchema)
from invenio_rdm_records.services.schemas.utils import dump_empty
from invenio_rdm_records.services.schemas.versions import VersionsSchema
from invenio_records.systemfields.relations.errors import InvalidRelationValue
from invenio_records_resources.services.custom_fields import CustomFieldsSchema
from invenio_records_resources.services.uow import (RecordCommitOp,
                                                    RecordDeleteOp,
                                                    RecordIndexOp,
                                                    unit_of_work)
from invenio_vocabularies.contrib.subjects.schema import SubjectRelationSchema
from invenio_vocabularies.services.schema import \
    VocabularyRelationSchema as VocabularySchema
from marshmallow import (EXCLUDE, Schema, ValidationError, fields, post_dump,
                         validate, validates_schema)
from marshmallow_utils.fields import (EDTFDateString, IdentifierSet,
                                      NestedAttribute, SanitizedHTML,
                                      SanitizedUnicode)
from marshmallow_utils.permissions import FieldPermissionsMixin
from marshmallow_utils.schemas import \
    IdentifierSchema as marshmallow_utils_IdentifierSchema
from werkzeug.utils import cached_property


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


# Override function new_record in invenio_app_rdm.records_ui.views
# Set access of new records to restricted
def new_record():
    """Create an empty record with default values."""
    record = dump_empty(RDMRecordSchema)
    record['access']['record'] = 'restricted'
    record['access']['files'] = 'restricted'
    record['access']['status'] = 'restricted'
    record["files"] = {"enabled": current_app.config.get("RDM_DEFAULT_FILES_ENABLED")}
    if "doi" in current_rdm_records.records_service.config.pids_providers:
        record["pids"] = {"doi": {"provider": "external", "identifier": ""}}
    else:
        record["pids"] = {}
    record["status"] = "draft"
    defaults = current_app.config.get("APP_RDM_DEPOSIT_FORM_DEFAULTS") or {}
    for key, value in defaults.items():
        set_default_value(record, value, key)
    return record


# Override function submit in invenio_rdm_records.services.review.service
# Do not send an email to the community owner(s) when a record is directly published to that community
@request_next_link()
@unit_of_work()
def submit(self, identity, id_, data=None, require_review=False, uow=None):
    """Submit record for review or direct publish to the community."""

    if not isinstance(require_review, bool):
        raise ValidationError(
            _("Must be a boolean, true or false"),
            field_name="require_review",
        )

    draft = self.draft_cls.pid.resolve(id_, registered_only=False)
    # Preconditions
    if draft.parent.review is None:
        raise ReviewNotFoundError()

    request_type = draft.parent.review.get_object()["type"]
    self._validate_request_type(request_type)

    # since it is submit review action, assume the receiver is community
    community = draft.parent.review.receiver.resolve()

    # Check permission
    self.require_permission(identity, "update_draft", record=draft)

    # create review request
    request_item = current_rdm_records.community_inclusion_service.submit(
        identity, draft, community, draft.parent.review, data, uow
    )
    request = request_item._request

    # This shouldn't be required BUT because of the caching mechanism
    # in the review systemfield, the review should be set with the updated
    # request object
    draft.parent.review = request
    uow.register(ParentRecordCommitOp(draft.parent))

    if not require_review:
        request_item = current_rdm_records.community_inclusion_service.include(
            identity, community, request, uow
        )

    uow.register(RecordIndexOp(draft, indexer=self.indexer))
    return request_item


# Make upload form's description required
class MetadataSchema(Schema):
    """Schema for the record metadata."""
    # Metadata fields
    resource_type = fields.Nested(VocabularySchema, required=True)
    creators = fields.List(
        fields.Nested(CreatorSchema),
        required=True,
        validate=validate.Length(min=1, error=_("Missing data for required field.")),
    )
    title = SanitizedUnicode(required=True, validate=validate.Length(min=3))
    additional_titles = fields.List(fields.Nested(TitleSchema))
    publisher = SanitizedUnicode()
    publication_date = EDTFDateString(required=True)
    subjects = fields.List(fields.Nested(SubjectRelationSchema))
    contributors = fields.List(fields.Nested(ContributorSchema))
    dates = fields.List(fields.Nested(DateSchema))
    languages = fields.List(fields.Nested(VocabularySchema))
    # alternate identifiers
    identifiers = IdentifierSet(
        fields.Nested(
            partial(marshmallow_utils_IdentifierSchema, allowed_schemes=record_identifiers_schemes)
        )
    )
    related_identifiers = fields.List(fields.Nested(RelatedIdentifierSchema))
    sizes = fields.List(
        SanitizedUnicode(validate=_not_blank(_("Size cannot be a blank string.")))
    )
    formats = fields.List(
        SanitizedUnicode(validate=_not_blank(_("Format cannot be a blank string.")))
    )
    version = SanitizedUnicode()
    rights = fields.List(fields.Nested(RightsSchema))
    description = SanitizedHTML(required=True, validate=validate.Length(min=3))
    additional_descriptions = fields.List(fields.Nested(DescriptionSchema))
    locations = fields.Nested(FeatureSchema)
    funding = fields.List(fields.Nested(FundingSchema))
    references = fields.List(fields.Nested(ReferenceSchema))


class BMA_RDMRecordSchema(RecordSchema, FieldPermissionsMixin):
    """Record schema."""
    class Meta:
        """Meta attributes for the schema."""

        unknown = EXCLUDE

    # ATTENTION: In this schema you should be using the ``NestedAttribute``
    # instead  of Marshmallow's ``fields.Nested``. Using NestedAttribute
    # ensures that the nested schema will receive the system field instead of
    # the record dict (i.e. record.myattr instead of record['myattr']).
    pids = fields.Dict(
        keys=SanitizedUnicode(validate=validate_scheme),
        values=fields.Nested(PIDSchema),
    )
    metadata = NestedAttribute(MetadataSchema)
    custom_fields = NestedAttribute(
        partial(CustomFieldsSchema, fields_var="RDM_CUSTOM_FIELDS")
    )
    # provenance
    access = NestedAttribute(AccessSchema)
    files = NestedAttribute(FilesSchema)
    media_files = NestedAttribute(FilesSchema)
    # notes = fields.List(fields.Nested(InternalNoteSchema))
    revision = fields.Integer(dump_only=True)
    versions = NestedAttribute(VersionsSchema, dump_only=True)
    parent = NestedAttribute(RDMParentSchema)
    is_published = fields.Boolean(dump_only=True)
    status = fields.String(dump_only=True)

    tombstone = fields.Nested(TombstoneSchema, dump_only=True)
    deletion_status = fields.Nested(DeletionStatusSchema, dump_only=True)

    stats = NestedAttribute(StatsSchema, dump_only=True)
    # schema_version = fields.Integer(dump_only=True)

    def default_nested(self, data):
        """Serialize fields as empty dict for partial drafts.

        Cannot use marshmallow for Nested fields due to issue:
        https://github.com/marshmallow-code/marshmallow/issues/1566
        https://github.com/marshmallow-code/marshmallow/issues/41
        and more.
        """
        if not data.get("metadata"):
            data["metadata"] = {}
        # set publication date, this is necessary when creating a record using the api
        if not data["metadata"].get("publication_date"):
            data["metadata"]["publication_date"] = datetime.now().strftime("%Y-%m-%d")
        if not data.get("pids"):
            data["pids"] = {}
        if not data.get("custom_fields"):
            data["custom_fields"] = {}
        return data

    def hide_tombstone(self, data):
        """Hide tombstone info if the record isn't deleted and metadata if it is."""
        is_deleted = (data.get("deletion_status") or {}).get("is_deleted", False)
        tombstone_visible = (data.get("tombstone") or {}).get("is_visible", True)

        if not is_deleted or not tombstone_visible:
            data.pop("tombstone", None)

        return data

    @post_dump
    def post_dump(self, data, many, **kwargs):
        """Perform some updates on the dumped data."""
        data = self.default_nested(data)
        data = self.hide_tombstone(data)
        return data


# Allow multipart file upload
@cached_property
def init_s3fs_info(self):
    """Gather all the information needed to start the S3FSFileSystem."""

    if 'S3_ACCCESS_KEY_ID' in current_app.config:
        current_app.config['S3_ACCESS_KEY_ID'] = current_app.config[
            'S3_ACCCESS_KEY_ID']
        warnings.warn(
            'Key S3_ACCCESS_KEY_ID contained a typo and has been '
            'corrected to S3_ACCESS_KEY_ID, support for the '
            'flawed version will be removed.',
            DeprecationWarning
        )

    if 'S3_SECRECT_ACCESS_KEY' in current_app.config:
        current_app.config['S3_SECRET_ACCESS_KEY'] = current_app.config[
            'S3_SECRECT_ACCESS_KEY']
        warnings.warn(
            'Key S3_SECRECT_ACCESS_KEY contained a typo and has been '
            'corrected to S3_SECRET_ACCESS_KEY, support for the '
            'flawed version will be removed.',
            DeprecationWarning
        )

    info = dict(
        key=current_app.config.get('S3_ACCESS_KEY_ID', ''),
        secret=current_app.config.get('S3_SECRET_ACCESS_KEY', ''),
        client_kwargs={},
        config_kwargs={
            's3': {
                'addressing_style': 'path',
            },
            'signature_version': current_app.config.get(
                'S3_SIGNATURE_VERSION', 's3v4'
            ),
        },
        s3_additional_kwargs={
            'ACL': 'private',
        },
    )

    s3_endpoint = current_app.config.get('S3_ENDPOINT_URL', None)
    if s3_endpoint:
        info['client_kwargs']['endpoint_url'] = s3_endpoint

    region_name = current_app.config.get('S3_REGION_NAME', None)
    if region_name:
        info['client_kwargs']['region_name'] = region_name

    return info


# When trying to publish a draft, raise an exception if no community has been selected for the draft
@unit_of_work()
def publish(self, identity, id_, uow=None, expand=False):
    """Publish a draft.

    Idea:
        - Get the draft from the data layer (draft is not passed in)
        - Validate it more strictly than when it was originally saved
          (drafts can be incomplete but only complete drafts can be turned
          into records)
        - Create or update associated (published) record with data
    """
    # Get the draft
    draft = self.draft_cls.pid.resolve(id_, registered_only=False)
    self.require_permission(identity, "publish", record=draft)

    # Validate the draft strictly - since a draft can be saved with errors
    # we do a strict validation here to make sure only valid drafts can be
    # published.
    self._validate_draft(identity, draft)

    # Raise an exception if no community has been selected for the draft
    if not bool(draft.parent.communities.ids):
        raise Exception('Please select a community.')

    # Create the record from the draft
    latest_id = draft.versions.latest_id
    record = self.record_cls.publish(draft)

    # Run components
    self.run_components("publish", identity, draft=draft, record=record, uow=uow)

    # Commit and index
    uow.register(RecordCommitOp(record, indexer=self.indexer))
    uow.register(RecordDeleteOp(draft, force=False, indexer=self.indexer))

    if latest_id:
        self._reindex_latest(latest_id, uow=uow)

    return self.result_item(
        self,
        identity,
        record,
        links_tpl=self.links_item_tpl,
        expandable_fields=self.expandable_fields,
        expand=expand,
    )
