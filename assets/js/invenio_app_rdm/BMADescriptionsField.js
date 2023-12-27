import React, { Component } from "react";
import PropTypes from "prop-types";
import { FieldLabel, RichInputField } from "react-invenio-forms";
import { i18next } from "@translations/invenio_rdm_records/i18next";

export class BMADescriptionsField extends Component {
  render() {
    const { fieldPath, label, labelIcon, options, editorConfig, recordUI, required } = this.props;
    return (
      <>
        <RichInputField
          className="description-field rel-mb-1"
          fieldPath={fieldPath}
          editorConfig={editorConfig}
          label={<FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />}
          optimized
          required={required}
        />
      </>
    );
  }
}

BMADescriptionsField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  labelIcon: PropTypes.string,
  editorConfig: PropTypes.object,
  recordUI: PropTypes.object,
  options: PropTypes.object.isRequired,
};

BMADescriptionsField.defaultProps = {
  label: i18next.t("Description"),
  labelIcon: "pencil",
  editorConfig: undefined,
  recordUI: undefined,
};
