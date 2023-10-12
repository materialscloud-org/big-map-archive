import { i18next } from "@translations/invenio_rdm_records/i18next";
import _capitalize from "lodash/capitalize";
import PropTypes from "prop-types";
import React, { useContext } from "react";
import { Button, Icon, Label } from "semantic-ui-react";
import { BMACommunityCompactItem } from "./BMACommunityCompactItem";
import { CommunityContext } from "@js/invenio_rdm_records/src/deposit/components/CommunitySelectionModal/CommunityContext";
import { InvenioPopup } from "react-invenio-forms";

export const BMACommunityListItem = ({ result, record }) => {
  const {
    setLocalCommunity,
    getChosenCommunity,
    userCommunitiesMemberships,
    displaySelected,
  } = useContext(CommunityContext);

  const { metadata } = result;
  const itemSelected = getChosenCommunity()?.id === result.id;
  const userMembership = userCommunitiesMemberships[result["id"]];
  const invalidPermissionLevel =
    record.access.record === "public" && result.access.visibility === "restricted";

  const actions = (
    <>
      <Button
        content={
          displaySelected && itemSelected ? i18next.t("Selected") : i18next.t("Select")
        }
        size="tiny"
        positive={displaySelected && itemSelected}
        onClick={() => setLocalCommunity(result)}
        disabled={invalidPermissionLevel}
        aria-label={i18next.t("Select {{title}}", { title: metadata.title })}
      />
    </>
  );

  const extraLabels = null;

  return (
    <BMACommunityCompactItem
      result={result}
      actions={actions}
      extraLabels={extraLabels}
      showPermissionLabel
    />
  );
};

BMACommunityListItem.propTypes = {
  result: PropTypes.object.isRequired,
  record: PropTypes.object.isRequired,
};