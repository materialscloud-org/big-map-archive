# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 BIG-MAP Archive.
#
# BIG-MAP Archive is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Routes for faqs pages."""

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