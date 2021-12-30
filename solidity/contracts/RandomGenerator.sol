// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";
import "./libraries/SharedStructs.sol";

contract RandomGenerator is VRFConsumerBase, Ownable {
    using Address for address;

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
    address internal linkToken;

    constructor(
        address _VRFCoordinator,
        address _LinkToken,
        bytes32 _keyhash,
        uint256 _fee
    ) VRFConsumerBase(_VRFCoordinator, _LinkToken) {
        linkToken = _LinkToken;
        keyHash = _keyhash;
        // fee = 0.1 * 10**18;
        fee = _fee;
    }

    function getRequestByRequestId(bytes32 requestId)
    public
    returns (RequestRandomCollectibles memory query)
    {
        require(requests[requestId].sender == msg.sender, "This request is not your request!");
        return requests[requestId];
    }

    /**
     * Create request and save as request initialized
     * return struct as contract checking
     * In this moment struct will be empty except requestID, it means is not completed yet
     **/
    function requestRandom(
        uint256 limitDown,
        uint256 limitTop,
        uint256 amountRequested
    ) public returns (bytes32 requestId) {
        RequestRandomCollectibles memory newRequest;
        newRequest.sender = msg.sender;
        newRequest.requestId = requestRandomness(keyHash, fee);
        newRequest.amountRequested = amountRequested;
        newRequest.limitTop = limitTop;
        newRequest.limitDown = limitDown;
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
        RequestRandomCollectibles memory requestRead = getRequestByRequestId(
            requestId
        );
        uint256 randomResult = coerceAtLimits(
            requestRead.limitDown,
            requestRead.limitTop,
            randomNumber
        );
        uint256[] memory expandedValues = expand(
            requestRead.limitDown,
            requestRead.limitTop,
            randomResult,
            requestRead.amountRequested
        );
        requests[requestId].randomValues = expandedValues;
        requestRandomFinished(requestRead);

        emit EventRequestRandomsFinished();
    }

    function requestRandomFinished(RequestRandomCollectibles memory requestRandomCollectibles) public virtual {}

    /* Testing purpose */
    function coerceAtLimitsTest(
        uint256 _limitDown,
        uint256 _limitTop,
        uint256 number
    ) public returns (uint256 numberLimited) {
        return coerceAtLimits(_limitDown, _limitTop, number);
    }

    function coerceAtLimits(
        uint256 _limitDown,
        uint256 _limitTop,
        uint256 number
    ) public pure returns (uint256 numberLimited) {
        return (number % (_limitTop - _limitDown + 1)) + _limitDown;
    }

    /**
     * Chainlink function to expand a randomvalue in more values
     */
    function expand(
        uint256 _limitDown,
        uint256 _limitTop,
        uint256 randomValue,
        uint256 n
    ) public pure returns (uint256[] memory expandedValues) {
        expandedValues = new uint256[](n);
        for (uint256 i = 0; i < n; i++) {
            expandedValues[i] = coerceAtLimits(
                _limitDown,
                _limitTop,
                uint256(keccak256(abi.encode(randomValue, i)))
            );
        }
        return expandedValues;
    }
}
