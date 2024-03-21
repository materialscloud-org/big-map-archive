import React, { useEffect, useRef} from "react";
import {
    PreviewButton,
    SaveButton,
} from "@js/invenio_rdm_records";
import { Card, Grid, Icon, Popup } from "semantic-ui-react";
import { BMASubmitReviewOrPublishButton } from "./BMASubmitReviewOrPublishButton";
import { ShareButton } from "@js/invenio_app_rdm/landing_page/ShareOptions/ShareButton";
import { getInputFromDOM } from "@js/invenio_rdm_records/";

const BMACardDepositStatusBox = () => {
    const record = getInputFromDOM("deposits-record");
    const permissions = getInputFromDOM("deposits-record-permissions");
    const id = record["id"];

    // override text in Share button
    const share_button = useRef(null);
    useEffect(() => {
        if (share_button.current) {
            share_button.current.children[0].innerText = "Share links";
        }
    });

    return (
        <>
        {(!id || permissions?.can_update_draft) && (
            <Card>
                <Card.Content>
                    <Grid verticalAlign="middle">
                        <Grid.Row centered className="pt-5 pb-5">
                            <Grid.Column
                                width="16"
                                textAlign="center"
                            >
                                <Popup
                                    trigger={<Icon className="ml-10" name="info circle"/>}
                                    content={
                                    <>
                                    <p>Click "Save draft" to create or update a private record.</p>
                                    <p>Click "Preview" to have a preview of the record before it is shared with the community.</p>
                                    <p>Click "Share with community" to share your record with the members of the selected community.
                                       <i>Only the owner of the record can share the record with the selected community.</i>
                                    </p>
                                    <p>Click "Share links" to manage access links.
                                       <i>This button is only visible to the owner of the record after the draft has been saved and the page reloaded.</i>
                                    </p>
                                    <p>Click "Delete" to delete the draft. <i>If this button is not visible save the record as draft and reload the page.</i></p>
                                    </>
                                    }
                                    position='top center'
                                    wide
                                />
                            </Grid.Column>
                        </Grid.Row>
                    </Grid>
                </Card.Content>
                <Card.Content>
                    <Grid relaxed>
                        <Grid.Column
                            computer={8}
                            mobile={16}
                            className="pb-0 pt-10"
                        >
                            <SaveButton fluid/>
                        </Grid.Column>
                        <Grid.Column
                            computer={8}
                            mobile={16}
                            className="pb-0 pt-10"
                          >
                            <PreviewButton fluid />
                        </Grid.Column>
                        <Grid.Column width={16} className="pt-20">
                            <BMASubmitReviewOrPublishButton fluid/>
                        </Grid.Column>
                        {permissions?.can_manage_record_access &&
                            (<Grid.Column width={16} className="pt-10">
                                <div ref={share_button}>
                                    <ShareButton
                                        disabled={false}
                                        record={record}
                                        permissions={permissions}
                                        fluid
                                    />
                                </div>
                            </Grid.Column>)
                        }
                    </Grid>
                </Card.Content>
            </Card>
        )}
        </>
    );
}

export default BMACardDepositStatusBox;