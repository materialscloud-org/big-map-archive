// This file is part of BIG-MAP Archive
// Copyright (C) 2024 BIG-MAP Archive Team.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.
import { i18next } from "@translations/invenio_app_rdm/i18next";
import React from "react";
import _isEmpty from "lodash/isEmpty";
import PropTypes from "prop-types";
import { Table, Loader } from "semantic-ui-react";
import { CreateAccessLink } from "@js/invenio_app_rdm/landing_page/ShareOptions/AccessLinks/CreateAccessLink";
import { BMALinksSearchItem } from "./BMALinksSearchItem";
import { LinksSearchResultContainer } from "@js/invenio_app_rdm/landing_page/ShareOptions/AccessLinks/LinksSearchResultContainer";

export class BMALinksSearchResultContainer extends LinksSearchResultContainer {
  render() {
    const { results, record, fetchData } = this.props;
    const { loading, error } = this.state;
    return (
      <>
        {error && this.errorMessage()}

        <Table className="fixed-header">
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell data-label="Link title" width={3}>
                {i18next.t("Link title")}
              </Table.HeaderCell>
              <Table.HeaderCell data-label="Created" width={3}>
                {i18next.t("Created")}
              </Table.HeaderCell>
              <Table.HeaderCell data-label="Expires at" width={3}>
                {i18next.t("Expires")}
              </Table.HeaderCell>
              <Table.HeaderCell data-label="Access" width={3}>
                {i18next.t("Access")}
              </Table.HeaderCell>
              <Table.HeaderCell width={4} />
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {loading ? (
              <Loader />
            ) : !_isEmpty(results) ? (
              results.map((result) => (
                <BMALinksSearchItem
                  key={result.id}
                  result={result}
                  record={record}
                  fetchData={fetchData}
                />
              ))
            ) : (
              <Table.Row textAlign="center">
                <td className="mt-10">
                  <i>
                    <h5>{i18next.t("This record has no links generated yet.")}</h5>
                  </i>
                </td>
              </Table.Row>
            )}
          </Table.Body>
        </Table>

        <Table color="green">
          <CreateAccessLink handleCreation={this.handleCreation} loading={loading} />
        </Table>
      </>
    );
  }
}

BMALinksSearchResultContainer.propTypes = {
  // results: PropTypes.array.isRequired,
  record: PropTypes.object.isRequired,
  fetchData: PropTypes.func.isRequired,
};