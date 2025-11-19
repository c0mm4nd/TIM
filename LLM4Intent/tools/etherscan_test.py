from LLM4Intent.tools.etherscan import get_verified_contract_abi_from_etherscan


def test_get_verified_contract_abi_from_etherscan():
    abi_result = get_verified_contract_abi_from_etherscan("0xed0e416e0feea5b484ba5c95d375545ac2b60572") # Exploiter test, no ABI
    # {"status": "0", "message": "NOTOK", "result": "Contract source code not verified"}
    print("abi_result", abi_result)

    abi_result = get_verified_contract_abi_from_etherscan("0x06012c8cf97bead5deae237070f9587f8e7a266d") # CryptoKitties
    print("abi_result", abi_result)