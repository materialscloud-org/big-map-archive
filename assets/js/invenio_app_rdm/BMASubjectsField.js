import React, {Component} from "react";
import PropTypes from "prop-types";
import {FieldLabel, GroupField, RemoteSelectField} from "react-invenio-forms";
import {Form} from "semantic-ui-react";
import {Field, getIn} from "formik";
import {i18next} from "@translations/invenio_rdm_records/i18next";

export class BMASubjectsField extends Component {
    state = {
        limitTo: "all",
    };

    serializeSubjects = (subjects) =>
        subjects.map((subject) => {
            const scheme = subject.scheme ? `(${subject.scheme}) ` : "";
            return {
                text: scheme + subject.subject,
                value: subject.subject,
                key: subject.subject,
                ...(subject.id ? {id: subject.id} : {}),
                subject: subject.subject,
            };
        });

    prepareSuggest = (searchQuery) => {
        const {limitTo} = this.state;

        const prefix = limitTo === "all" ? "" : `${limitTo}:`;
        return `${prefix}${searchQuery}`;
    };

    render() {
        const {
            fieldPath,
            label,
            labelIcon,
            required,
            multiple,
            placeholder,
            clearable,
            limitToOptions,
        } = this.props;
        return (
            <Field name={fieldPath}>
                {({form: {values}}) => {
                    return (
                        <RemoteSelectField
                            clearable={clearable}
                            fieldPath={fieldPath}
                            initialSuggestions={getIn(values, fieldPath, [])}
                            multiple={multiple}
                            noQueryMessage={i18next.t("Search or create keywords")}
                            placeholder={placeholder}
                            preSearchChange={this.prepareSuggest}
                            required={required}
                            serializeSuggestions={this.serializeSubjects}
                            serializeAddedValue={(value) => ({
                                text: value,
                                value: value,
                                key: value,
                                subject: value,
                            })}
                            suggestionAPIUrl="/api/subjects"
                            onValueChange={({formikProps}, selectedSuggestions) => {
                                formikProps.form.setFieldValue(
                                    fieldPath,
                                    // save the suggestion objects so we can extract information
                                    // about which value added by the user
                                    selectedSuggestions
                                );
                            }}
                            value={getIn(values, fieldPath, []).map((val) => val.subject)}
                            label={<FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label}/>}
                            allowAdditions
                            width={16}
                        />
                    );
                }}
            </Field>
        );
    }
}

BMASubjectsField.propTypes = {
    limitToOptions: PropTypes.array.isRequired,
    fieldPath: PropTypes.string.isRequired,
    label: PropTypes.string,
    labelIcon: PropTypes.string,
    required: PropTypes.bool,
    multiple: PropTypes.bool,
    clearable: PropTypes.bool,
    placeholder: PropTypes.string,
};

BMASubjectsField.defaultProps = {
    required: false,
    label: i18next.t("Keywords"),
    labelIcon: "tag",
    multiple: true,
    clearable: true,
    placeholder: i18next.t("Search or create keywords"),
};