# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 BIG MAP Archive.
#
# BIG MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

""" Create users for demo site """

import os

from invenio_app.factory import create_app
from flask_security.confirmable import confirm_user
from invenio_accounts.proxies import current_datastore
from invenio_db import db
from invenio_users_resources.services.users.tasks import reindex_users
import json


def create_user_account(email):
    """
    Create a user account if there is no account for the given email address in the database yet
    and confirm it
    :param email: email address of user
    """
    user = current_datastore.get_user(email)

    if not user:
        with db.session.begin_nested():
            password = None
            user = current_datastore.create_user(
                email=email,
                password=password,
                active=True,
                preferences=dict(visibility="restricted", email_visibility="restricted"),
            )
        confirm_user(user)
        db.session.commit()
        reindex_users([user.id])
        print("\033[92mCreated account for {} with password {}.\033[0m".format(email, password))

        if not current_datastore.get_user(email):
            print("\033[91mERROR: the account for {} has not been created.\033[0m".format(email))
            print("\n")
            return
    else:
        print("\033[94mWARNING: An account for user {} already exists.\033[0m".format(email))


if __name__ == '__main__':
    """ Create users with no password for demo site.

    Users are created from a file and the communities battery2030 and bigmap are attributed to them.
    """
    app = create_app()
    with app.app_context():
        # Can get emails from production db with:
        # COPY (SELECT array_to_json(array_agg(email), FALSE) AS ok_json FROM accounts_user where active is True) TO '/var/lib/postgresql/data/emails.json';
        # docker cp <CONTAINER_ID>:/var/lib/postgresql/data/emails.json .

        # emails to create accounts for
        file = 'emails.json'
        f = open(file)
        emails = json.load(f)
        # example: emails = ["user1@materialscloud.org","user2@materialscloud.org"]
        for email in emails:
            create_user_account(email)
            # Attribute communities bigmap and battery2030 to user
            os.system(f'invenio bmarchive users add_community bigmap reader {email}')
            os.system(f'invenio bmarchive users add_community battery2030 reader {email}')
