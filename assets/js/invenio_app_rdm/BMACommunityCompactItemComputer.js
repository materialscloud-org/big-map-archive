import { i18next } from "@translations/invenio_app_rdm/i18next";
import React from "react";
import PropTypes from "prop-types";
import _truncate from "lodash/truncate";

import { Image, InvenioPopup } from "react-invenio-forms";
import { Icon } from "semantic-ui-react";
import { CommunityTypeLabel, RestrictedLabel } from "@js/invenio_communities/community/labels";

export const BMACommunityCompactItemComputer = ({
  result,
  actions,
  extraLabels,
  itemClassName,
  showPermissionLabel,
  detailUrl,
}) => {
  const { metadata, ui, links, access, id } = result;
  const communityType = ui?.type?.title_l10n;
  return (
    <div
      key={id}
      className={`community-item tablet computer only display-grid auto-column-grid no-wrap ${itemClassName}`}
    >
      <div className="flex align-items-center">
        <Image
          wrapped
          size="tiny"
          src={links.logo}
          alt=""
          className="community-image rel-mr-2"
        />

        <div>
          <div className="flex align-items-center rel-mb-1">
            <p
              className="ui small header truncate-lines-2 m-0 mr-5"
            >
              {metadata.title}
            </p>
          </div>
        </div>
      </div>

      <div className="flex align-items-center justify-end">
        {showPermissionLabel && (
          <span className="rel-mr-1">
          </span>
        )}
        {actions}
      </div>
    </div>
  );
};

BMACommunityCompactItemComputer.propTypes = {
  result: PropTypes.object.isRequired,
  actions: PropTypes.node,
  extraLabels: PropTypes.node,
  itemClassName: PropTypes.string,
  showPermissionLabel: PropTypes.bool,
  detailUrl: PropTypes.string,
};

BMACommunityCompactItemComputer.defaultProps = {
  actions: undefined,
  extraLabels: undefined,
  itemClassName: "",
  showPermissionLabel: false,
  detailUrl: undefined,
};