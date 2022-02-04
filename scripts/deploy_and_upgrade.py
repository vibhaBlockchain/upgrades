from webbrowser import get
from brownie import (
    config,
    Box,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    network,
    Contract,
    BoxV2,
)
from scripts.helpful_scripts import get_account, encode_function_data, upgrade


def main():
    account = get_account()
    print(f"Deploying to {network.show_active()}")
    box = Box.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print(box.retrieve())
    ## The box we just created is the implementation contract, we will be hooking this up to a proxy

    ## Having Proxy admin multi-signosis safe
    # Optional deploy ProxyAdmin and use that as the admin contract
    proxy_admin = ProxyAdmin.deploy({"from": account})

    ## Instead of having a constructor we call the initializer function the instant we deploy our contract
    # If we want an initallizer function we can add `initializer=box.store, 1`
    # to simulate initializer being teh store function
    # with newValue of 1

    # box_encoded_initializer_function = encode_function_data()
    box_encoded_initializer_function = encode_function_data(box.store, 1)
    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        # account.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print(f"Proxy deployed to {proxy}! You can now upgrade it to BoxxV2")
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    print(f"Here is the initial value in Box {proxy_box.retrieve()}")

    box_v2 = BoxV2.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    # box_v2_encoded_initialzer_function = encode_function_data(box_v2.store, 1)
    upgrade_transaction = upgrade(
        account, proxy, box_v2.address, proxy_admin, box_v2.store, 5
    )

    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    proxy_box.increment({"from": account})
    print(f"Incremented value: {proxy_box.retrieve()}")
