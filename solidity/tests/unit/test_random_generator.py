import pytest

from brownie import network, RandomGenerator
# noinspection PyUnresolvedReferences
from scripts.helpful_scripts import (
    get_account,
    get_contract,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)

LIMIT_TOP = 1000
LIMIT_DOWN = 100
AMOUNT_NUMBERS = 10

def pytest_namespace():
    return {'random_generator': 0}

@pytest.fixture(autouse=True)
def run_around_tests(get_keyhash,
                     chainlink_fee):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")

    random_generator = RandomGenerator.deploy(
        LIMIT_DOWN,
        LIMIT_TOP,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        get_keyhash,
        {"from": get_account()},
    )
    get_contract("link_token").transfer(
        random_generator.address, chainlink_fee * 3, {"from": get_account()}
    )
    pytest.random_generator = random_generator


def test_generated_new_random_numbers(
        chainlink_fee
):
    get_contract("link_token").transfer(
        pytest.random_generator.address, chainlink_fee * 3, {"from": get_account()}
    )

    transaction_receipt = pytest.random_generator.requestRandomForCollectibles(AMOUNT_NUMBERS)
    requestId = transaction_receipt.events["EventRequestInitialized"]["requestId"]

    assert isinstance(transaction_receipt.txid, str)
    get_contract("vrf_coordinator").callBackWithRandomness(
        requestId, 150, pytest.random_generator.address, {"from": get_account()}
    )

    print("Request id")
    print(requestId)
    request = pytest.random_generator.getRequestByRequestId(requestId).return_value

    print(request)
    # Assert functions
    assert LIMIT_DOWN == pytest.random_generator.getLimitDown().return_value
    assert LIMIT_TOP == pytest.random_generator.getLimitTop().return_value
    assert request[0] == requestId
    for x in request[1]:
        assert LIMIT_TOP >= x >= LIMIT_DOWN
    assert request[2] == AMOUNT_NUMBERS
    assert len(request[1]) == AMOUNT_NUMBERS


def test_coerce_function(
        get_keyhash
):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    random_generator = RandomGenerator.deploy(
        LIMIT_DOWN,
        LIMIT_TOP,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        get_keyhash,
        {"from": get_account()},
    )

    numberList = [LIMIT_TOP + 1650, LIMIT_DOWN - 100, LIMIT_DOWN, LIMIT_TOP]

    for x in numberList:
        y = random_generator.coerceAtLimitsTest(LIMIT_DOWN, LIMIT_TOP, x).return_value
        assert y in range(LIMIT_DOWN, LIMIT_TOP)
