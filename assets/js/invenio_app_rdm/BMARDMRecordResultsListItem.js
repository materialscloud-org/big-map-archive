import { i18next } from "@translations/invenio_app_rdm/i18next";
import _get from "lodash/get";
import React from "react";
import { http } from "react-invenio-forms";
import { BMAComputerTabletUploadsItem } from "./BMAComputerTabletUploadsItem";
import { MobileUploadsItem } from "@js/invenio_app_rdm/user_dashboard/uploads_items/MobileUploadsItem";
import PropTypes from "prop-types";

const statuses = {
  in_review: { color: "warning", title: i18next.t("In review") },
  declined: { color: "negative", title: i18next.t("Declined") },
  expired: { color: "expired", title: i18next.t("Expired") },
  draft_with_review: { color: "red", title: i18next.t("Private") },
  draft: { color: "red", title: i18next.t("Private") },
  new_version_draft: { color: "red", title: i18next.t("Private") },
  published: { color: "green", title: i18next.t("Community shared") },
};

export const BMARDMRecordResultsListItem = ({ result }) => {
  const editRecord = () => {
    http
      .post(`/api/records/${result.id}/draft`)
      .then(() => {
        window.location = `/uploads/${result.id}`;
      })
      .catch((error) => {
        console.error(error.response.data);
      });
  };

  const isPublished = result.is_published;
  const access = {
    accessStatusId: _get(result, "ui.access_status.id", i18next.t("open")),
    accessStatus: _get(result, "ui.access_status.title_l10n", i18next.t("Open")),
    accessStatusIcon: _get(result, "ui.access_status.icon", i18next.t("unlock")),
  };
  const uiMetadata = {
    descriptionStripped: _get(
      result,
      "ui.description_stripped",
      i18next.t("No description")
    ),
    title: _get(result, "metadata.title", i18next.t("No title")),
    creators: _get(result, "ui.creators.creators", []).slice(0, 3),
    subjects: _get(result, "ui.subjects", []),
    publicationDate: _get(
      result,
      "ui.publication_date_l10n_long",
      i18next.t("No publication date found.")
    ),
    resourceType: _get(
      result,
      "ui.resource_type.title_l10n",
      i18next.t("No resource type")
    ),
    createdDate: result.ui?.created_date_l10n_long,
    version: result.ui?.version ?? "",
    isPublished: isPublished,
    viewLink: isPublished ? `/records/${result.id}` : `/uploads/${result.id}`,
    publishingInformation: _get(result, "ui.publishing_information.journal", ""),
  };

  return (
    <>
      <BMAComputerTabletUploadsItem
        result={result}
        editRecord={editRecord}
        statuses={statuses}
        access={access}
        uiMetadata={uiMetadata}
      />
      <MobileUploadsItem
        result={result}
        editRecord={editRecord}
        statuses={statuses}
        access={access}
        uiMetadata={uiMetadata}
      />
    </>
  );
};

BMARDMRecordResultsListItem.propTypes = {
  result: PropTypes.object.isRequired,
};