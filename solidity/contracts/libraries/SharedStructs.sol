// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

struct RequestRandomCollectibles {
  address sender;
  bytes32 requestId;
  uint256[] randomValues;
  uint256 amountRequested;
  uint256 limitDown;
  uint256 limitTop;
}

library SharedStructs {}
