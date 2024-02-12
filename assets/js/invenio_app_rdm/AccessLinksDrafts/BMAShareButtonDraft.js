// This file is part of BIG-MAP Archive
// Copyright (C) 2024 BIG-MAP Archive Team.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useState } from "react";
import { Icon, Button, Popup } from "semantic-ui-react";
import { BMAShareModalDraft } from "./BMAShareModalDraft";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import PropTypes from "prop-types";

export const BMAShareButtonDraft = ({
  disabled,
  record,
  permissions,
  accessLinksSearchConfig,
}) => {
  const [modalOpen, setModalOpen] = useState(false);
  const handleOpen = () => setModalOpen(true);
  const handleClose = () => setModalOpen(false);

  return (
    <>
      <Popup
        content={i18next.t("You don't have permissions to share this record.")}
        disabled={!disabled}
        trigger={
          <Button
            fluid
            onClick={handleOpen}
            disabled={disabled}
            primary
            size="medium"
            aria-haspopup="dialog"
            icon
            labelPosition="left"
          >
            <Icon name="share square" />
            {i18next.t("Share with link")}
          </Button>
        }
      />
      <BMAShareModalDraft
        open={modalOpen}
        handleClose={handleClose}
        record={record}
        permissions={permissions}
        accessLinksSearchConfig={accessLinksSearchConfig}
      />
    </>
  );
};

BMAShareButtonDraft.propTypes = {
  disabled: PropTypes.bool,
  record: PropTypes.object.isRequired,
  permissions: PropTypes.object.isRequired,
};

BMAShareButtonDraft.defaultProps = {
  disabled: false,
};
