#!/bin/bash
cp $(pipenv --venv)/var/instance/assets/js/invenio_app_rdm/landing_page/ShareOptions/ShareModal.js $(pipenv --venv)/var/instance/assets/js/invenio_app_rdm/landing_page/ShareOptions/ShareModal_original.js
cp override/ShareModal_overridable.js $(pipenv --venv)/var/instance/assets/js/invenio_app_rdm/landing_page/ShareOptions/ShareModal.js