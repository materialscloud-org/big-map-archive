import { i18next } from "@translations/invenio_app_rdm/i18next";
import React from "react";
import PropTypes from "prop-types";
import _truncate from "lodash/truncate";
import _get from "lodash/get";
import { Button, Icon, Item, Label } from "semantic-ui-react";
import { SearchItemCreators } from "@js/invenio_app_rdm/utils";
import { CompactStats } from "@js/invenio_app_rdm/components/CompactStats";
import { BMADisplayPartOfCommunities } from "./BMADisplayPartOfCommunities";

export const BMAComputerTabletUploadsItem = ({
  result,
  editRecord,
  statuses,
  access,
  uiMetadata,
}) => {
  const { accessStatusId, accessStatus, accessStatusIcon } = access;
  const {
    descriptionStripped,
    title,
    creators,
    subjects,
    publicationDate,
    resourceType,
    createdDate,
    version,
    isPublished,
    viewLink,
    publishingInformation,
  } = uiMetadata;

  const icon = isPublished ? (
    <Icon name="check" className="positive" />
  ) : (
    <Icon name="upload" className="negative" />
  );
  const uniqueViews = _get(result, "stats.all_versions.unique_views", 0);
  const uniqueDownloads = _get(result, "stats.all_versions.unique_downloads", 0);

  return (
    <Item key={result.id} className="deposits-list-item computer tablet only flex">
      <div className="status-icon mr-10">
        <Item.Content verticalAlign="top">
          <Item.Extra>{icon}</Item.Extra>
        </Item.Content>
      </div>
      <Item.Content>
        <Item.Extra className="labels-actions">
          {result.status in statuses && result.status !== "published" && (
            <Label horizontal size="tiny" className={statuses[result.status].color}>
              {statuses[result.status].title}
            </Label>
          )}
          <Label horizontal size="tiny" color="green">
            {version}
          </Label>
          {isPublished && (
            <Label horizontal size="tiny" color="blue">
              {publicationDate}
            </Label>
          )}
          <Button
            compact
            size="small"
            floated="right"
            onClick={() => editRecord()}
            labelPosition="left"
            icon="edit"
            content={i18next.t("Edit")}
          />
          {isPublished && (
            <Button
              compact
              size="small"
              floated="right"
              href={viewLink}
              labelPosition="left"
              icon="eye"
              content={i18next.t("View")}
            />
          )}
        </Item.Extra>
        <Item.Header as="h2">
          <a href={viewLink} className="truncate-lines-2">
            {title}
          </a>
        </Item.Header>
        <Item.Meta>
          <div className="creatibutors">
            <SearchItemCreators creators={creators} />
          </div>
        </Item.Meta>
        <Item.Description>
          {_truncate(descriptionStripped, {
            length: 350,
          })}
        </Item.Description>
        <Item.Extra>
          {subjects.map((subject) => (
            <Label key={subject.title_l10n} size="tiny">
              {subject.title_l10n}
            </Label>
          ))}

          <div className="flex justify-space-between align-items-end">
            <small>
              <BMADisplayPartOfCommunities communities={result.parent?.communities} />
            </small>
            <small>
              <CompactStats
                uniqueViews={uniqueViews}
                uniqueDownloads={uniqueDownloads}
              />
            </small>
          </div>
        </Item.Extra>
      </Item.Content>
    </Item>
  );
};

BMAComputerTabletUploadsItem.propTypes = {
  result: PropTypes.object.isRequired,
  editRecord: PropTypes.func.isRequired,
  statuses: PropTypes.object.isRequired,
  access: PropTypes.object.isRequired,
  uiMetadata: PropTypes.object.isRequired,
};