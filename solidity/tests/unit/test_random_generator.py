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
def test_generated_new_random_numbers(
        chainlink_fee
):
    transaction_receipt = pytest.random_generator.requestRandom(
        LIMIT_DOWN,
        LIMIT_TOP,
        AMOUNT_NUMBERS
    )
    request_id = transaction_receipt.events["EventRequestInitialized"]["requestId"]

    assert isinstance(transaction_receipt.txid, str)
    print("Calling the callback function inside Chainlink contract")
    pytest.vrf_coordinator.callBackWithRandomness(
        request_id, 700, pytest.random_generator.address, {"from": get_account()}
    )

    print("Request struct from contract that must be generated")
    request = pytest.random_generator.getRequestByRequestId(request_id).return_value

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


def test_coerce_function(
        get_keyhash
):
    numberList = [LIMIT_TOP + 1650, LIMIT_DOWN, LIMIT_DOWN, LIMIT_TOP]

    for x in numberList:
        y = pytest.random_generator.coerceAtLimitsTest(LIMIT_DOWN, LIMIT_TOP, x).return_value
        assert y in range(LIMIT_DOWN, LIMIT_TOP)
