import React from "react";
import {ResultsList} from "react-searchkit";
import {Grid} from "semantic-ui-react";

export function BMADashboardResultViewResultList(props) {
    const {id, sortOptions, paginationOptions, currentResultsState, appName} = props;
    return (
        <Grid.Row>
            <Grid.Column>
                <div style={{"display": "flex", "align-items": "center"}}>
                    <h2 style={{"margin": "0px"}}>My records</h2>
                </div>
                <ResultsList/>
            </Grid.Column>
        </Grid.Row>
    );
}