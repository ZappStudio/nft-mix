import pytest
from brownie import network, AnymalPoker
from scripts.helpful_scripts import (
    get_account,
    get_contract,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)



def test_can_create_advanced_collectible(
    get_keyhash,
    chainlink_fee,
):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    anymal_poker = AnymalPoker.deploy(
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        get_keyhash,
        {"from": get_account()},
    )
    anymal_poker.setSaleActive(True)

    get_contract("link_token").transfer(
        anymal_poker.address, chainlink_fee * 3, {"from": get_account()}
    )
    # Act
    transaction_receipt = anymal_poker.mintToken(
        1, {"from": get_account()}
    )
    requestId = transaction_receipt.events["requestedCollectible"]["requestId"]
    assert isinstance(transaction_receipt.txid, str)
    get_contract("vrf_coordinator").callBackWithRandomness(
        requestId, 777, anymal_poker.address, {"from": get_account()}
    )
    # Assert
    assert anymal_poker.tokenCounter() > 0
    assert isinstance(anymal_poker.tokenCounter(), int)