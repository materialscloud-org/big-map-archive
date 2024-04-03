# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 BIG MAP Archive.
#
# BIG MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record Deposits."""


from flask import current_app, g
from flask_login import login_required
from invenio_app_rdm.records_ui.views.decorators import (pass_draft,
                                                         pass_draft_files)
from invenio_app_rdm.records_ui.views.deposits import (get_form_config,
                                                       get_search_url)
from invenio_communities.errors import CommunityDeletedError
from invenio_communities.proxies import current_communities
from invenio_communities.views.communities import \
    render_community_theme_template
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

    community_theme = None
    community = record.get("expanded", {}).get("parent", {}).get("review", {}).get(
        "receiver"
    ) or record.get("expanded", {}).get("parent", {}).get("communities", {}).get(
        "default"
    )

    if community:
        # TODO: handle deleted community
        try:
            community = current_communities.service.read(
                id_=community["id"], identity=g.identity
            )
            community_theme = community.to_dict().get("theme", {})
        except CommunityDeletedError:
            pass

    # show the community branded header when there is a theme and record is published
    # for unpublished records we fallback to the react component so users can change
    # communities
    community_use_jinja_header = bool(community_theme)

    return render_community_theme_template(
        current_app.config["APP_RDM_DEPOSIT_FORM_TEMPLATE"],
        theme=community_theme,
        forms_config=get_form_config(
            apiUrl=f"/api/records/{pid_value}/draft",
            # maybe quota should be serialized into the record e.g for admins
            quota=get_quota(draft._record),
            # hide react community component
            hide_community_selection=community_use_jinja_header,
        ),
        record=record,
        community=community,
        community_use_jinja_header=community_use_jinja_header,
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
