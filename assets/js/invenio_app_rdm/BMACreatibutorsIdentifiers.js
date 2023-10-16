import React, { Component } from "react";
import PropTypes from "prop-types";
import { SelectField } from "react-invenio-forms";
import _unickBy from "lodash/unionBy";
import { i18next } from "@translations/invenio_rdm_records/i18next";

export class BMACreatibutorsIdentifiers extends Component {
  constructor(props) {
    super(props);
    this.state = {
      selectedOptions: props.initialOptions,
    };
  }

  handleIdentifierAddition = (e, { value }) => {
    this.setState((prevState) => ({
      selectedOptions: _unickBy(
        [
          {
            text: value,
            value: value,
            key: value,
          },
          ...prevState.selectedOptions,
        ],
        "value"
      ),
    }));
  };

  valuesToOptions = (options) =>
    options.map((option) => ({
      text: option,
      value: option,
      key: option,
    }));

  handleChange = ({ data, formikProps }) => {
    const { fieldPath } = this.props;
    this.setState({
      selectedOptions: this.valuesToOptions(data.value),
    });
    formikProps.form.setFieldValue(fieldPath, data.value);
  };

  render() {
    const { fieldPath, label, placeholder } = this.props;
    const { selectedOptions } = this.state;

    return (
      <SelectField
        fieldPath={fieldPath}
        label={label}
        options={selectedOptions}
        placeholder={placeholder}
        noResultsMessage={i18next.t("Type the value of an identifier...")}
        search
        multiple
        selection
        allowAdditions
        onChange={this.handleChange}
        // `icon` is set to `null` in order to hide the dropdown default icon
        icon={null}
        onAddItem={this.handleIdentifierAddition}
        optimized
      />
    );
  }
}

BMACreatibutorsIdentifiers.propTypes = {
  initialOptions: PropTypes.arrayOf(
    PropTypes.shape({
      key: PropTypes.string.isRequired,
      text: PropTypes.string.isRequired,
      value: PropTypes.string.isRequired,
    })
  ).isRequired,
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  placeholder: PropTypes.string,
};

BMACreatibutorsIdentifiers.defaultProps = {
  label: i18next.t("ORCID identifier"),
  placeholder: i18next.t("ORCID"),
};