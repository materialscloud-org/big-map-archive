// This file is part of BIG-MAP Archive
// Copyright (C) 2024 BIG-MAP Archive Team.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import { Modal, Loader, Button } from "semantic-ui-react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import PropTypes from "prop-types";

import { BMALinksSearchResultContainer } from "./BMALinksSearchResultContainer.js"
import { LinksTab } from "@js/invenio_app_rdm/landing_page/ShareOptions/AccessLinks/LinksTab";

export class BMALinksTab extends LinksTab {
    render() {
      const { results, loading, error } = this.state;
      const { record, handleClose } = this.props;
      return (
        <>
          {error && error}
          <Modal.Content>
            {loading ? (
              <Loader />
            ) : (
              <BMALinksSearchResultContainer
                results={results}
                record={record}
                fetchData={this.fetchData}
              />
            )}
          </Modal.Content>
          <Modal.Actions className="ui clearing segment">
            <Button
              size="small"
              onClick={handleClose}
              content={i18next.t("Cancel")}
              icon="remove"
              className="left floated clearing"
            />
          </Modal.Actions>
        </>
      );
  }
}

BMALinksTab.propTypes = {
  record: PropTypes.object.isRequired,
  handleClose: PropTypes.func.isRequired,
};
