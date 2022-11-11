import time

from flask import current_app
from flask_security.confirmable import confirm_user
from flask_security.signals import reset_password_instructions_sent
from flask_security.utils import config_value, send_mail
from flask_mail import Mail, Message

from invenio_accounts.proxies import current_datastore
from invenio_accounts.utils import default_reset_password_link_func
from invenio_db import db
from invenio_users_resources.services.users.tasks import reindex_user
from invenio_app.factory import create_app


def read_users(file):
    import json

    f = open(file)
    data = json.load(f)
    accounts_created = 0
    for i in data:
        accounts_created += 1
        print("Creating user account n. {}".format(accounts_created))
        create_user_account(i['email'])


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
                preferences=dict(visibility="public", email_visibility="public"),
            )
        confirm_user(user)
        db.session.commit()
        reindex_user(user.id)
        print("\033[92mCreated account for {} with password {}.\033[0m".format(email, password))

        if not current_datastore.get_user(email):
            print("\033[91mERROR: the account for {} has not been created.\033[0m".format(email))
            print("\n")
            return

        # send_welcome_email(user)
        # print("\033[92mSent welcome email to {}\033[0m".format(email))

        # wait 10 seconds and then send email to reset password
        # this is to avoid that the reset password email arrives before the
        # welcome email
        # time.sleep(10)
        #
        # send_reset_password_email(user)
        # print("\033[92mSent email to reset password to {}\033[0m".format(email))
        # print("\n")
    else:
        print("\033[94mWARNING: An account for user {} already exists.\033[0m".format(email))


def big_map_send_email(recipients, subject, email_body):
    """Send email"""

    mail = Mail(app)
    sender = app.config['SUPPORT_EMAIL']

    msg = Message(subject, sender=sender, recipients=[recipients], body=email_body)

    mail.send(msg)


def send_welcome_email(user):
    """Send welcome email."""
    subject = "Welcome to the BIG MAP ARCHIVE"
    email_body = "\
    Dear Big Map member,\n\
    \n\
    An account has been created for you at BIG MAP ARCHIVE (https://big-map-archive.big-map.eu)\n\
    You will shortly receive an email with a link to reset your password, click on the link and\n\
    choose and insert a password, click on \"Reset password\". The password should be minimum 6 characters.\n\
    \n\
    Once logged in you can start to upload records by clicking on \"Upload a record\" on the menu bar. \n\
    You can access the records you have created by clicking on \"My records\". \n\
    If you encounter any problems logging in, please contact us at big-map-archive@materialscloud.org.\n\
    \n\
    We thank you very much and we wish you a nice day.\n\
    \n\
    Best regards,\n\
    The BIG MAP ARCHIVE team\
    "
    big_map_send_email(recipients=user.email, subject=subject, email_body=email_body)


def send_reset_password_email(user):
    """Send email containing instructions to reset password."""
    token, reset_link = default_reset_password_link_func(user)
    subject = "BIG MAP ARCHIVE: please reset your password"

    if config_value("SEND_PASSWORD_RESET_EMAIL"):
        send_mail(
            subject,
            user.email,
            "reset_instructions",
            user=user,
            reset_link=reset_link,
        )
        reset_password_instructions_sent.send(
            current_app._get_current_object(), user=user, token=token
        )


def set_member_community(community, user):
    """Set user as member of community"""
    # TODO
    pass


if __name__ == '__main__':
    app = create_app()
    ctx = app.app_context()
    ctx.push()

    file = '../app_data/users.json'
    read_users(file)