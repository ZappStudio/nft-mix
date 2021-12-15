import pytest
from brownie import network, AnymalPoker
from scripts.helpful_scripts import (
    get_account,
    get_contract,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)
import time


def test_can_create_advanced_collectible_integration(
    get_keyhash,
    chainlink_fee,
):
    # Arrange
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for integration testing")
    anymal_poker = AnymalPoker.deploy(
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        get_keyhash,
        {"from": get_account()},
    )
    get_contract("link_token").transfer(
        anymal_poker.address, chainlink_fee * 3, {"from": get_account()}
    )
    # Act
    anymal_poker.createCollectible("None", {"from": get_account()})
    time.sleep(75)
    # Assert
    assert anymal_poker.tokenCounter() > 0
