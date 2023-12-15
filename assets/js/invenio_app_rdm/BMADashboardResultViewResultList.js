import React from "react";
import {ResultsList} from "react-searchkit";
import {Grid, Popup, Icon} from "semantic-ui-react";

export function BMADashboardResultViewResultList(props) {
    const {id, sortOptions, paginationOptions, currentResultsState, appName} = props;
    return (
        <Grid.Row>
            <Grid.Column>
                <div style={{"display": "flex", "align-items": "center"}}>
                    <h2 style={{"margin": "0px"}}>My records</h2>
                    <Popup
                        trigger={<Icon className="ml-5" name="info circle"/>}
                        content={"Use the closest search box to filter through your records. The search guide provides examples of advanced search queries."}
                    />
                </div>
                <ResultsList/>
            </Grid.Column>
        </Grid.Row>
    );
}