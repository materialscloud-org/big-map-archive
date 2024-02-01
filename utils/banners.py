# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 BIG MAP Archive.
#
# BIG MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""BM Archive Banners."""

from invenio_access.permissions import system_identity
from invenio_banners.proxies import current_banners_service as service
from datetime import datetime, timedelta
from invenio_banners.records import BannerModel
from invenio_app.factory import create_app


def create_banner(message, url_path, category, start_datetime, end_datetime, active):
    """Create a banner

    :param message: banner message
    :url_path: path of the page where the banner should appear
    :category: info or warning
    :start_datetime: start date and time when the banner become visible
    :end_datetime: end date and time when the banner is no longer visible
    :active: status of banner, True or False
    """
    data = {
        "message": message,
        "url_path": url_path,
        "category": category,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "active": active,
    }

    banner = service.create(system_identity, data)
    return banner["id"]


def search_banner():
    """Search banners

    :returns: list of banners
    """

    search_params = {
        "q": "true",
        "sort": "end_datetime",
        "size": 10000,
        "sort_direction": "desc",
    }

    banner_list = service.search(system_identity, params=search_params)

    result_list = banner_list.to_dict()["hits"]["hits"]
    return result_list


def update_banner(id, message, url_path, category, start_datetime, end_datetime, active):
    """Update a banner

    :param id: banner id, int
    :param message: banner message
    :url_path: path of the page where the banner should appear
    :category: info or warning
    :start_datetime: start date and time when the banner become visible
    :end_datetime: end date and time when the banner is no longer visible
    :active: status of banner, True or False
    """
    if start_datetime:
        start_datetime = start_datetime.strftime("%Y-%m-%d %H:%M:%S")
    if end_datetime:
        end_datetime = end_datetime.strftime("%Y-%m-%d %H:%M:%S")

    data = {
        "message": message,
        "url_path": url_path,
        "category": category,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "active": active,
    }
    service.update(system_identity, id, data)


def delete_banner(id):
    """Delete banner

    :param id: banner id, int
    """
    service.delete(system_identity, id)
    assert BannerModel.query.filter_by(id=id).one_or_none() is None


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        message = '\
            <div class="ui visible warning message bma_banner">\
            <p>\
                <i aria-hidden="true" class="warning sign icon"></i>\
                This is a demo site where you can explore and test the archive\'s functionalities of the next release.<br>\
                It is only for testing and data will be deleted at any time. Do NOT store here confidential data or information.<br>\
                If you are a member of the BIG-MAP project you can use the <a href="https://archive.big-map.eu/" style="text-decoration: underline;" target="_blank">main archive</a> for storing and sharing research data.\
            </p>\
            </div>\
        '

        url_path = "/"

        # categories are: info, warning
        category = "warning"

        start_datetime = datetime.utcnow()

        # keep banner forever
        # end_datetime = datetime.utcnow() + timedelta(days=1)
        end_datetime = None

        active = True

        # id = create_banner(message, url_path, category, start_datetime, end_datetime, active)
        # update_banner(id, message, url_path, category, start_datetime, end_datetime, active)
        # delete_banner(id)

        # Examples
        # update_banner(6, message, url_path, category, start_datetime, end_datetime, active)
        # delete_banner(6)
