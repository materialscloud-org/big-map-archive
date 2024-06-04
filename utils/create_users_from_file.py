# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 BIG MAP Archive.
#
# BIG MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

""" Create users from file """

import os
import secrets
import string

from invenio_app.factory import create_app


def format_emails_list(emails_file):
    """ Create list of emails from file """
    with open(emails_file) as f:
        emails = [email.strip() for email in f]
    return emails


if __name__ == '__main__':
    """ Create users from file with random password.

    Users are created with random password from a file.
    Users are attributed with role reader to the selected community (slug).
    Users are attributed with role reader to the battery2030 community.
    """
    app = create_app()
    with app.app_context():
        # replace path of file
        emails_file = "<file.txt>"
        # replace slug of community
        slug = "<slug>"

        emails = format_emails_list(emails_file)

        # print(emails)
        print(f"Number of users to create: {len(emails)}")

        # example: emails = ["user1@materialscloud.org","user2@materialscloud.org"]
        for email in emails:
            pwd = ''.join((secrets.choice(string.ascii_letters + string.digits) for i in range(16)))
            # print(pwd)
            os.system(f'invenio users create {email} --password={pwd} -c -a')
            # Attribute communities to user
            os.system(f'invenio bmarchive users add_community {slug} reader {email}')
            os.system(f'invenio bmarchive users add_community battery2030 reader {email}')
