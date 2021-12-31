from deploy_contracts import *
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


# This test is to be safe that random numbers are properly generated
# The request must be the same quantity, same requestId, same ownerId.
# The data source should be alway mapping in the contract, the struct is only to request id and testing.
def test_generated_new_random_numbers():
    request_id = pytest.random_generator.requestRandom(
        LIMIT_DOWN,
        LIMIT_TOP,
        AMOUNT_NUMBERS
    ).return_value

    pytest.vrf_coordinator.callBackWithRandomness(
        request_id, 700, pytest.random_generator.address, {"from": get_account()}
    )

    request = pytest.random_generator.getRequestByRequestId(request_id).return_value

    # Assert functions
    assert request[0] == pytest.owner_address
    assert request[1] == request_id
    assert len(request[2]) == AMOUNT_NUMBERS
    for x in request[2]:
        assert LIMIT_TOP >= x >= LIMIT_DOWN
    assert request[3] == AMOUNT_NUMBERS
    assert LIMIT_DOWN == request[4]
    assert LIMIT_TOP == request[5]


def test_coerce_function():
    numberList = [LIMIT_TOP + 1650, LIMIT_DOWN, LIMIT_DOWN, LIMIT_TOP]

    for x in numberList:
        y = pytest.random_generator.coerceAtLimitsTest(LIMIT_DOWN, LIMIT_TOP, x).return_value
        assert y in range(LIMIT_DOWN, LIMIT_TOP)
