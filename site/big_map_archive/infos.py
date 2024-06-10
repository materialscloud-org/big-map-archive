# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 BIG-MAP Archive.
#
# BIG-MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""BIG-MAP Archive routes."""

from flask import render_template


def faqs():
    """FAQs page."""
    return render_template(
        "big_map_archive/faqs.html",
    )


def share_links():
    """Share links page."""
    return render_template(
        "big_map_archive/share_links.html",
    )


def tutorial():
    """Tutorial page."""
    return render_template(
        "big_map_archive/tutorial.html",
    )


def licenses():
    """BATTERY2030+ license page."""
    return render_template(
        "big_map_archive/license.html",
    )


def disclaimer():
    """Disclaimer page."""
    return render_template(
        "big_map_archive/disclaimer.html",
    )
