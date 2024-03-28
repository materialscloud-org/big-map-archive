// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";
import { connect as connectFormik } from "formik";
import _get from "lodash/get";
import _omit from "lodash/omit";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { connect } from "react-redux";
import { Button, Icon, Message, Modal } from "semantic-ui-react";
import {
  DepositFormSubmitActions,
  DepositFormSubmitContext,
} from "@js/invenio_rdm_records/src/deposit/api/DepositFormSubmitContext";
import { DRAFT_PUBLISH_STARTED } from "@js/invenio_rdm_records/src/deposit/state/types";
import { getInputFromDOM } from "@js/invenio_rdm_records/";

class BMAPublishButtonComponent extends Component {
  state = { isConfirmModalOpen: false };

  static contextType = DepositFormSubmitContext;

  openConfirmModal = () => {
    return this.setState({ isConfirmModalOpen: true })
  };

  closeConfirmModal = () => this.setState({ isConfirmModalOpen: false });

  handlePublish = (event, handleSubmit, publishWithoutCommunity) => {
    let publication_date = this.props.formik.values.metadata.publication_date;
    // this should never happen because publication date is already set
    if (publication_date === undefined || publication_date === null) {
      this.props.formik.values.metadata.publication_date = new Date().toISOString().slice(0, 10);
    }
    const { setSubmitContext } = this.context;

    setSubmitContext(
      publishWithoutCommunity
        ? DepositFormSubmitActions.PUBLISH_WITHOUT_COMMUNITY
        : DepositFormSubmitActions.PUBLISH
    );
    handleSubmit(event);
    this.closeConfirmModal();
  };

  isDisabled = (values, isSubmitting, numberOfFiles) => {
    const filesEnabled = _get(values, "files.enabled", false);
    const filesMissing = filesEnabled && !numberOfFiles;
    const communityIds = _get(values, "parent.communities.ids", []);
    const communityMissing = communityIds.length === 0;
    const record = getInputFromDOM("deposits-record");
    const permissions = getInputFromDOM("deposits-record-permissions");

    var disabled;
    record["id"]
    ? disabled = isSubmitting || filesMissing || communityMissing || !permissions?.can_publish
    : disabled = isSubmitting || filesMissing || communityMissing

    return disabled;
  };

  render() {
    const {
      actionState,
      numberOfFiles,
      buttonLabel,
      publishWithoutCommunity,
      formik,
      publishModalExtraContent,
      ...ui
    } = this.props;
    const { isConfirmModalOpen } = this.state;
    const { values, isSubmitting, handleSubmit } = formik;

    const uiProps = _omit(ui, ["dispatch"]);

    return (
      <>
        <Button
          disabled={this.isDisabled(values, isSubmitting, numberOfFiles)}
          name="publish"
          onClick={this.openConfirmModal}
          positive
          icon="upload"
          loading={isSubmitting && actionState === DRAFT_PUBLISH_STARTED}
          labelPosition="left"
          content={buttonLabel}
          {...uiProps}
          type="button" // needed so the formik form doesn't handle it as submit button i.e enable HTML validation on required input fields
        />
        {isConfirmModalOpen && (
          <Modal
            open={isConfirmModalOpen}
            onClose={this.closeConfirmModal}
            size="small"
            closeIcon
            closeOnDimmerClick={false}
          >
            <Modal.Content>
              <Message visible warning>
                <p>
                  <Icon name="warning sign" />{" "}
                  {i18next.t(
                    "Once your record is shared, you can no longer make it private to you."
                  )}
                </p>
              </Message>
              {publishModalExtraContent && (
                <div dangerouslySetInnerHTML={{ __html: publishModalExtraContent }} />
              )}
            </Modal.Content>
            <Modal.Actions>
              <Button onClick={this.closeConfirmModal} floated="left">
                {i18next.t("Cancel")}
              </Button>
              <Button
                onClick={(event) =>
                  this.handlePublish(event, handleSubmit, publishWithoutCommunity)
                }
                positive
                content={buttonLabel}
              />
            </Modal.Actions>
          </Modal>
        )}
      </>
    );
  }
}

BMAPublishButtonComponent.propTypes = {
  buttonLabel: PropTypes.string,
  publishWithoutCommunity: PropTypes.bool,
  actionState: PropTypes.string,
  numberOfFiles: PropTypes.number.isRequired,
  formik: PropTypes.object.isRequired,
  publishModalExtraContent: PropTypes.string,
};

BMAPublishButtonComponent.defaultProps = {
  buttonLabel: i18next.t("Share with community"),
  publishWithoutCommunity: false,
  actionState: undefined,
  publishModalExtraContent: undefined,
};

const mapStateToProps = (state) => ({
  actionState: state.deposit.actionState,
  numberOfFiles: Object.values(state.files.entries).length,
  publishModalExtraContent: state.deposit.config.publish_modal_extra,
});

export const BMAPublishButton = connect(
  mapStateToProps,
  null
)(connectFormik(BMAPublishButtonComponent));