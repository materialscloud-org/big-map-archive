"""Additional views."""

from datetime import datetime

import babel
from flask import Blueprint, current_app, g, redirect, render_template
from flask_principal import AnonymousIdentity
from flask_security.utils import url_for_security
from invenio_previewer.proxies import current_previewer

from .deposits import deposit_edit
from .infos import disclaimer, faqs, licenses, share_links, tutorial

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

    routes_bmarchive = {
        "faqs": "/help/faqs",
        "share_links": "/help/share_links",
        "tutorial": "/help/tutorial",
        "licenses": "/licenses/nonexclusive-distrib/1.1",
        "disclaimer": "/about/disclaimer",
    }

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

        # override list of previewable_extensions, remove csv and pdf
        current_previewer.previewable_extensions = {
            v for v in current_previewer.previewable_extensions if v not in ["csv", "pdf", "pdfa"]
        }

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

    # "/help/faqs"
    blueprint.add_url_rule(
        routes_bmarchive["faqs"],
        view_func=faqs,
    )

    # "/help/share_links"
    blueprint.add_url_rule(
        routes_bmarchive["share_links"],
        view_func=share_links,
    )

    # "/help/tutorial"
    blueprint.add_url_rule(
        routes_bmarchive["tutorial"],
        view_func=tutorial,
    )

    # "/licenses/nonexclusive-distrib/1.1"
    blueprint.add_url_rule(
        routes_bmarchive["licenses"],
        view_func=licenses,
    )

    # "/about/disclaimer"
    blueprint.add_url_rule(
        routes_bmarchive["disclaimer"],
        view_func=disclaimer,
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
