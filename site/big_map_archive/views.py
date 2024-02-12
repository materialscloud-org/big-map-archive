"""Additional views."""

from flask import Blueprint

from .deposits import deposit_edit


#
# Registration
#
def create_blueprint(app):
    """Register blueprint routes on app."""

    # override view function for deposit_edit
    @app.before_first_request
    def upload_form_view_function_deposit_edit():
        app.view_functions["invenio_app_rdm_records.deposit_edit"] = deposit_edit

    blueprint = Blueprint(
        "big_map_archive",
        __name__,
        template_folder="./templates",
    )

    # Add URL rules
    return blueprint
