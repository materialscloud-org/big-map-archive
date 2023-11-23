import React from "react";
import Overridable, {
} from "react-overridable";
import {
    InvenioSearchApi,
    withState,
    buildUID,
} from "react-searchkit";
import {GridResponsiveSidebarColumn} from "react-invenio-forms";
import {Container, Grid, Button} from "semantic-ui-react";
import {ResultOptions} from "@js/invenio_search_ui/components/Results";
import {SearchBar} from "@js/invenio_search_ui/components/SearchBar";
import {i18next} from "@translations/invenio_search_ui/i18next";
import _isEmpty from "lodash/isEmpty";
import {SearchAppFacets} from "@js/invenio_search_ui/components/SearchAppFacets";
import {SearchAppResultsPane} from "@js/invenio_search_ui/components/SearchAppResultsPane";

const ResultOptionsWithState = withState(ResultOptions);
const appName = "InvenioAppRdm.Search";

export const BMASearchAppLayout = (props) => {
    const {config} = props;

    const [sidebarVisible, setSidebarVisible] = React.useState(false);
    const searchApi = new InvenioSearchApi(config.searchApi);
    const context = {
        appName,
        buildUID: (element) => buildUID(element, "", appName),
        ...config,
    };
    const facetsAvailable = !_isEmpty(config.aggs);

    const resultsPaneLayoutNoFacets = {width: 16};
    const resultsSortLayoutNoFacets = {width: 16};

    const resultsPaneLayoutFacets = {
        mobile: 16,
        tablet: 16,
        computer: 12,
        largeScreen: 13,
        widescreen: 13,
        width: undefined,
    };

    const resultsSortLayoutFacets = {
        mobile: 14,
        tablet: 15,
        computer: 12,
        largeScreen: 13,
        widescreen: 13,
    };

    // make list full width if no facets available
    const resultsPaneLayout = facetsAvailable
        ? resultsPaneLayoutFacets
        : resultsPaneLayoutNoFacets;

    const resultSortLayout = facetsAvailable
        ? resultsSortLayoutFacets
        : resultsSortLayoutNoFacets;

    const columnsAmount = facetsAvailable ? 2 : 1;

    return (
        <Container fluid>
            <Overridable
                id={buildUID("SearchApp.searchbarContainer", "", appName)}
            >
                <Grid relaxed padded>
                    <Grid.Row>
                        <Grid.Column width={12} floated="right">
                            <SearchBar buildUID={buildUID} appName={appName}/>
                        </Grid.Column>
                    </Grid.Row>
                </Grid>
            </Overridable>

            <Grid relaxed>

                <div className="two column row rel-mt-2">
                  <div className="computer only four wide computer three wide large screen three wide widescreen column"></div>
                  <div className="twelve wide computer sixteen wide mobile sixteen wide tablet column">
                    <div className="ui grid">
                      <div className="middle aligned row pb-0">
                        <div className="left eight wide column">
                            <h2>Shared records</h2>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <Grid.Row
                    textAlign="right"
                    columns={columnsAmount}
                    className="result-options rel-mt-2"
                >
                    {facetsAvailable && (
                        <Grid.Column
                            only="mobile tablet"
                            mobile={2}
                            tablet={1}
                            textAlign="center"
                            verticalAlign="middle"
                        >
                            <Button
                                basic
                                icon="sliders"
                                onClick={() => setSidebarVisible(true)}
                                aria-label={i18next.t("Filter results")}
                            />
                        </Grid.Column>
                    )}

                    <Grid.Column {...resultSortLayout} floated="right">
                        <ResultOptionsWithState
                            sortOptions={config.sortOptions}
                            layoutOptions={config.layoutOptions}
                        />
                    </Grid.Column>
                </Grid.Row>

                <Grid.Row columns={columnsAmount}>
                    {facetsAvailable && (
                        <GridResponsiveSidebarColumn
                            ariaLabel={i18next.t("Search filters")}
                            mobile={4}
                            tablet={4}
                            computer={4}
                            largeScreen={3}
                            widescreen={3}
                            open={sidebarVisible}
                            onHideClick={() => setSidebarVisible(false)}
                        >
                            <SearchAppFacets aggs={config.aggs} appName={appName} buildUID={buildUID}/>
                        </GridResponsiveSidebarColumn>
                    )}

                    <Grid.Column
                        as="section"
                        aria-label={i18next.t("Search results")}
                        {...resultsPaneLayout}
                    >
                        <SearchAppResultsPane
                            layoutOptions={config.layoutOptions} appName={appName} buildUID={buildUID}
                        />
                    </Grid.Column>
                </Grid.Row>
            </Grid>
        </Container>
    );
}