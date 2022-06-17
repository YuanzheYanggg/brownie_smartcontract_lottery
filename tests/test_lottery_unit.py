# if we want 50 dollars usd equivalent ether
# meaning current ether price is 1230usd/ether, 50 usd = 0.04 ether
# 0.04 ether will roughly equals to 0.04 * 1e18 wei

from re import L
from brownie import Lottery, accounts, network, config, exceptions
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    get_contract,
)
from scripts.deploy_lottery import deploy_lottery, fund_with_link
from web3 import Web3
import pytest


def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    entrance_fee = lottery.getEntranceFee()
    # if price of eth is 2000
    # usd entryfee is 50 dollars
    # equivalent eth entry fee is 50/2000 * 1e18
    expected = Web3.toWei(0.025, "ether")
    assert entrance_fee == expected


def test_cant_enter_unless_starter():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account()})


def test_can_startenter_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    assert lottery.players(0) == account


def test_can_end_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    assert lottery.lottery_state() == 2


def test_can_pick_winner_correctly():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    for i in range(9):
        lottery.enter(
            {"from": get_account(index=i + 1), "value": lottery.getEntranceFee()}
        )
    fund_with_link(lottery)
    transaction = lottery.endLottery({"from": account})
    request_id = transaction.events["RequestedRandomness"]["requestId"]
    # since we are doing the mock
    # we need to predetermine the random number
    STATIC_RNG = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RNG, lottery.address, {"from": account}
    )
    starting_balance_of_account = get_account(index=4).balance()
    balance_of_lottery = lottery.balance()
    # 777 = 3 mod(9)
    assert lottery.recentWinner() == get_account(index=4)
    assert lottery.balance() == 0
    assert (
        get_account(index=4).balance()
        == starting_balance_of_account + balance_of_lottery
    )
