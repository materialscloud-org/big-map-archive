// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C)      2021 Graz University of Technology.
// Copyright (C)      2022 TU Wien.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import {Header, Grid, Label, List} from "semantic-ui-react";
import {humanReadableBytes, FieldLabel} from "react-invenio-forms";
import {i18next} from "@translations/invenio_rdm_records/i18next";
import Overridable from "react-overridable";


export const BMAFileUploaderToolbar = (props) => {
    const {
        filesList,
        filesSize,
        filesEnabled,
        quota,
        decimalSizeDisplay,
    } = props;

    return (
        <>
            <Grid.Column
                verticalAlign="middle"
                floated="left"
                mobile={16}
                tablet={6}
                computer={6}
            >
                <div className="required field title-field files">
                    <FieldLabel className="field-label-class invenio-field-label files" htmlFor="" icon="file" label="Files"/>
                </div>
            </Grid.Column>
            <Overridable
                id="ReactInvenioDeposit.FileUploaderToolbar.FileList.container"
                filesList={filesList}
                filesSize={filesSize}
                filesEnabled={filesEnabled}
                quota={quota}
                decimalSizeDisplay={decimalSizeDisplay}
            >
                {filesEnabled && (
                    <Grid.Column mobile={16} tablet={10} computer={10} className="storage-col">
                        <Header size="tiny" className="mr-10">
                            {i18next.t("Storage available")}
                        </Header>
                        <List horizontal floated="right">
                            <List.Item>
                                <Label
                                    {...(filesList.length === quota.maxFiles ? {color: "blue"} : {})}
                                >
                                    {i18next.t(`{{length}} out of {{maxfiles}} files`, {
                                        length: filesList.length,
                                        maxfiles: quota.maxFiles,
                                    })}
                                </Label>
                            </List.Item>
                            <List.Item>
                                <Label
                                    {...(humanReadableBytes(filesSize, decimalSizeDisplay) ===
                                    humanReadableBytes(quota.maxStorage, decimalSizeDisplay)
                                        ? {color: "blue"}
                                        : {})}
                                >
                                    {humanReadableBytes(filesSize, decimalSizeDisplay)}{" "}
                                    {i18next.t("out of")}{" "}
                                    {humanReadableBytes(quota.maxStorage, decimalSizeDisplay)}
                                </Label>
                            </List.Item>
                        </List>
                    </Grid.Column>
                )}
            </Overridable>
        </>
    );
};