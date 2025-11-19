import json
from LLM4Intent.tools.jsonrpc import *
from LLM4Intent.tools.web2 import get_contract_ABI_from_whatsabi

vitalik_EOA_address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
WETH_contract_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"


# decorator to check if the function returns a jsonable object
def check_jsonable(result):
    assert json.dumps(result)


def test_get_transaction_from_jsonrpc() -> str:
    check_jsonable(
        get_transaction_from_jsonrpc(
            "0x43a2cb2a2a4fa683a67db6f828d2db99e1253a33a8eb1032915e50f71d85a9f0"
        )
    )


def test_get_transaction_receipt_from_jsonrpc() -> str:
    check_jsonable(
        get_transaction_receipt_from_jsonrpc(
            "0x43a2cb2a2a4fa683a67db6f828d2db99e1253a33a8eb1032915e50f71d85a9f0"
        )
    )


def test_get_transaction_trace_from_jsonrpc() -> int:
    check_jsonable(
        get_transaction_trace_from_jsonrpc(
            "0x43a2cb2a2a4fa683a67db6f828d2db99e1253a33a8eb1032915e50f71d85a9f0"
        )
    )

    print(
        "tx has",
        get_transaction_trace_from_jsonrpc(
            "0x43a2cb2a2a4fa683a67db6f828d2db99e1253a33a8eb1032915e50f71d85a9f0"
        ),
        "trace(s)",
    )


def test_get_address_eth_balance_at_block_number_from_json() -> int:
    check_jsonable(
        get_address_eth_balance_at_block_number_from_jsonrpc(
            vitalik_EOA_address, 20_000_000
        )
    )


# def test_get_address_transactions_within_block_number_range_from_jsonrpc() -> str:
#     check_jsonable(
#         get_address_transactions_within_block_number_range_from_jsonrpc(
#             vitalik_EOA_address, 20_000_000 - 10, 20_000_000
#         )
#     )


# def test_get_address_ERC20_token_balance_at_block_number_from_jsonrpc() -> int:
#     check_jsonable(
#         get_address_token_balance_at_block_number_from_jsonrpc(
#             vitalik_EOA_address, WETH_contract_address, 20_000_000
#         )
#     )


# def test_get_address_ERC20_token_transfers_within_block_number_range_from_jsonrpc() -> (
#     str
# ):
#     check_jsonable(
#         get_address_token_transfers_within_block_number_range_from_jsonrpc(
#             vitalik_EOA_address, 20_000_000 - 10, 20_000_000
#         )
#     )


# def test_get_address_ERC721_NFT_transfers_within_block_number_range_from_jsonrpc() -> (
#     str
# ):
#     check_jsonable(get_address_ERC721_NFT_transfers_within_block_number_range_from_jsonrpc(
#         vitalik_EOA_address, 20_000_000 - 10, 20_000_000
#     )


# def test_get_address_ERC1155_NFT_single_transfers_within_block_number_range_from_jsonrpc() -> (
#     str
# ):
#     check_jsonable((
#         get_address_ERC1155_NFT_single_transfers_within_block_number_range_from_jsonrpc(
#             vitalik_EOA_address, 20_000_000 - 10, 20_000_000
#         )
#     )


# def test_get_address_ERC1155_NFT_batch_transfers_within_block_number_range_from_jsonrpc() -> (
#     str
# ):
#     check_jsonable((
#         get_address_ERC1155_NFT_batch_transfers_within_block_number_range_from_jsonrpc(
#             vitalik_EOA_address, 20_000_000 - 10, 20_000_000
#         )
#     )


def test_get_contract_code_at_block_number_from_jsonrpc() -> str:
    check_jsonable(
        get_contract_code_at_block_number_from_jsonrpc(vitalik_EOA_address, 20_000_000)
    )


def test_get_contract_storage_at_block_number_from_jsonrpc() -> str:
    check_jsonable(
        get_contract_storage_at_block_number_from_jsonrpc(
            WETH_contract_address, 0, 20_000_000
        )
    )


