# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 BIG MAP Archive.
#
# BIG MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""BM Archive Record API."""

from invenio_rdm_records.records.api import RDMDraft
from invenio_rdm_records.records.systemfields.access.embargo import Embargo
from invenio_rdm_records.records.systemfields.access.field.record import (
    RecordAccess, RecordAccessField)
from invenio_rdm_records.records.systemfields.access.protection import \
    Protection


class BMAEmbargo(Embargo):
    def __init__(self):
        """Replace class Embargo to set embargo to False."""
        self.until = None
        self.reason = None
        self._active = False


class BMARecordAccess(RecordAccess):
    protection_cls = Protection
    embargo_cls = BMAEmbargo

    def __init__(
        self,
        protection=None,
        embargo=None,
        protection_cls=None,
        embargo_cls=None,
        has_files=None,
    ):
        """Replace class RecordAccess to set record and files as restricted
        and embargo to False.

        :param protection: The record and file protection levels
        :param embargo: The embargo on the record (None means no embargo)
        """

        restricted = Protection("restricted", "restricted")
        self.protection = restricted
        self.embargo = BMAEmbargo()
        self.has_files = has_files
        self.errors = []


class BMARecordAccessField(RecordAccessField):
    def __init__(self, key="access", access_obj_class=BMARecordAccess):
        """Replace class RecordAccessField to set access as restricted."""
        self._access_obj_class = access_obj_class
        super().__init__(key=key, access_obj_class=BMARecordAccess)


class BMARDMDraft(RDMDraft):
    """BMA RDMDraft API class."""
    access = BMARecordAccessField()
