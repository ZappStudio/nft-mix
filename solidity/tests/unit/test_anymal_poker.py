from deploy_contracts import *
from brownie import reverts

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
    pytest.vrf_coordinator.callBackWithRandomness(
        request_id, 777, pytest.animal_poker.address, {"from": pytest.owner_address}
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

#
# def test_can_create_advanced_collectible(
#         get_keyhash,
#         chainlink_fee,
# ):
#     check_local_testing()
#
#     pytest.animal_poker.setSaleActive(True)
#
#     get_contract("link_token").transfer(
#         pytest.animal_poker.address, chainlink_fee * 3, {"from": get_account()}
#     )
#     # Act
#     transaction_receipt = pytest.animal_poker.mintToken(
#         10, {"from": get_account()}
#     )
#     requestId = transaction_receipt.events["requestedCollectible"]["requestId"]
#     assert isinstance(transaction_receipt.txid, str)
#     get_contract("vrf_coordinator").callBackWithRandomness(
#         requestId, 777, pytest.animal_poker.address, {"from": get_account()}
#     )
#     # Assert
#     assert pytest.animal_poker.tokenCounter() == 10
#     assert isinstance(pytest.animal_poker.tokenCounter(), int)
