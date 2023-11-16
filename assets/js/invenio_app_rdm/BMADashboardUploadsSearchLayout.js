import { i18next } from "@translations/invenio_app_rdm/i18next";
import React from "react";
import { Button } from "semantic-ui-react";

import {DashboardSearchLayoutHOC} from "@js/invenio_app_rdm/user_dashboard/base";


const appName = "InvenioAppRdm.DashboardUploads";

export const BMADashboardUploadsSearchLayout = DashboardSearchLayoutHOC({
  searchBarPlaceholder: i18next.t("Search my records"),
  newBtn: (
    <Button
      positive
      icon="upload"
      href="/uploads/new"
      content={i18next.t("New upload")}
      floated="right"
    />
  ),
  appName: appName,
});