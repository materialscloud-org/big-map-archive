import BMACardDepositStatusBox from "../BMACardDepositStatusBox";
import { BMACommunityHeader } from "../BMACommunityHeader";
import BMAAccordionFieldBasicInformation from "../BMAAccordionFieldBasicInformation";
import {BMANewVersionButton} from "../BMANewVersionButton";
import {BMAFileUploaderToolbar} from "../BMAFileUploaderToolbar";
import {BMARDMRecordResultsListItem} from "../BMARDMRecordResultsListItem";
import {BMADashboardUploadsSearchLayout} from "../BMADashboardUploadsSearchLayout";
import {BMADashboardResultViewResultList} from "../BMADashboardResultViewResultList";

export const overriddenComponents = {
    "InvenioAppRdm.Deposit.CardDepositStatusBox.container": BMACardDepositStatusBox,
    "InvenioAppRdm.Deposit.AccessRightField.container": () => null,
    "InvenioAppRdm.Deposit.CommunityHeader.container": BMACommunityHeader,
    "InvenioAppRdm.Deposit.PublicationDateField.container": () => null,
    "InvenioAppRdm.Deposit.ContributorsField.container": () => null,
    "InvenioAppRdm.Deposit.LanguagesField.container": () => null,
    "InvenioAppRdm.Deposit.DateField.container": () => null,
    "InvenioAppRdm.Deposit.VersionField.container": () => null,
    "InvenioAppRdm.Deposit.AccordionFieldFunding.container": () => null,
    "InvenioAppRdm.Deposit.AccordionFieldAlternateIdentifiers.container": () => null,
    "InvenioAppRdm.Deposit.AccordionFieldReferences.container": () => null,
    "InvenioAppRdm.Deposit.PublisherField.container": () => null,
    "InvenioAppRdm.Deposit.AccordionFieldBasicInformation.container": BMAAccordionFieldBasicInformation,
    "InvenioAppRdm.Deposit.AccordionFieldRecommendedInformation.container": () => null,
    "InvenioAppRdm.Deposit.AccordionFieldRelatedWorks.container": () => null,
    "ReactInvenioDeposit.FileUploader.NewVersionButton.container": BMANewVersionButton,
    "ReactInvenioDeposit.FileUploaderToolbar.layout": BMAFileUploaderToolbar,
    "InvenioAppRdm.DashboardUploads.ResultsList.item": BMARDMRecordResultsListItem,
    "InvenioAppRdm.DashboardUploads.SearchApp.layout": BMADashboardUploadsSearchLayout,
    "InvenioAppRdm.DashboardUploads.ResultView.resultList": BMADashboardResultViewResultList,
}