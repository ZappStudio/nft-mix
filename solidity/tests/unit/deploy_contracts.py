import pytest

# noinspection PyUnresolvedReferences
from brownie import network, RandomGenerator, AnimalPoker, reverts
# noinspection PyUnresolvedReferences
from scripts.helpful_scripts import (
    get_account,
    get_contract,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)

LIMIT_TOP = 10000
LIMIT_DOWN = 1
AMOUNT_NUMBERS = 10
NAME_CONTRACT = "Animal Poker"
SYMBOL_CONTRACT = "APD"
BASE_URI_CONTRACT = "https://animalpoker.zapp.dev/"
SIGNING_DOMAIN_NAME = NAME_CONTRACT
SIGNING_DOMAIN_VERSION = "1.0.0"


def pytest_namespace():
    return {
        'random_generator': 0,
        'animal_poker': 0,
        'owner_address': 0
    }


def deploy(get_keyhash,
           chainlink_fee):
    # Arrange
    check_local_testing()
    pytest.vrf_coordinator = get_contract("vrf_coordinator")
    pytest.link_token = get_contract("link_token")

    random_generator = RandomGenerator.deploy(
        pytest.vrf_coordinator.address,
        pytest.link_token.address,
        get_keyhash,
        {"from": get_account()},
    )

    animal_poker = AnimalPoker.deploy(
        pytest.vrf_coordinator.address,
        pytest.link_token.address,
        get_keyhash,
        {"from": get_account()},
    )

    pytest.random_generator = random_generator
    pytest.animal_poker = animal_poker
    pytest.owner_address = get_account()

    pytest.link_token.transfer(
        random_generator.address, chainlink_fee * 3, {"from": get_account()}
    )
    pytest.link_token.transfer(
        animal_poker.address, chainlink_fee * 3, {"from": get_account()}
    )


def check_local_testing():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
