import React from "react";
import PropTypes from "prop-types";

import { Image, InvenioPopup } from "react-invenio-forms";

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
          <div className="flex align-items-center">
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