import React from "react";
import PropTypes from "prop-types";

import { BMACommunityCompactItemComputer } from "./BMACommunityCompactItemComputer";
import { BMACommunityCompactItemMobile } from "./BMACommunityCompactItemMobile";

export function BMACommunityCompactItem({
  result,
  actions,
  extraLabels,
  itemClassName,
  showPermissionLabel,
  detailUrl,
}) {
  return (
    <>
      <BMACommunityCompactItemComputer
        result={result}
        actions={actions}
        extraLabels={extraLabels}
        itemClassName={itemClassName}
        showPermissionLabel={showPermissionLabel}
        detailUrl={detailUrl}
      />
      <BMACommunityCompactItemMobile
        result={result}
        actions={actions}
        extraLabels={extraLabels}
        itemClassName={itemClassName}
        showPermissionLabel={showPermissionLabel}
        detailUrl={detailUrl}
      />
    </>
  );
}

BMACommunityCompactItem.propTypes = {
  result: PropTypes.object.isRequired,
  actions: PropTypes.node,
  extraLabels: PropTypes.node,
  itemClassName: PropTypes.string,
  showPermissionLabel: PropTypes.bool,
  detailUrl: PropTypes.string,
};

BMACommunityCompactItem.defaultProps = {
  actions: undefined,
  extraLabels: undefined,
  itemClassName: "",
  showPermissionLabel: false,
  detailUrl: undefined,
};