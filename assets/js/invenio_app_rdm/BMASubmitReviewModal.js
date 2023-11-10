import { i18next } from "@translations/invenio_rdm_records/i18next";
import { Formik } from "formik";
import _get from "lodash/get";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Trans } from "react-i18next";
import {
  ErrorLabel,
  RadioField,
  TextAreaField,
  ErrorMessage,
} from "react-invenio-forms";
import { Button, Checkbox, Form, Icon, Message, Modal } from "semantic-ui-react";
import * as Yup from "yup";

export class BMASubmitReviewModal extends Component {
  componentDidMount() {
  }

  ConfirmSubmitReviewSchema = Yup.object({
    acceptAccessToRecord: Yup.bool().oneOf([true], i18next.t("You must accept this.")),
    reviewComment: Yup.string(),
  });

  render() {
    const {
      initialReviewComment,
      isConfirmModalOpen,
      community,
      onClose,
      onSubmit,
      publishModalExtraContent,
      directPublish,
      errors,
      loading,
      record,
    } = this.props;
    const communityTitle = community.metadata.title;

    const directPublishCase = () => {
      headerTitle = "";
      msgWarningTitle = i18next.t(
        "Once your record is shared with the {{communityTitle}} community, you can no longer make it private to you or change the community that it is shared with.",
          { communityTitle }
      );
      msgWarningText1 = i18next.t(
        "",
        { communityTitle }
      );
      submitBtnLbl = i18next.t("Share with community");
    };

    let headerTitle, msgWarningTitle, msgWarningText1, submitBtnLbl;
    // if record is passed and it is published
    if (record?.is_published) {
      headerTitle = i18next.t("Submit to community");
      msgWarningTitle = i18next.t(
        "Before submitting to community, please read and check the following:"
      );
      submitBtnLbl = i18next.t("Submit to community");
    }
    // else record is a draft
    else {
      if (directPublish) {
        directPublishCase();
      } else {
        headerTitle = i18next.t("Submit for review");
        msgWarningTitle = i18next.t(
          "Before requesting review, please read and check the following:"
        );
        msgWarningText1 = i18next.t(
          "If your upload is accepted by the community curators, it will be <bold>immediately published</bold>. Before that, you will still be able to modify metadata and files of this upload."
        );
        submitBtnLbl = i18next.t("Submit record for review");
      }
    }

    // acceptAfterPublishRecord checkbox is absent if record is published
    const schema = () => {
      if (record) {
        return this.ConfirmSubmitReviewSchema;
      } else {
        const additionalValidationSchema = Yup.object({
          acceptAfterPublishRecord: Yup.bool().oneOf(
            [true],
            i18next.t("You must accept this.")
          ),
        });
        return this.ConfirmSubmitReviewSchema.concat(additionalValidationSchema);
      }
    };

    return (
      <Formik
        initialValues={{
          acceptAccessToRecord: true,
          acceptAfterPublishRecord: true,
          reviewComment: initialReviewComment || "",
        }}
        onSubmit={onSubmit}
        validationSchema={schema}
        validateOnChange={false}
        validateOnBlur={false}
      >
        {({ values, handleSubmit }) => {
          return (
            <Modal
              open={isConfirmModalOpen}
              onClose={onClose}
              size="small"
              closeIcon
              closeOnDimmerClick={false}
            >
              <Modal.Content>
                {errors && <ErrorMessage errors={errors} />}
                <Message visible warning>
                  <p>
                    <Icon name="warning sign" />
                    {msgWarningTitle}
                  </p>
                </Message>
                  {!record && (
                      <p>
                        {msgWarningText1}
                      </p>
                  )}
              </Modal.Content>
              <Modal.Actions>
                <Button
                  onClick={onClose}
                  floated="left"
                  loading={loading}
                  disabled={loading}
                >
                  {i18next.t("Cancel")}
                </Button>
                <Button
                  name="submitReview"
                  onClick={(event) => {
                    handleSubmit(event);
                  }}
                  loading={loading}
                  disabled={loading}
                  positive={directPublish}
                  primary={!directPublish}
                  content={submitBtnLbl}
                />
              </Modal.Actions>
            </Modal>
          );
        }}
      </Formik>
    );
  }
}

BMASubmitReviewModal.propTypes = {
  isConfirmModalOpen: PropTypes.bool.isRequired,
  community: PropTypes.object.isRequired,
  onClose: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  initialReviewComment: PropTypes.string,
  publishModalExtraContent: PropTypes.string,
  directPublish: PropTypes.bool,
  errors: PropTypes.node, // TODO FIXME: Use a common error cmp to display errros.
  loading: PropTypes.bool,
  record: PropTypes.object.isRequired,
};

BMASubmitReviewModal.defaultProps = {
  initialReviewComment: "",
  publishModalExtraContent: undefined,
  directPublish: false,
  errors: undefined,
  loading: false,
};