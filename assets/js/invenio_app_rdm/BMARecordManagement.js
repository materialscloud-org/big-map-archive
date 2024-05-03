// This file is part of BIG-MAP Archive
// Copyright (C) 2024 BIG-MAP Archive Team.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";

export class BMARecordManagement extends Component {
  render() {
    window.addEventListener("load", changeText);
    function changeText() {
      // Change text in share links button
      var buttonTags = document.getElementsByTagName("button");
      for (const bt of buttonTags) {
        if (bt.textContent == "Share") {
          bt.textContent = "Share links";
        }
      }
    }
    // Leave the following to do not see the text changing while the page load
    changeText();
    return(<></>);
  }
}
