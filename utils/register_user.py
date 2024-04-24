from flask_security.confirmable import confirm_user

from invenio_accounts.proxies import current_datastore
from invenio_db import db
from invenio_users_resources.services.users.tasks import reindex_user
from invenio_app.factory import create_app

def create_user_account(email):
    """
    Create a user account if there is no account for the given email address in the database yet,
    confirm it and reindex users index
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
    else:
        print("\033[94mWARNING: An account for user {} already exists.\033[0m".format(email))

if __name__ == '__main__':
    app = create_app()
    ctx = app.app_context()
    ctx.push()

    email="CHANGE_ME"
    create_user_account(email)
