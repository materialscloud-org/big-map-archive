import { i18next } from "@translations/invenio_app_rdm/i18next";
import { CommunityTypeLabel } from "@js/invenio_communities/community/labels";
import { RestrictedLabel } from "@js/invenio_communities/community/labels";
import _truncate from "lodash/truncate";
import React from "react";
import { Image, InvenioPopup } from "react-invenio-forms";
import { Icon } from "semantic-ui-react";
import PropTypes from "prop-types";

export const BMACommunityCompactItemMobile = ({
  result,
  actions,
  extraLabels,
  itemClassName,
  showPermissionLabel,
  detailUrl,
}) => {
  const communityType = result.ui?.type?.title_l10n;
  const { metadata, ui, links, access, id } = result;
  return (
    <div key={id} className={`community-item mobile only ${itemClassName}`}>
      <div className="display-grid auto-column-grid no-wrap">
        <div className="flex align-items-center">
          <Image
            wrapped
            size="mini"
            src={links.logo}
            alt=""
            className="community-image rel-mr-1"
          />

          <div className="flex align-items-center rel-mb-1">
            <p
              className="ui small header truncate-lines-2 m-0 mr-5"
            >
              {metadata.title}
            </p>
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
    </div>
  );
};

BMACommunityCompactItemMobile.propTypes = {
  result: PropTypes.object.isRequired,
  extraLabels: PropTypes.node,
  itemClassName: PropTypes.string,
  showPermissionLabel: PropTypes.bool,
  actions: PropTypes.node,
  detailUrl: PropTypes.string,
};

BMACommunityCompactItemMobile.defaultProps = {
  actions: undefined,
  extraLabels: undefined,
  itemClassName: "",
  showPermissionLabel: false,
  detailUrl: undefined,
};