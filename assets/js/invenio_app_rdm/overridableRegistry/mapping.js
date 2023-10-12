import CardDepositStatusBox from "../CardDepositStatusBox";

export const overriddenComponents = {
    "InvenioAppRdm.Deposit.CardDepositStatusBox.container": CardDepositStatusBox,
    "InvenioAppRdm.Deposit.AccessRightField.container": () => null,
}