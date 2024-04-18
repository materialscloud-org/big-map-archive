// This file is part of InvenioRDM
// Copyright (C) 2024-2024 CERN.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/invenio_app_rdm/i18next";

export const BMADisplayPartOfCommunities = ({ communities }) => {
  const PartOfCommunities = () => {
    // FIXME: Uncomment to enable themed banner
    // const communitiesEntries = communities.entries?.filter((community) => !(community.id === communities?.default && community?.theme));
    const communitiesEntries = communities.entries;

    if (communitiesEntries?.length > 0) {
      return (
        <>
          {i18next.t("Part of ")}
          {communitiesEntries.map((community, index) => {
            return (
              <>
                {community.metadata?.title}
                {index !== communitiesEntries.length - 1 && ", "}
              </>
            );
          })}
        </>
      );
    }
  };
  return (
    <p>
      <b>{PartOfCommunities()}</b>
    </p>
  );
};

BMADisplayPartOfCommunities.propTypes = {
  communities: PropTypes.object.isRequired,
};
