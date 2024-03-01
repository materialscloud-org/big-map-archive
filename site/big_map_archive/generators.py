# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 BIG MAP Archive.
#
# BIG MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""BIG MAP Archive permissions."""


from flask import g
from invenio_access.permissions import any_user, system_identity
from invenio_rdm_records.proxies import current_rdm_records
from invenio_records_permissions.generators import Generator
from invenio_search.engine import dsl


class AnyUserWithSecretLink(Generator):
    """Allows any user with SecretLink to read community."""

    def needs(self, record=None, **kwargs):
        """Enabling Needs.

        param record: community
        """
        if record is None:
            # 'record' is required, so if not passed we default to empty array,
            # i.e. superuser-access.
            return []

        # get secret_links
        secret_link = [n.value for n in g.identity.provides if n.method == "link"]

        if not secret_link:
            # secret_link is required
            return []

        # check community is in parent
        communities_ids = self.get_communities_from_secret_link(secret_link)
        community_id = [_id for _id in communities_ids if _id == str(record.id)]

        return [any_user] if community_id else []

    def get_communities_from_secret_link(self, secret_link):
        """ Get the communities of the record from the secret link id.

        @param secret_link: secret link id
        """
        # TODO case of draft
        service = current_rdm_records.records_service
        _filter = dsl.Q("terms", **{"parent.access.links.id": secret_link})

        # get latest version of record
        records = service.scan(identity=system_identity, extra_filter=_filter)

        for record in records:
            communities = record["parent"].get("communities", None)
            return communities.get("ids", None)

        return []
