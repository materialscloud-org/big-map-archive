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

import { emptyRelatedWork } from "@js/invenio_rdm_records/src/deposit/fields/RelatedWorksField/initialValues";
import { ResourceTypeField } from "@js/invenio_rdm_records/src/deposit/fields/ResourceTypeField";
import { i18next } from "@translations/invenio_rdm_records/i18next";

export class BMARelatedWorksField extends Component {
  render() {
    const { fieldPath, label, labelIcon, required, options, showEmptyValue } =
      this.props;
    
    return (
      <>
        <ArrayField
          addButtonLabel={i18next.t("Add reference")}
          defaultNewValue={emptyRelatedWork}
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
                  fieldPath={`${fieldPathPrefix}.relation_type`}
                  label={i18next.t("Relation")}
                  aria-label={i18next.t("Relation")}
                  optimized
                  options={options.relations}
                  placeholder={{
                    role: "option",
                    content: "Select relation...",
                  }}
                  required
                  width={3}
                />

                <TextField
                  fieldPath={`${fieldPathPrefix}.identifier`}
                  label={i18next.t("Identifier")}
                  required
                  width={4}
                />

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

                <ResourceTypeField
                  clearable
                  fieldPath={`${fieldPathPrefix}.resource_type`}
                  labelIcon="" // Otherwise breaks alignment
                  options={options.resource_type}
                  width={7}
                  labelclassname="small field-label-class"
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