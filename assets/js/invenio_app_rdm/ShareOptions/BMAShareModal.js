// This file is part of BIG-MAP Archive
// Copyright (C) 2024 BIG-MAP Archive Team.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import { Icon, Modal, Tab, Container } from "semantic-ui-react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import PropTypes from "prop-types";
import { BMALinksTab } from "./AccessLinks/BMALinksTab.js";

export class BMAShareModal extends Component {
  constructor(props) {
    super(props);
    const { record } = this.props;
    this.state = {
      record: record,
    };
  }

  handleRecordUpdate = (updatedRecord) => {
    this.setState({ record: updatedRecord });
  };

  panes = (record, accessLinksSearchConfig) => {
    const { handleClose } = this.props;
    return [
      {
        menuItem: { icon: "linkify", content: "Links" },
        pane: (
          <Tab.Pane key="accessLinks" as={Container}>
            <BMALinksTab
              record={record}
              accessLinksSearchConfig={accessLinksSearchConfig}
              handleClose={handleClose}
            />
          </Tab.Pane>
        ),
      },
    ];
  };

  render() {
    const { open, handleClose, accessLinksSearchConfig, permissions } = this.props;
    const { record } = this.state;
    return (
      <Modal
        open={open}
        closeIcon
        onClose={handleClose}
        className="share-modal"
        role="dialog"
        aria-labelledby="access-link-modal-header"
        aria-modal="true"
        tab-index="-1"
        size="large"
        closeOnDimmerClick={false}
      >
        <Modal.Header as="h2" id="access-link-modal-header">
          <Icon name="share square" /> {i18next.t("Share links")}
          <div className="ui mini message">
            <i aria-hidden="true" className="warning sign icon"/>
            Read on the <a href="/help/share_links" target="_blank">access permissions</a> before creating and sharing links.
          </div>
        </Modal.Header>

        <Tab
          menu={{ secondary: true, pointing: true }}
          panes={this.panes(record, accessLinksSearchConfig, permissions)}
          renderActiveOnly={false}
        />
      </Modal>
    );
  }
}

BMAShareModal.propTypes = {
  record: PropTypes.object.isRequired,
  open: PropTypes.bool.isRequired,
  handleClose: PropTypes.func.isRequired,
  accessLinksSearchConfig: PropTypes.object.isRequired,
  permissions: PropTypes.object.isRequired,
};
