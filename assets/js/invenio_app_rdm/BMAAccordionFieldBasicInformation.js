import {i18next} from "@translations/invenio_app_rdm/i18next";
import _get from "lodash/get";
import React, {Fragment} from "react";
import {AccordionField} from "react-invenio-forms";
import {
    DescriptionsField,
    CreatibutorsField,
    PIDField,
    LicenseField,
    PublicationDateField,
    ResourceTypeField,
    TitlesField,
} from "@js/invenio_rdm_records";
import Overridable from "react-overridable";

const BMAAccordionFieldBasicInformation = (props) => {
    const { record, config, vocabularies } = props;

    return (
        <AccordionField
            includesPaths={[
                "metadata.resource_type",
                "metadata.title",
                "metadata.additional_titles",
                "metadata.publication_date",
                "metadata.creators",
                "metadata.description",
                "metadata.additional_descriptions",
                "metadata.rights",
            ]}
            active
            label={i18next.t("Metadata")}
        >
            <Overridable
                id="InvenioAppRdm.Deposit.PIDField.container"
                config={config}
                record={record}
            >
                <Fragment>
                    {config.pids.map((pid) => (
                        <Fragment key={pid.scheme}>
                            <PIDField
                                btnLabelDiscardPID={pid.btn_label_discard_pid}
                                btnLabelGetPID={pid.btn_label_get_pid}
                                canBeManaged={pid.can_be_managed}
                                canBeUnmanaged={pid.can_be_unmanaged}
                                fieldPath={`pids.${pid.scheme}`}
                                fieldLabel={pid.field_label}
                                isEditingPublishedRecord={
                                    record.is_published === true // is_published is `null` at first upload
                                }
                                managedHelpText={pid.managed_help_text}
                                pidLabel={pid.pid_label}
                                pidPlaceholder={pid.pid_placeholder}
                                pidType={pid.scheme}
                                unmanagedHelpText={pid.unmanaged_help_text}
                                required
                            />
                        </Fragment>
                    ))}
                </Fragment>
            </Overridable>

            <Overridable
                id="InvenioAppRdm.Deposit.ResourceTypeField.container"
                vocabularies={vocabularies}
                fieldPath="metadata.resource_type"
            >
                <ResourceTypeField
                    options={vocabularies.metadata.resource_type}
                    fieldPath="metadata.resource_type"
                    required
                />
            </Overridable>

            <Overridable
                id="InvenioAppRdm.Deposit.TitlesField.container"
                vocabularies={vocabularies}
                fieldPath="metadata.title"
                record={record}
            >
                <TitlesField
                    options={vocabularies.metadata.titles}
                    fieldPath="metadata.title"
                    recordUI={record.ui}
                    required
                />
            </Overridable>

            <Overridable
                id="InvenioAppRdm.Deposit.PublicationDateField.container"
                fieldPath="metadata.publication_date"
            >
                <PublicationDateField
                    required
                    fieldPath="metadata.publication_date"
                />
            </Overridable>

            <Overridable
                id="InvenioAppRdm.Deposit.CreatorsField.container"
                vocabularies={vocabularies}
                config={config}
                fieldPath="metadata.creators"
            >
                <CreatibutorsField
                    label={i18next.t("Creators")}
                    labelIcon="user"
                    fieldPath="metadata.creators"
                    roleOptions={vocabularies.metadata.creators.role}
                    schema="creators"
                    autocompleteNames={config.autocomplete_names}
                    required
                />
            </Overridable>

            <Overridable
                id="InvenioAppRdm.Deposit.DescriptionsField.container"
                record={record}
                vocabularies={vocabularies}
                fieldPath="metadata.description"
            >
                <DescriptionsField
                    fieldPath="metadata.description"
                    options={vocabularies.metadata.descriptions}
                    recordUI={_get(record, "ui", null)}
                    editorConfig={{
                        removePlugins: [
                            "Image",
                            "ImageCaption",
                            "ImageStyle",
                            "ImageToolbar",
                            "ImageUpload",
                            "MediaEmbed",
                            "Table",
                            "TableToolbar",
                            "TableProperties",
                            "TableCellProperties",
                        ],
                    }}
                />
            </Overridable>

            <Overridable
                id="InvenioAppRdm.Deposit.LicenseField.container"
                fieldPath="metadata.rights"
            >
                <LicenseField
                    fieldPath="metadata.rights"
                    searchConfig={{
                        searchApi: {
                            axios: {
                                headers: {
                                    Accept: "application/vnd.inveniordm.v1+json",
                                },
                                url: "/api/vocabularies/licenses",
                                withCredentials: false,
                            },
                        },
                        initialQueryState: {
                            filters: [["tags", "recommended"]],
                        },
                    }}
                    serializeLicenses={(result) => ({
                        title: result.title_l10n,
                        description: result.description_l10n,
                        id: result.id,
                        link: result.props.url,
                    })}
                />
            </Overridable>
        </AccordionField>);
};

export default BMAAccordionFieldBasicInformation;

