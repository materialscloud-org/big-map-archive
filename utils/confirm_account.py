from invenio_app.factory import create_app
from flask_security.confirmable import confirm_user
from invenio_accounts.proxies import current_datastore
from invenio_db import db
from invenio_users_resources.services.users.tasks import reindex_user

def confirm_user_account(email):
    """
    Confirm user account if there is an account for the given email address in the database
    :param email: email address of user
    """
    user = current_datastore.get_user(email)

    if user:
        confirm_user(user)
        db.session.commit()
        reindex_user(user.id)
        print("Confirmed account")


if __name__ == '__main__':
    app = create_app()
    ctx = app.app_context()
    ctx.push()

    email = "francois.liot@epfl.ch"
    confirm_user_account(email)
    print("Done")