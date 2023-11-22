import {i18next} from "@translations/invenio_app_rdm/i18next";
import _truncate from "lodash/truncate";
import React from "react";
import {SearchItemCreators} from "@js/invenio_app_rdm/utils";
import {Item, Label, Icon} from "semantic-ui-react";
import {CompactStats} from "@js/invenio_app_rdm/components/CompactStats";
import _get from "lodash/get";

export const BMARecordsResultsListItemLayout = (props) => {
    const {
        result,
        key,
        accessStatusId,
        accessStatus,
        accessStatusIcon,
        createdDate,
        creators,
        descriptionStripped,
        publicationDate,
        resourceType,
        subjects,
        title,
        version,
        versions,
        allVersionsVisible,
        numOtherVersions,
    } = props;

    const uniqueViews = _get(result, "stats.all_versions.unique_views", 0);
    const uniqueDownloads = _get(result, "stats.all_versions.unique_downloads", 0);
    const publishingInformation = _get(result, "ui.publishing_information.journal", "");
    const viewLink = `/records/${result.id}`;

    return (
        <>
            <Item key={key ?? result.id}>
                <Item.Content>
                    <Item.Extra className="labels-actions">
                        <Label horizontal size="tiny" color="green">
                            {publicationDate}
                        </Label>
                        <Label horizontal size="tiny" className="primary">
                            {version}
                        </Label>
                    </Item.Extra>
                    <Item.Header as="h2">
                        <a href={viewLink}>{title}</a>
                    </Item.Header>
                    <Item className="creatibutors">
                        <SearchItemCreators creators={creators}/>
                    </Item>
                    <Item.Description>
                        {_truncate(descriptionStripped, {length: 350})}
                    </Item.Description>
                    <Item.Extra>
                        <div className="flex justify-content-end">
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
        </>
    );
}