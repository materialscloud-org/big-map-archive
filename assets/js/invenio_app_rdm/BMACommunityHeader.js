import { i18next } from "@translations/invenio_rdm_records/i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Image } from "react-invenio-forms";
import { connect } from "react-redux";
import { Button, Container } from "semantic-ui-react";
import { changeSelectedCommunity } from "@js/invenio_rdm_records/src/deposit/state/actions";
import { BMACommunitySelectionModal } from "./BMACommunitySelectionModal";

class BMACommunityHeaderComponent extends Component {
  constructor(props) {
    super(props);
    this.state = {
      modalOpen: false,
    };
  }
  render() {
    const {
      changeSelectedCommunity,
      community,
      imagePlaceholderLink,
      showCommunitySelectionButton,
      disableCommunitySelectionButton,
      showCommunityHeader,
      record,
    } = this.props;
    const { modalOpen } = this.state;

    return (
      showCommunityHeader && (
      <>
        <div className="ui container">
          <div className="ui grid">
            <div className="eleven wide computer sixteen wide mobile sixteen wide tablet column">
              <ul className="pl-15">
                <li>This is the <b>main repository</b>, intended for storing and sharing research data.</li>
                <li>For testing purposes, use the <a href="https://big-map-archive-demo.materialscloud.org/">demo repository</a>.</li>
                <li>Proceed as follows to privately share a record with a community:</li>
                  <ul className="pl-15">
                    <li>Select one of your communities.</li>
                    <li>Upload or import at least one file.</li>
                    <li>Fill in the required metadata fields (<span className="color-red">*</span>).</li>
                    <li>Click the "Share with community" button.</li>
                  </ul>
                </ul>
            </div>
          </div>
        </div>
        <Container
          className="page-subheader-outer compact ml-0-mobile mr-0-mobile"
          fluid
        >
          <Container className="page-subheader">
            {community ? (
              <>
                <div className="page-subheader-element">
                  <Image
                    rounded
                    className="community-header-logo"
                    src={community.links?.logo || imagePlaceholderLink} // logo is undefined when new draft and no selection
                    fallbackSrc={imagePlaceholderLink}
                  />
                </div>
                <div className="page-subheader-element flex align-items-center">
                  {community.metadata.title}
                </div>
              </>
            ) : (
              <></>
            )}
            <div className="community-header-element flex align-items-center">
              {showCommunitySelectionButton && (
                <>
                  <BMACommunitySelectionModal
                    onCommunityChange={(community) => {
                      changeSelectedCommunity(community);
                      this.setState({ modalOpen: false });
                    }}
                    onModalChange={(value) => this.setState({ modalOpen: value })}
                    modalOpen={modalOpen}
                    chosenCommunity={community}
                    displaySelected
                    record={record}
                    trigger={
                      <Button
                        className="community-header-button"
                        disabled={disableCommunitySelectionButton}
                        onClick={() => this.setState({ modalOpen: true })}
                        primary
                        size="mini"
                        name="setting"
                        type="button"
                        content={
                          community
                            ? i18next.t("Change")
                            : i18next.t("Select community")
                        }
                      />
                    }
                  />
                  {community && (
                    <Button
                      basic
                      size="mini"
                      labelPosition="left"
                      className="community-header-button ml-5"
                      onClick={() => changeSelectedCommunity(null)}
                      content={i18next.t("Remove")}
                      icon="close"
                      disabled={disableCommunitySelectionButton}
                    />
                  )}
                </>
              )}
            </div>
          </Container>
        </Container>
      </>
      )
    );
  }
}

BMACommunityHeaderComponent.propTypes = {
  imagePlaceholderLink: PropTypes.string.isRequired,
  community: PropTypes.object,
  disableCommunitySelectionButton: PropTypes.bool.isRequired,
  showCommunitySelectionButton: PropTypes.bool.isRequired,
  showCommunityHeader: PropTypes.bool.isRequired,
  changeSelectedCommunity: PropTypes.func.isRequired,
  record: PropTypes.object.isRequired,
};

BMACommunityHeaderComponent.defaultProps = {
  community: undefined,
};

const mapStateToProps = (state) => ({
  community: state.deposit.editorState.selectedCommunity,
  disableCommunitySelectionButton:
    state.deposit.editorState.ui.disableCommunitySelectionButton,
  showCommunitySelectionButton:
    state.deposit.editorState.ui.showCommunitySelectionButton,
  showCommunityHeader: state.deposit.editorState.ui.showCommunityHeader,
});

const mapDispatchToProps = (dispatch) => ({
  changeSelectedCommunity: (community) => dispatch(changeSelectedCommunity(community)),
});

export const BMACommunityHeader = connect(
  mapStateToProps,
  mapDispatchToProps
)(BMACommunityHeaderComponent);