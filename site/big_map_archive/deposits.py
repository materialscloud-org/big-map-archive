# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 BIG MAP Archive.
#
# BIG MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record Deposits."""


from flask import current_app, render_template
from flask_login import login_required
from invenio_app_rdm.records_ui.views.decorators import (pass_draft,
                                                         pass_draft_files)
from invenio_app_rdm.records_ui.views.deposits import (get_form_config,
                                                       get_search_url)
from invenio_rdm_records.records.api import get_quota
from invenio_rdm_records.resources.serializers import UIJSONSerializer


@login_required
@pass_draft(expand=True)
@pass_draft_files
def deposit_edit(pid_value, draft=None, draft_files=None, files_locked=True):
    """Override deposit edit to include permissions update_draft and publish."""
    files_dict = None if draft_files is None else draft_files.to_dict()
    ui_serializer = UIJSONSerializer()
    record = ui_serializer.dump_obj(draft.to_dict())

    return render_template(
        current_app.config["APP_RDM_DEPOSIT_FORM_TEMPLATE"],
        forms_config=get_form_config(
            apiUrl=f"/api/records/{pid_value}/draft",
            # maybe quota should be serialized into the record e.g for admins
            quota=get_quota(draft._record),
        ),
        record=record,
        files=files_dict,
        searchbar_config=dict(searchUrl=get_search_url()),
        files_locked=files_locked,
        permissions=draft.has_permissions_to(
            [
                "new_version",
                "delete_draft",
                "manage_files",
                "manage_record_access",
                "update_draft",
                "publish",
            ]
        ),
    )
