from LLM4Intent.tools.web3research import (
    get_address_transactions_within_block_number_range_from_web3research,
    get_address_token_transfers_within_block_number_range_from_web3research,
)
from LLM4Intent.tools.jsonrpc_test import check_jsonable
import os
import dotenv

dotenv.load_dotenv()


def test_get_address_transactions_within_block_number_range():
    print(os.getenv("W3R_BACKEND"))

    txs = get_address_transactions_within_block_number_range_from_web3research(
        "0xcd212c13967b957eb728f25484d3f66b0650ffe1", 0, 22000000
    )
    assert txs is not None
    check_jsonable(txs)


def test_get_address_token_transfers_within_block_number_range():
    print(os.getenv("W3R_BACKEND"))
    tfs = get_address_token_transfers_within_block_number_range_from_web3research(
        "0xcd212c13967b957eb728f25484d3f66b0650ffe1", 0, 22000000
    )
    assert tfs is not None
    check_jsonable(tfs)
