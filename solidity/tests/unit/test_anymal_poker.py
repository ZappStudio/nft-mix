from eip712.messages import EIP712Message, EIP712Type
from deploy_contracts import *
from brownie import (
    reverts,
    accounts
)
import os


# noinspection PyUnresolvedReferences
from scripts.helpful_scripts import (
    get_account,
    get_contract,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)


@pytest.fixture(autouse=True)
def before_test(get_keyhash,
                chainlink_fee):
    deploy(get_keyhash, chainlink_fee)


def test_presale_inactive():
    check_local_testing()
    pytest.animal_poker.setPresaleActive(False)

    with reverts("Presale isn't active"):
        pytest.animal_poker.mintPresale(10, {"from": get_account()})


def test_presale_active():
    check_local_testing()
    pytest.animal_poker.setPresaleActive(True)
    pytest.animal_poker.mintPresale(1, {"from": get_account()})


def test_sale_inactive():
    check_local_testing()
    pytest.animal_poker.setSaleActive(False)
    with reverts("Sale isn't active"):
        pytest.animal_poker.mintToken(10, {"from": get_account()})


def make_sale_active():
    check_local_testing()
    pytest.animal_poker.setSaleActive(True)
    transaction_receipt = pytest.animal_poker.mintToken(AMOUNT_NUMBERS, {"from": pytest.owner_address})

    request_id = transaction_receipt.events["requestedCollectible"]["requestId"]
    transaction_coordinator = pytest.vrf_coordinator.callBackWithRandomness(
        request_id, 4, pytest.animal_poker.address, {"from": get_account()}
    )
    assert isinstance(transaction_receipt.txid, str)
    return request_id


def test_get_request_by_request_id():
    """Verify that user who is not owner of request cant get it"""
    request_id = make_sale_active()
    with reverts("This request is not your request!"):
        pytest.animal_poker.getRequestByRequestId(request_id, {"from": get_account(1)})


def test_check_request_id():
    """Verify that request id is properly generated and get request id is returning properly"""
    request_id = make_sale_active()
    request = pytest.animal_poker.getRequestByRequestId(request_id, {"from": pytest.owner_address}).return_value
    print(request)
    # Assert functions
    assert request[0] == pytest.owner_address
    assert request[1] == request_id
    assert len(request[2]) == AMOUNT_NUMBERS
    for x in request[2]:
        assert LIMIT_TOP >= x >= LIMIT_DOWN
    assert request[3] == AMOUNT_NUMBERS
    assert LIMIT_DOWN == request[4]
    assert LIMIT_TOP == request[5]


def test_tokens_are_minted_properly():
    """ Verify that tokens are properly minted and have properly owner """
    request_id = make_sale_active()
    request = pytest.animal_poker.getRequestByRequestId(request_id, {"from": pytest.owner_address}).return_value
    print(request)
    token_balances = pytest.animal_poker \
        .tokensOfOwner(pytest.owner_address, {"from": pytest.owner_address})
    print(token_balances)
    assert len(token_balances) == AMOUNT_NUMBERS


def test_metadata_contract_is_correct():
    """ Test of metadata contract is correct """
    request_id = make_sale_active()
    token_balances = pytest.animal_poker \
        .tokensOfOwner(pytest.owner_address, {"from": pytest.owner_address})
    assert len(token_balances) == AMOUNT_NUMBERS
    name = pytest.animal_poker \
        .name({"from": pytest.owner_address})
    symbol = pytest.animal_poker \
        .symbol({"from": pytest.owner_address})

    assert name == NAME_CONTRACT
    assert symbol == SYMBOL_CONTRACT


def test_lazy_redeem():
    """ Test lazy redeem with correct signing """
    voucher = create_voucher(1)
    print(voucher)


def create_voucher(token_id):
    domain = signing_domain()
    test_message = Voucher(tokenId=token_id)
    # >>> local = accounts.add(private_key="0x416b8a7d9290502f5661da81f0cf43893e3d19cb9aea3c426cfb36e8186e9c09")
    account = accounts.add(private_key=os.getenv('PRIVATE_KEY'))
    account.sign_message(domain, test_message)


def signing_domain():
    chainId = pytest.animal_poker.getChainID()
    domain = {
        "name": SIGNING_DOMAIN_NAME,
        "version": SIGNING_DOMAIN_VERSION,
        "verifyingContract": pytest.animal_poker.address,
        "chainId": chainId
    }
    return domain


class Voucher(EIP712Type):
    tokenId: "uint256"

# async createVoucher(tokenId, uri, minPrice = 0) {
#     const voucher = { tokenId, uri, minPrice }
# const domain = await this._signingDomain()
# const types = {
#     NFTVoucher: [
#         {name: "tokenId", type: "uint256"},
#         {name: "minPrice", type: "uint256"},
#         {name: "uri", type: "string"},
#     ]
# }
# const signature = await this.signer._signTypedData(domain, types, voucher)
# return {
#     ...voucher,
#        signature,
# }
# }

# /**
# * @private
# * @returns {object} the EIP-721 signing domain, tied to the chainId of the signer
# */
# async _signingDomain() {
# if (this._domain != null) {
# return this._domain
# }
# const chainId = await this.contract.getChainID()
# this._domain = {
# name: SIGNING_DOMAIN_NAME,
# version: SIGNING_DOMAIN_VERSION,
# verifyingContract: this.contract.address,
# chainId,
# }
# return this._domain
# }
# }
