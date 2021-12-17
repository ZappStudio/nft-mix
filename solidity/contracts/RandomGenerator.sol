// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";

contract RandomGenerator is VRFConsumerBase, Ownable {
    using Address for address;

    struct RequestRandomCollectibles {
        bytes32 requestId;
        uint256[] randomValues;
        uint256 amountRequested;
    }

    /** Maybe it's not safe send information inside event
      * It's better execute event and access information inside contract
      * To be sure the information it's trustworthy
      **/
    event EventRequestRandomsFinished();
    event EventRequestInitialized(bytes32 indexed requestId);

    //Vars
    mapping(bytes32 => RequestRandomCollectibles) public requests;
    bytes32 internal keyHash;
    uint256 internal fee;

    uint256 internal limitDown;
    uint256 internal limitTop;

    constructor(
        uint256 _limitDown,
        uint256 _limitTop,
        address _VRFCoordinator,
        address _LinkToken,
        bytes32 _keyhash
    ) VRFConsumerBase(_VRFCoordinator, _LinkToken) {
        limitDown = _limitDown;
        limitTop = _limitTop;
        keyHash = _keyhash;
        fee = 0.1 * 10 ** 18;
    }

    function getLimitDown() public returns (uint256 query){
        return limitDown;
    }

    function getLimitTop() public returns (uint256 query){
        return limitTop;
    }

    function getRequestByRequestId(bytes32 requestId) public returns (RequestRandomCollectibles memory query){
        return requests[requestId];
    }

    /**
    * Create request and save as request initialized
    * return struct as contract checking
    * In this moment struct will be empty except requestID, it means is not completed yet
    **/
    function requestRandomForCollectibles(uint256 amountRequested) public returns (bytes32 requestId){
        RequestRandomCollectibles memory newRequest;
        newRequest.requestId = requestRandomness(keyHash, fee);
        newRequest.amountRequested = amountRequested;
        requests[newRequest.requestId] = newRequest;
        emit EventRequestInitialized(newRequest.requestId);
        return newRequest.requestId;
    }
    /**
    * Generated new random function chainlink
    * Coerce random at limits and expand in its limited random high down.
    * emit and event with data
    **/
    function fulfillRandomness(bytes32 requestId, uint256 randomNumber)
    internal
    override
    {
        uint256 randomResult = coerceAtLimits(limitDown, limitTop, randomNumber);
        uint256[] memory expandedValues = expand(limitDown, limitTop, randomResult, requests[requestId].amountRequested);
        requests[requestId].randomValues = expandedValues;
        emit EventRequestRandomsFinished();
    }


    /* Testing purpose */
    function coerceAtLimitsTest(uint256 _limitDown,
        uint256 _limitTop,
        uint256 number) public returns (uint256 numberLimited) {
        return coerceAtLimits(_limitDown, _limitTop, number);
    }

    function coerceAtLimits(uint256 _limitDown,
        uint256 _limitTop,
        uint256 number) public pure returns (uint256 numberLimited) {
        return number % (_limitTop - _limitDown + 1 ) + _limitDown;
    }

    /**
    * Chainlink function to expand a randomvalue in more values
    */
    function expand(
        uint _limitDown,
        uint _limitTop,
        uint256 randomValue, uint256 n) public pure returns (uint256[] memory expandedValues) {
        expandedValues = new uint256[](n);
        for (uint256 i = 0; i < n; i++) {
            expandedValues[i] = coerceAtLimits(_limitDown, _limitTop, uint256(keccak256(abi.encode(randomValue, i))));
        }
        return expandedValues;
    }
}
