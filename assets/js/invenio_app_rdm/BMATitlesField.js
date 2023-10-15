import React, { Component } from "react";
import PropTypes from "prop-types";

import { FieldLabel, TextField } from "react-invenio-forms";
import { i18next } from "@translations/invenio_rdm_records/i18next";

export class BMATitlesField extends Component {
  render() {
    const { fieldPath, options, label, required, recordUI } = this.props;

    return (
      <>
        <TextField
          fieldPath={fieldPath}
          label={<FieldLabel htmlFor={fieldPath} icon="book" label={label} />}
          required={required}
          className="title-field"
          optimized
        />
      </>
    );
  }
}

BMATitlesField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  options: PropTypes.shape({
    type: PropTypes.arrayOf(
      PropTypes.shape({
        icon: PropTypes.string,
        text: PropTypes.string,
        value: PropTypes.string,
      })
    ),
    lang: PropTypes.arrayOf(
      PropTypes.shape({
        text: PropTypes.string,
        value: PropTypes.string,
      })
    ),
  }).isRequired,
  required: PropTypes.bool,
  recordUI: PropTypes.object,
};

BMATitlesField.defaultProps = {
  label: i18next.t("Title"),
  required: false,
  recordUI: undefined,
};