import React, { Component } from "react";
import PropTypes from "prop-types";

import {
  TextField,
  GroupField,
  ArrayField,
  FieldLabel,
  SelectField,
} from "react-invenio-forms";
import { Button, Form, Icon } from "semantic-ui-react";

import { BMAEmptyRelatedWork } from "./BMAEmptyRelatedWork";
import { i18next } from "@translations/invenio_rdm_records/i18next";

export class BMARelatedWorksField extends Component {
  render() {
    const { fieldPath, label, labelIcon, required, options, showEmptyValue } =
      this.props;

    return (
      <>
        <ArrayField
          addButtonLabel={i18next.t("Add reference")}
          defaultNewValue={BMAEmptyRelatedWork}
          fieldPath={fieldPath}
          label={<FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />}
          required={required}
          showEmptyValue={showEmptyValue}
        >
          {({ arrayHelpers, indexPath }) => {
            const fieldPathPrefix = `${fieldPath}.${indexPath}`;

            return (
              <GroupField optimized>
                <SelectField
                  clearable
                  fieldPath={`${fieldPathPrefix}.scheme`}
                  label={i18next.t("Scheme")}
                  aria-label={i18next.t("Scheme")}
                  optimized
                  options={options.scheme}
                  required
                  width={2}
                />

                <TextField
                  fieldPath={`${fieldPathPrefix}.identifier`}
                  label={i18next.t("Identifier")}
                  required
                  width={4}
                />

                <Form.Field>
                  <Button
                    aria-label={i18next.t("Remove field")}
                    className="close-btn"
                    icon
                    onClick={() => arrayHelpers.remove(indexPath)}
                  >
                    <Icon name="close" />
                  </Button>
                </Form.Field>
              </GroupField>
            );
          }}
        </ArrayField>
      </>
    );
  }
}

BMARelatedWorksField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  labelIcon: PropTypes.string,
  required: PropTypes.bool,
  options: PropTypes.object.isRequired,
  showEmptyValue: PropTypes.bool,
};

BMARelatedWorksField.defaultProps = {
  label: i18next.t("References"),
  labelIcon: "barcode",
  required: undefined,
  showEmptyValue: false,
};