import React from "react";
import {
    DepositStatusBox,
    SaveButton,
} from "@js/invenio_rdm_records";
import {Card, Grid, Icon, Popup} from "semantic-ui-react";
import {BMASubmitReviewOrPublishButton} from "./BMASubmitReviewOrPublishButton";

const BMACardDepositStatusBox = () => {
    return (
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
                                content='Click "Save draft" to create or update a private record. Click "Share with community" to privately share your record with the selected community.'
                            />
                        </Grid.Column>
                    </Grid.Row>
                </Grid>
            </Card.Content>
            <Card.Content>
                <Grid relaxed>
                    <Grid.Column
                        computer={16}
                        mobile={16}
                        className="pb-0 pt-10"
                    >
                        <SaveButton fluid/>
                    </Grid.Column>
                    <Grid.Column width={16} className="pt-10">
                        <BMASubmitReviewOrPublishButton fluid/>
                    </Grid.Column>
                </Grid>
            </Card.Content>
        </Card>);
}

export default BMACardDepositStatusBox;