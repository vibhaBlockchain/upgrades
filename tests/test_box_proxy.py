from scripts.helpful_scripts import encode_function_data, get_account, upgrade
from brownie import (
    Box,
    BoxV2,
    Contract,
    ProxyAdmin,
    TransparentUpgradeableProxy,
)
import pytest


def test_proxy_delegates_call():
    account = get_account()
    box = Box.deploy({"from": account})

    proxy_admin = ProxyAdmin.deploy({"from": account})

    """
        address _logic,
        address admin_,
        bytes memory _data

        If _data is nonempty, it’s used as data in a delegate call to _logic. This will typically be an encoded function call, and allows initializating the storage of the proxy like a Solidity constructo
    """
    encode_function_call = encode_function_data(box.store, 1)
    proxy = TransparentUpgradeableProxy.deploy(
        box.address, proxy_admin.address, encode_function_call, {"from": account}
    )

    proxy_box = Contract.from_abi("Box", proxy.address, box.abi)

    assert proxy_box.retrieve() == 1
    with pytest.raises(AttributeError):
        proxy_box.increment({"from": account})


def test_proxy_upgrades():
    account = get_account()
    box = Box.deploy({"from": account})
    proxy_admin = ProxyAdmin.deploy({"from": account})
    encode_function_call = encode_function_data(box.store, 1)
    proxy = TransparentUpgradeableProxy.deploy(
        box.address, proxy_admin.address, encode_function_call, {"from": account}
    )
    proxy_box = Contract.from_abi("Box", proxy.address, box.abi)
    initial_proxy_address = proxy_box.address

    with pytest.raises(AttributeError):
        proxy_box.increment({"from": account})
    box_v2 = BoxV2.deploy({"from": account})
    upgrade(account, proxy, box_v2.address, proxy_admin, box.store, 3)
    proxy_box = Contract.from_abi("BoxV2", proxy.address, box_v2.abi)
    upgraded_proxy_address = proxy_box.address

    assert proxy_box.retrieve() == 3
    assert initial_proxy_address == upgraded_proxy_address
