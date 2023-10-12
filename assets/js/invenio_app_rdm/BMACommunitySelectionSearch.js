import React, { Component } from "react";
import { OverridableContext, parametrize } from "react-overridable";
import {
  EmptyResults,
  Error,
  InvenioSearchApi,
  Pagination,
  ReactSearchKit,
  ResultsList,
  ResultsLoader,
} from "react-searchkit";
import { Modal } from "semantic-ui-react";
import { BMACommunityListItem } from "./BMACommunityListItem";
import PropTypes from "prop-types";

export class BMACommunitySelectionSearch extends Component {
  constructor(props) {
    super(props);
    const {
      apiConfigs: { allCommunities },
    } = this.props;

    const defaultConfig = allCommunities;

    this.state = {
      selectedConfig: defaultConfig,
    };
  }

  render() {
    const {
      selectedConfig: {
        searchApi: selectedsearchApi,
        appId: selectedAppId,
        initialQueryState: selectedInitialQueryState,
        toggleText,
      },
    } = this.state;
    const {
      apiConfigs: { allCommunities, myCommunities },
      record,
    } = this.props;
    const searchApi = new InvenioSearchApi(selectedsearchApi);
    const overriddenComponents = {
      [`${selectedAppId}.ResultsList.item`]: parametrize(BMACommunityListItem, {
        record: record,
      }),
    };
    return (
      <OverridableContext.Provider value={overriddenComponents}>
        <ReactSearchKit
          appName={selectedAppId}
          urlHandlerApi={{ enabled: false }}
          searchApi={searchApi}
          key={selectedAppId}
          initialQueryState={selectedInitialQueryState}
        >
          <>
            <Modal.Content
              role="tabpanel"
              id={selectedAppId}
              scrolling
              className="community-list-results"
            >
              <ResultsLoader>
                <EmptyResults />
                <Error />
                <ResultsList />
              </ResultsLoader>
            </Modal.Content>

            <Modal.Content className="text-align-center">
              <Pagination />
            </Modal.Content>
          </>
        </ReactSearchKit>
      </OverridableContext.Provider>
    );
  }
}

BMACommunitySelectionSearch.propTypes = {
  apiConfigs: PropTypes.shape({
    allCommunities: PropTypes.shape({
      appId: PropTypes.string.isRequired,
      initialQueryState: PropTypes.object.isRequired,
      searchApi: PropTypes.object.isRequired,
    }),
    myCommunities: PropTypes.shape({
      appId: PropTypes.string.isRequired,
      initialQueryState: PropTypes.object.isRequired,
      searchApi: PropTypes.object.isRequired,
    }),
  }),
  record: PropTypes.object.isRequired,
};

BMACommunitySelectionSearch.defaultProps = {
  apiConfigs: {
    allCommunities: {
      initialQueryState: { size: 5, page: 1 },
      searchApi: {
        axios: {
          url: "/api/communities",
          headers: { Accept: "application/vnd.inveniordm.v1+json" },
        },
      },
      appId: "ReactInvenioDeposit.CommunitySelectionSearch.AllCommunities",
      toggleText: "Search in all communities",
    },
    myCommunities: {
      initialQueryState: { size: 5, page: 1 },
      searchApi: {
        axios: {
          url: "/api/user/communities",
          headers: { Accept: "application/vnd.inveniordm.v1+json" },
        },
      },
      appId: "ReactInvenioDeposit.CommunitySelectionSearch.MyCommunities",
      toggleText: "Search in my communities",
    },
  },
};