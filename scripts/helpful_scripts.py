from mmap import ACCESS_COPY
from operator import ne
from tracemalloc import start
from turtle import right
from brownie import (
    accounts,
    network,
    config,
    MockV3Aggregator,
    Contract,
    VRFCoordinatorMock,
    LinkToken,
    interface,
)
from web3 import Web3


DECIMALS = 8
STARTING_PRICE = 200000000000
FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork-alchemy", "mainnet-fork"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]


def get_account(index=None, id=None):

    # accounts[0]
    # accounts.add("env")
    # accounts.load("id")
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    """
    this function will grab contract address from brownie config if defined
    otherwise it will deploy a mock version of that contract and return that mock contract

        Args:
            contract_name(string):

        Returns:
            brownie.network.contract.ProjectContract: the most recently deployed version of the contract
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        # address
        # abi
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )

    return contract


def deploy_mocks(decimals=DECIMALS, starting_price=STARTING_PRICE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, starting_price, {"from": account})
    mock_link = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(mock_link.address, {"from": account})
    print("deployed mock")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):  # 0.1 Link
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    # tx = link_token.transfer(contract_address, amount, {"from":account})
    # we can also use interface to construct a link_token contract
    link_token_contract = interface.LinkTokenInterface(link_token.address)
    tx = link_token_contract.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Fund the contract!")
