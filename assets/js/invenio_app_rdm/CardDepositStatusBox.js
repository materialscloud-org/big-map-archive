import React from "react";
import {
  DepositStatusBox,
  PreviewButton,
  SaveButton,
} from "@js/invenio_rdm_records";
import { Card, Grid, } from "semantic-ui-react";
import {BMASubmitReviewOrPublishButton} from "./BMASubmitReviewOrPublishButton";

const CardDepositStatusBox = () => {
    return (
        <Card>
            <Card.Content>
                <DepositStatusBox/>
            </Card.Content>
            <Card.Content>
                <Grid relaxed>
                    <Grid.Column
                        computer={8}
                        mobile={16}
                        className="pb-0 left-btn-col"
                    >
                        <SaveButton fluid/>
                    </Grid.Column>

                    <Grid.Column
                        computer={8}
                        mobile={16}
                        className="pb-0 right-btn-col"
                    >
                        <PreviewButton fluid/>
                    </Grid.Column>

                    <Grid.Column width={16} className="pt-10">
                        <BMASubmitReviewOrPublishButton fluid/>
                    </Grid.Column>
                </Grid>
            </Card.Content>
        </Card>);
}

export default CardDepositStatusBox;