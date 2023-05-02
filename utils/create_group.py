from invenio_app.factory import create_app
from invenio_accounts.proxies import current_datastore


def create_group(group_name, group_description):
    current_datastore.create_role(name=group_name, description=group_description)
    current_datastore.commit()


if __name__ == '__main__':
    app = create_app()

    name = 'instabat_group'
    description = 'The group containing all INSTABAT users.'

    with app.app_context():
        create_group(name, description)
