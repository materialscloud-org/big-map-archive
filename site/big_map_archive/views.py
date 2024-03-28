"""Additional views."""

from datetime import datetime

import babel
from flask import Blueprint, current_app, g, redirect, render_template
from flask_principal import AnonymousIdentity
from flask_security.utils import url_for_security

from .deposits import deposit_edit
from .infos import faqs, share_links

#
# BIG-MAP Archive blueprint
#


def not_found_template():
    """Not Found template."""
    return render_template(current_app.config["THEME_404_TEMPLATE"])


def bma_search():
    """Search view function: /search"""
    if isinstance(g.identity, AnonymousIdentity):
        return redirect(url_for_security('login'))
    return render_template(current_app.config["SEARCH_UI_SEARCH_TEMPLATE"])


def bma_send_confirmation():
    """Send confirmation view function: /confirm"""
    return redirect(url_for_security('login'))


def create_blueprint(app):
    """Register BIG-MAP Archive blueprint routes on app."""

    routes_bmarchive = app.config.get("BM_ARCHIVE_ROUTES")

    # override views functions
    @app.before_first_request
    def override_view_functions():
        # override deposit_edit function
        app.view_functions["invenio_app_rdm_records.deposit_edit"] = deposit_edit

        # override user requets function
        app.view_functions["invenio_app_rdm_users.requests"] = not_found_template

        # override search function, prevent non-authenticated users from accessing search page
        app.view_functions["invenio_search_ui.search"] = bma_search

        # prevent users from creating accounts by redirecting to login page
        # Not needed as set SECURITY_REGISTERABLE to False in invenio.cfg
        # app.view_functions["security.register"] = bma_register

        # prevent users from asking for new confirmation email
        app.view_functions["security.send_confirmation"] = bma_send_confirmation

        # override view help/versioning
        app.view_functions["invenio_app_rdm.help_versioning"] = not_found_template

        # override view /me/communities
        app.view_functions["invenio_app_rdm_users.communities"] = not_found_template

    @app.template_filter()
    def format_datetime(value, format='basic'):
        if isinstance(value, str):
            date_format = "%Y-%m-%dT%H:%M:%S.%f%z"
            value = datetime.strptime(value, date_format)
        if format == 'basic':
            format = "MMMM d, YYYY"
        return babel.dates.format_datetime(value, format)

    blueprint = Blueprint(
        "big_map_archive",
        __name__,
        template_folder="./templates",
    )

    # "/help/faqs",
    blueprint.add_url_rule(
        routes_bmarchive["faqs"],
        view_func=faqs,
    )

    # "/help/share_links",
    blueprint.add_url_rule(
        routes_bmarchive["share_links"],
        view_func=share_links,
    )

    # Add URL rules
    return blueprint


# Override all communities ui views: COMMUNITIES_ROUTES
# Remove all
def invenio_communities_create_ui_blueprint(app):
    """Override all ui blueprint routes in invenio_communities.

    routes: COMMUNITIES_ROUTES
    """
    blueprint = Blueprint(
        "invenio_communities",
        __name__,
        template_folder="",
        static_folder="",
    )

    return blueprint


# Override all communities ui views: RDM_COMMUNITIES_ROUTES
# Remove all
def invenio_app_rdm_communities_ui_create_ui_blueprint(app):
    """Override all ui blueprint communities routes in invenio_app_rdm.

    routes: RDM_COMMUNITIES_ROUTES
    """
    blueprint = Blueprint(
        "invenio_app_rdm_communities",
        __name__,
        template_folder="",
        static_folder="",
    )

    return blueprint


# Override all requests ui views: RDM_REQUESTS_ROUTES
# Remove all
def invenio_app_rdm_requests_ui_create_ui_blueprint(app):
    """Override all ui blueprint requests routes in invenio_app_rdm.

    routes: RDM_REQUESTS_ROUTES
    """
    blueprint = Blueprint(
        "invenio_app_rdm_requests",
        __name__,
        template_folder="",
        static_folder="",
    )

    return blueprint


# Override all ui blueprint invenio_notifications_settings
def invenio_notifications_create_blueprint_settings(app):
    """Override all ui blueprint invenio_notifications_settings routes in invenio_notifications.

    Do not associate route ("/accounts/settings/notifications/", methods=["GET", "POST"]) with blueprint below
    route: /accounts/settings/notifications/
    """
    blueprint = Blueprint(
        "invenio_notifications_settings",
        __name__,
        template_folder="templates/settings",
        url_prefix="/account/settings/notifications",
        static_folder="static",
    )

    return blueprint
