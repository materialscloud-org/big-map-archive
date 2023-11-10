import React from "react";
import {
  DepositStatusBox,
  SaveButton,
} from "@js/invenio_rdm_records";
import { Card, Grid, } from "semantic-ui-react";
import { BMASubmitReviewOrPublishButton } from "./BMASubmitReviewOrPublishButton";

const BMACardDepositStatusBox = () => {
    return (
        <Card>
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