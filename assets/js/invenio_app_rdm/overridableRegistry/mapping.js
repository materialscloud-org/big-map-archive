import BMACardDepositStatusBox from "../BMACardDepositStatusBox";
import { BMACommunityHeader } from "../BMACommunityHeader";
import { BMACommunitySelectionSearch } from "../BMACommunitySelectionSearch.js";

export const overriddenComponents = {
    "InvenioAppRdm.Deposit.CardDepositStatusBox.container": BMACardDepositStatusBox,
    "InvenioAppRdm.Deposit.AccessRightField.container": () => null,
    "InvenioAppRdm.Deposit.CommunityHeader.container": BMACommunityHeader,
}