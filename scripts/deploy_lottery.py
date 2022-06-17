from tracemalloc import start
from webbrowser import get
from scripts.helpful_scripts import get_account, get_contract, fund_with_link
from brownie import Lottery, config, network
import time


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"]["rinkeby"][
            "fee"
        ],  # since brownie is not allowing me to change development config, just use rinkeby inplace
        config["networks"]["rinkeby"]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"],
    )
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from": account})
    # we often need to wait the last transaction before we terminate our RPC client
    starting_tx.wait(1)
    print("lottery is started!")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 10000000
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print("You entered the lottery!")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # since we need a random number from chainlink, we need to first fund some link to our VRFCoordinator address
    # then we can end the lottery
    fund_with_link(lottery.address)
    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(1)
    time.sleep(60)
    print(f"lottery recent winner is {lottery.recentWinner()}")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
