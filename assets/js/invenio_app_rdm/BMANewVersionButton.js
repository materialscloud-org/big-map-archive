import {Grid, Icon, Message} from "semantic-ui-react";
import {NewVersionButton} from "@js/invenio_rdm_records/src/deposit/controls/NewVersionButton";
import React, {Component} from "react";
import {i18next} from "@translations/invenio_rdm_records/i18next";


export class BMANewVersionButton extends Component {

    render() {
        const isDraftRecord = this.props.isDraftRecord;
        const filesLocked = this.props.lockFileUploader;
        const permissions = this.props.permissions;
        const record = this.props.record;

        return (
            <>
                {isDraftRecord ? (
                    <Grid.Row className="file-upload-note pt-5">
                        <Grid.Column width={16}>
                            <Message visible warning>
                                <p>
                                    <Icon name="warning sign"/>
                                    {i18next.t(
                                        "Once the record is shared, adding and removing files are no longer permitted."
                                    )}
                                </p>
                            </Message>
                        </Grid.Column>
                    </Grid.Row>
                ) : (
                    filesLocked && (
                        <Grid.Row className="file-upload-note pt-5">
                            <Grid.Column width={16}>
                                <Message info>
                                    <NewVersionButton
                                        record={record}
                                        onError={() => {
                                        }}
                                        className="right-floated"
                                        disabled={!permissions.can_new_version}
                                    />
                                    <p className="mt-5 display-inline-block">
                                        <Icon name="info circle" size="large"/>
                                        {i18next.t(
                                            "You must create a new version to add, modify or delete files."
                                        )}
                                    </p>
                                </Message>
                            </Grid.Column>
                        </Grid.Row>
                    )
                )}
            </>
        );
    }
}