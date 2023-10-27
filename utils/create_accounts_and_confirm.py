from invenio_app.factory import create_app
from flask_security.confirmable import confirm_user
from invenio_accounts.proxies import current_datastore
from invenio_db import db
from invenio_users_resources.services.users.tasks import reindex_user
from flask_security.utils import hash_password
from random import randint
import json


def create_user_account(email):
    """
    Create a user account if there is no account for the given email address in the database yet
    and confirm it
    :param email: email address of user
    """
    user = current_datastore.get_user(email)
    number_of_digits = 10

    if not user:
        with db.session.begin_nested():
            password = "CHANGE_ME"
            user = current_datastore.create_user(
                email=email,
                password=hash_password(password),
                active=True,
                preferences=dict(visibility="public", email_visibility="public"),
            )
        confirm_user(user)
        db.session.commit()
        reindex_user(user.id)
        print("Created new account for {}".format(email))


if __name__ == '__main__':
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    
    f = open('users_batman2023.json')
    data = json.load(f)
 
    for email in data['emails']:
        print(email)
        create_user_account(email)
 
    f.close()

    print("Done")