# def test_get_contract_events_within_block_number_range_from_jsonrpc() -> str:
#     check_jsonable(
#         get_contract_events_within_block_number_range_from_jsonrpc(
#             WETH_contract_address, 20_000_000 - 10, 20_000_000
#         )
#     )


# def test_get_contract_ERC20_token_transfers_within_block_number_range_from_jsonrpc() -> (
#     str
# ):
#     check_jsonable(
#         get_contract_token_transfers_within_block_number_range_from_jsonrpc(
#             WETH_contract_address, 20_000_000 - 10, 20_000_000
#         )
#     )


# def test_get_contract_ERC721_NFT_transfers_within_block_number_range_from_jsonrpc() -> (
#     str
# ):
#     check_jsonable(get_contract_ERC721_NFT_transfers_within_block_number_range_from_jsonrpc(
#         WETH_contract_address, 20_000_000 - 10, 20_000_000
#     )


# def test_get_contract_ERC1155_NFT_single_transfers_within_block_number_range_from_jsonrpc() -> (
#     str
# ):
#     check_jsonable(get_contract_ERC1155_NFT_single_transfers_within_block_number_range_from_jsonrpc(
#         WETH_contract_address, 20_000_000 - 10, 20_000_000
#     )


# def test_get_contract_ERC1155_NFT_batch_transfers_within_block_number_range_from_jsonrpc() -> (
#     str
# ):
#     check_jsonable((
#         get_contract_ERC1155_NFT_batch_transfers_within_block_number_range_from_jsonrpc(
#             WETH_contract_address, 20_000_000 - 10, 20_000_000
#         )
#     )


def test_get_contract_basic_info_from_jsonrpc() -> str:
    check_jsonable(
        get_contract_basic_info_from_jsonrpc(
            "0x47293Fe9dE5546A2D3Fc44F52a1C383075cDcd62", 22_000_000
        )
    )

    contract_basic_info = get_contract_basic_info_from_jsonrpc(
        "0x47293Fe9dE5546A2D3Fc44F52a1C383075cDcd62", 22_000_000
    )
    print(contract_basic_info)

    assert contract_basic_info["name"] == "ELON MARS"
    assert contract_basic_info["symbol"] == "ELONMARS"
    assert contract_basic_info["decimals"] == 9
    assert contract_basic_info["owner"] == "0x" + "0" * 40
    assert contract_basic_info["total_supply"] == 420000000000000000000000

def test_get_contract_basic_info_from_jsonrpc_1() -> str:
    check_jsonable(
        get_contract_basic_info_from_jsonrpc(
            "0x9Ed15383940CC380fAEF0a75edacE507cC775f22", 22_000_000
        )
    )

    contract_basic_info = get_contract_basic_info_from_jsonrpc(
        "0x9Ed15383940CC380fAEF0a75edacE507cC775f22", 22_000_000
    )
    print(contract_basic_info)

    assert contract_basic_info["name"] == "Swell Earn ETH"
    assert contract_basic_info["symbol"] == "earnETH"

def test_get_contract_basic_info_from_jsonrpc_2() -> str:
    check_jsonable(
        get_contract_basic_info_from_jsonrpc(
            "0xf079d7911c13369E7fd85607970036D2883aFcfD", 20_000_000
        )
    )

    contract_basic_info = get_contract_basic_info_from_jsonrpc(
        "0xf079d7911c13369E7fd85607970036D2883aFcfD", 20_000_000
    )
    print(contract_basic_info)


def test_get_contract_ABI_from_whatsabi() -> str:
    abi_result = get_contract_ABI_from_whatsabi(
        "0x47293Fe9dE5546A2D3Fc44F52a1C383075cDcd62"
    )
    print(abi_result)
    check_jsonable(abi_result)


def test_get_transaction_time_from_jsonrpc() -> str:
    time = get_transaction_time_from_jsonrpc(
        "0x43a2cb2a2a4fa683a67db6f828d2db99e1253a33a8eb1032915e50f71d85a9f0"
    )
    print(time)
    check_jsonable(time)

