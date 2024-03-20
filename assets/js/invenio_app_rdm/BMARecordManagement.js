// This file is part of BIG-MAP Archive
// Copyright (C) 2024 BIG-MAP Archive Team.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";

export class BMARecordManagement extends Component {
  render() {
    var buttonTags = document.getElementsByTagName("button");
    for (var i = 0; i < buttonTags.length; i++) {
      if (buttonTags[i].textContent == "Share") {
        buttonTags[i].textContent = "Share links";
      }
    }
    return(<></>);
  }
}
