// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";
import "./RandomGenerator.sol";
import "./libraries/SharedStructs.sol";

contract AnimalPoker is ERC721Enumerable, RandomGenerator {
    using Address for address;

    // Starting and stopping sale, presale and whitelist
    bool public saleActive = false;
    bool public whitelistActive = false;
    bool public presaleActive = false;

    // Reserved for the team, customs, giveaways, collabs and so on.
    uint256 public reserved = 150;

    // Price of each token
    uint256 public initial_price = 0.04 ether;
    uint256 public price;

    // Maximum limit of tokens that can ever exist
    uint256 public constant MAX_SUPPLY = 10000;
    uint256 public constant MAX_PRESALE_SUPPLY = 500;
    uint256 public constant MAX_MINT_PER_TX = 20;

    // The base link that leads to the image / video of the token
    string public baseTokenURI = "https://api.funkycrocs.io/";

    /* Team addresses for withdrawals */
    address public a1;
    address public a2;
    address public a3;

    enum Cards {ClubsK, DiamondsK, HeartsK, SpadesK}

    // Events
    event requestedCollectible(bytes32 indexed requestId);
    event numberGenerated(bytes32 indexed requestId);
    event requestMinted(bytes32 indexed requestId);

    // List of addresses that have a number of reserved tokens for whitelist
    mapping(address => uint256) public whitelistReserved;
    // add other things
    mapping(bytes32 => address) public requestIdToSender;
    mapping(bytes32 => string) public requestIdToTokenURI;
    mapping(uint256 => Cards) public tokenIdToBreed;
    mapping(bytes32 => uint256) public requestIdToTokenId;

    constructor(
        address _VRFCoordinator,
        address _LinkToken,
        bytes32 _keyhash
    )
    RandomGenerator(_VRFCoordinator, _LinkToken, _keyhash)
    ERC721("Anymal Poker", "APD")
    {

    }

    // Override so the openzeppelin tokenURI() method will use this method to create the full tokenURI instead
    function _baseURI() internal view virtual override returns (string memory) {
        return baseTokenURI;
    }

    // See which address owns which tokens
    function tokensOfOwner(address addr) public view returns (uint256[] memory) {
        uint256 tokenCount = balanceOf(addr);
        uint256[] memory tokensId = new uint256[](tokenCount);
        for (uint256 i; i < tokenCount; i++) {
            tokensId[i] = tokenOfOwnerByIndex(addr, i);
        }
        return tokensId;
    }

    // Exclusive whitelist minting
    function mintWhitelist(uint256 _amount) public payable {
        uint256 supply = totalSupply();
        uint256 reservedAmt = whitelistReserved[msg.sender];
        require(whitelistActive, "Whitelist isn't active");
        require(reservedAmt > 0, "No tokens reserved for your address");
        require(_amount <= reservedAmt, "Can't mint more than reserved");
        require(supply + _amount <= MAX_SUPPLY, "Can't mint more than max supply");
        require(msg.value == price * _amount, "Wrong amount of ETH sent");
        whitelistReserved[msg.sender] = reservedAmt - _amount;
        for (uint256 i; i < _amount; i++) {
            _safeMint(msg.sender, supply + i);
        }
    }

    function requestRandomFinished(RequestRandomCollectibles memory request) public override {
        mintRequest(request.requestId);
    }


    // Presale minting
    function mintPresale(uint256 _amount) public payable {
        uint256 supply = totalSupply();
        require(presaleActive, "Presale isn't active");
        require(
            _amount > 0 && _amount <= MAX_MINT_PER_TX,
            "Can only mint between 1 and 20 tokens at once"
        );
        require(
            supply + _amount <= MAX_PRESALE_SUPPLY,
            "Can't mint more than max supply"
        );
        require(msg.value == price * _amount, "Wrong amount of ETH sent");

        bytes32 requestId = requestRandom(1, MAX_SUPPLY, _amount);
        emit requestedCollectible(requestId);
    }

    // Standard mint function
    function mintToken(uint256 _amount) public payable {

        uint256 supply = totalSupply();
        require(saleActive, "Sale isn't active");
        require(
            _amount > 0 && _amount <= MAX_MINT_PER_TX,
            "Can only mint between 1 and 10 tokens at once"
        );
        require(supply + _amount <= MAX_SUPPLY, "Can't mint more than max supply");
        require(msg.value == price * _amount, "Wrong amount of ETH sent");

        bytes32 requestId = super.requestRandom(1, MAX_SUPPLY, _amount);
        emit requestedCollectible(requestId);
    }

    /*
     * This request is problematic in order to protect we have to get request from random request
     * We have to attach to sender, to avoid minting hack
     * Minting all received request, but we don't use this information and we query contract with queryid
     * If random it will be minted, we use as offset in order to keep randomly.
     *
     */
    function mintRequest(bytes32 requestId) public {
        RequestRandomCollectibles memory safeRequest = getRequestByRequestId(
            requestId
        );
        require(requests[requestId].sender == msg.sender || msg.sender == VRFCoordinator, "This request is not your request!");


        for (uint256 i; i < safeRequest.randomValues.length; i++) {
            uint256 random = safeRequest.randomValues[i];
            if (_exists(random)) {
                for (uint256 j = random; j < MAX_SUPPLY; j++) {
                    if (!_exists(i)) {
                        _safeMint(msg.sender, j);
                        break;
                    }
                }
            } else {
                _safeMint(requests[requestId].sender, random);
            }
        }


        /*    for (uint256 i; i < safeRequest.randomValues.length; i++) {
                uint256 random = safeRequest.randomValues[i];
                if (_exists(random)) {
                    for (uint256 j = random; j < MAX_SUPPLY; j++) {
                        if (!_exists(i)) {
                            _safeMint(msg.sender, j);
                        }
                    }
                } else {
                    _safeMint(msg.sender, random);
                }
            }*/

        emit requestMinted(requestId);
    }

    // Admin minting function to reserve tokens for the team, collabs, customs and giveaways
    function mintReserved(uint256 _amount) public onlyOwner {
        // Limited to a publicly set amount
        require(_amount <= reserved, "Can't reserve more than set amount");
        reserved -= _amount;
        uint256 supply = totalSupply();
        for (uint256 i; i < _amount; i++) {
            _safeMint(msg.sender, supply + i);
        }
    }

    // Edit reserved whitelist spots
    function editWhitelistReserved(address[] memory _a, uint256[] memory _amount)
    public
    onlyOwner
    {
        for (uint256 i; i < _a.length; i++) {
            whitelistReserved[_a[i]] = _amount[i];
        }
    }

    // Start and stop whitelist
    function setWhitelistActive(bool val) public onlyOwner {
        whitelistActive = val;
    }

    // Start and stop presale
    function setPresaleActive(bool val) public onlyOwner {
        presaleActive = val;
    }

    // Start and stop sale
    function setSaleActive(bool val) public onlyOwner {
        saleActive = val;
    }

    // Set new baseURI
    function setBaseURI(string memory baseURI) public onlyOwner {
        baseTokenURI = baseURI;
    }

    // Set a different price in case ETH changes drastically
    function setPrice(uint256 newPrice) public onlyOwner {
        price = newPrice;
    }

    // Set team addresses
    function setAddresses(address[] memory _a) public onlyOwner {
        a1 = _a[0];
        a2 = _a[1];
        a3 = _a[2];
    }

    // Withdraw funds from contract for the team
    function withdrawTeam(uint256 amount) public payable onlyOwner {
        uint256 percent = amount / 100;
        require(payable(a1).send(percent * 40));
        require(payable(a2).send(percent * 30));
        require(payable(a3).send(percent * 30));
    }
}
