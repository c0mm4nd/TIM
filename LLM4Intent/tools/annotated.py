import json
from typing import Dict, List
from datetime import datetime
import requests
import tiktoken


from LLM4Intent.tools.etherscan import (
    get_verified_contract_abi_from_etherscan,
    get_verified_contract_source_code_from_etherscan,
    get_contract_creation_from_etherscan,
)

from LLM4Intent.tools.jsonrpc import (
    get_address_token_balance_at_block_number_from_jsonrpc,
    get_address_eth_balance_at_block_number_from_jsonrpc,
    get_contract_basic_info_from_jsonrpc,
    get_contract_code_at_block_number_from_jsonrpc,
    get_contract_storage_at_block_number_from_jsonrpc,
    get_transaction_from_jsonrpc,
    get_transaction_receipt_from_jsonrpc,
    get_transaction_time_from_jsonrpc,
    get_transaction_trace_from_jsonrpc,
)
from LLM4Intent.tools.web2 import (
    extract_webpage_info_by_urls_from_tavily,
    get_address_labels_from_blocksec,
    get_address_labels_from_github_repo,
    get_contract_ABI_from_whatsabi,
    get_function_signatures_from_signature_database,
    get_event_signatures_from_signature_database,
    search_webpages_from_tavily,
)
from LLM4Intent.tools.web3research import (
    get_address_token_transfers_within_block_number_range_from_web3research,
    get_address_transactions_within_block_number_range_from_web3research,
    get_contract_events_within_block_number_range_from_web3research,
    get_token_transfers_from_address_within_block_number_range_from_web3research,
    get_token_transfers_to_address_within_block_number_range_from_web3research,
    get_token_transfers_within_block_number_range_from_web3research,
    get_transactions_from_address_within_block_number_range_from_web3research,
    get_transactions_to_address_within_block_number_range_from_web3research,
)


"""-------------jsonrpc-------------"""


def get_transaction(transaction_hash: str) -> Dict:
    """Retrieves transaction information from a JSON-RPC endpoint

    Args:
        transaction_hash: The hash of the transaction to retrieve

    Returns:
        Dict: Transaction information
    """
    return get_transaction_from_jsonrpc(transaction_hash)


def get_transaction_receipt(transaction_hash: str) -> Dict:
    """Retrieves transaction receipt information from a JSON-RPC endpoint

    Args:
        transaction_hash: The hash of the transaction to retrieve receipt for

    Returns:
        Dict: Transaction receipt information
    """
    return get_transaction_receipt_from_jsonrpc(transaction_hash)


def get_transaction_trace(transaction_hash: str) -> Dict:
    """Retrieves transaction trace information from a JSON-RPC endpoint

    Args:
        transaction_hash: The hash of the transaction to retrieve trace for

    Returns:
        Dict: Transaction trace information
    """
    return get_transaction_trace_from_jsonrpc(transaction_hash)


def get_address_eth_balance_at_block_number(address: str, block_number: int) -> str:
    """Retrieves ETH balance for an address at a specific block number

    Args:
        address: The Ethereum address to check balance for
        block_number: The block number to check balance at

    Returns:
        str: ETH balance in wei
    """
    return get_address_eth_balance_at_block_number_from_jsonrpc(address, block_number)


def get_address_token_transfers_within_block_number_range(
    address: str, from_block: int, to_block: int
) -> List[Dict]:
    """Retrieves ERC20 token transfers for an address within a block number range

    Args:
        address: The address to get transfers for
        from_block: Starting block number
        to_block: Ending block number, at most 1000 blocks can be queried at once, i.e. to_block <= from_block + 1000

    Returns:
        List[Dict]: List of token transfer events
    """
    return get_address_token_transfers_within_block_number_range_from_web3research(
        address, from_block, to_block
    )


def get_token_transfers_from_address_within_block_number_range(
    address: str, start_block: int, end_block: int
) -> List[Dict]:
    """Retrieves ERC20 token transfers from an address within a block number range

    Args:
        address: The address to get transfers from
        start_block: Starting block number
        end_block: Ending block number

    Returns:
        List[Dict]: List of token transfer events
    """
    return get_token_transfers_from_address_within_block_number_range_from_web3research(
        address, start_block, end_block
    )


def get_token_transfers_to_address_within_block_number_range(
    address: str, start_block: int, end_block: int
) -> List[Dict]:
    """Retrieves ERC20 token transfers to an address within a block number range

    Args:
        address: The address to get transfers to
        start_block: Starting block number
        end_block: Ending block number

    Returns:
        List[Dict]: List of token transfer events
    """
    return get_token_transfers_to_address_within_block_number_range_from_web3research(
        address, start_block, end_block
    )


def get_address_transactions_within_block_number_range(
    address: str, from_block: int, to_block: int
) -> List[Dict]:
    """Retrieves transactions for an address within a block number range

    Args:
        address: The address to get transactions for
        from_block: Starting block number
        to_block: Ending block number, at most 1000 blocks can be queried at once, i.e. to_block <= from_block + 1000

    Returns:
        List[Dict]: List of transactions
    """
    return get_address_transactions_within_block_number_range_from_web3research(
        address, from_block, to_block
    )


def get_transactions_from_address_within_block_number_range(
    address: str, start_block: int, end_block: int
) -> List[Dict]:
    """Retrieves transactions from an address within a block number range

    Args:
        address: The address to get transactions from
        start_block: Starting block number
        end_block: Ending block number

    Returns:
        List[Dict]: List of transactions
    """
    return get_transactions_from_address_within_block_number_range_from_web3research(
        address, start_block, end_block
    )


def get_transactions_to_address_within_block_number_range(
    address: str, start_block: int, end_block: int
) -> List[Dict]:
    """Retrieves transactions to an address within a block number range

    Args:
        address: The address to get transactions to
        start_block: Starting block number
        end_block: Ending block number

    Returns:
        List[Dict]: List of transactions
    """
    return get_transactions_to_address_within_block_number_range_from_web3research(
        address, start_block, end_block
    )


def get_address_token_balance_at_block_number(
    token_address: str, address: str, block_number: int
) -> str:
    """Retrieves ERC20 token balance for an address at a specific block number

    Args:
        token_address: The address of the ERC20 token contract
        address: The address to check balance for
        block_number: The block number to check balance at

    Returns:
        str: Token balance
    """
    return get_address_token_balance_at_block_number_from_jsonrpc(
        address, token_address, block_number
    )


def get_contract_basic_info(contract_address: str, block_number: int) -> Dict:
    """Retrieves basic information about a smart contract

    Args:
        contract_address: The address of the smart contract
        block_number: The block number to get contract info at

    Returns:
        Dict: Contract information
    """
    print(f"Calling get_contract_basic_info_from_jsonrpc with input:")
    print(f"contract_address: {contract_address}")

    try:
        result = get_contract_basic_info_from_jsonrpc(contract_address, block_number)
        print(f"Result: {result}")
        # if result.get("name") == "Not available":
        #     raise ValueError("Contract does not support ERC20 standard")
        return result
    except Exception as e:
        error_result = {"error": str(e)}
        print(f"Error occurred: {error_result}")
        return error_result


def get_contract_events_within_block_number_range(
    contract_address: str, from_block: int, to_block: int
) -> List[Dict]:
    """Retrieves events for a smart contract within a block number range

    Args:
        contract_address: The address of the smart contract
        from_block: Starting block number
        to_block: Ending block number, at most 1000 blocks can be queried at once, i.e. to_block <= from_block + 1000

    Returns:
        List[Dict]: List of events (not decoded)
    """
    return get_contract_events_within_block_number_range_from_web3research(
        contract_address, from_block, to_block
    )


def get_contract_code_at_block_number(contract_address: str, block_number: int) -> str:
    """Retrieves contract bytecode at a specific block number

    Args:
        contract_address: The address of the smart contract
        block_number: The block number to get code at

    Returns:
        str: Contract bytecode
    """
    return get_contract_code_at_block_number_from_jsonrpc(
        contract_address, block_number
    )


def get_contract_storage_at_block_number(
    contract_address: str, storage_slot: str, block_number: int
) -> str:
    """Retrieves contract storage data at a specific block number

    Args:
        contract_address: The address of the smart contract
        storage_slot: The storage slot to read
        block_number: The block number to get storage at

    Returns:
        str: Storage data
    """
    return get_contract_storage_at_block_number_from_jsonrpc(
        contract_address, storage_slot, block_number
    )


def get_token_transfers_within_block_number_range(
    erc20_contract_address: str, from_block: int, to_block: int
) -> List[Dict]:
    """Retrieves ERC20 token transfers for a token contract within a block number range

    Args:
        erc20_contract_address: The address of the ERC20 token contract
        from_block: Starting block number
        to_block: Ending block number, at most 1000 blocks can be queried at once, i.e. to_block <= from_block + 1000

    Returns:
        List[Dict]: List of token transfer events
    """
    return get_token_transfers_within_block_number_range_from_web3research(
        erc20_contract_address, from_block, to_block
    )


"""-------------etherscan-------------"""


def get_contract_creation(contract_address: str) -> dict:
    """Retrieves contract creation information (creator, and creation transaction) from Etherscan

    Args:
        contract_address: The Ethereum contract address to get creation info for

    Returns:
        dict: Contract creation information including creator address and transaction details
    """
    return get_contract_creation_from_etherscan(contract_address)


def get_contract_source_code(contract_address: str) -> dict:
    """Retrieves verified contract source code from Etherscan

    Args:
        contract_address: The Ethereum contract address to get source code for

    Returns:
        dict: Contract source code and related metadata
    """
    return get_verified_contract_source_code_from_etherscan(contract_address)


"""-------------database-------------"""


def get_function_signature(contract_address: str, hex_signature: str) -> str:
    """Retrieves function signature text from signature databases using a hex signature
    When the function signature is not found in the database, it returns None, and suggests to use the ABI data instead.

    Args:
        contract_address: The Ethereum contract address to look up function signature for
        hex_signature: The hex signature of the function to look up

    Returns:
        str: The text signature of the function if found, None otherwise
    """
    sig = get_function_signatures_from_signature_database(hex_signature)
    if sig:
        return sig

    abi = get_contract_ABI(contract_address)
    if not abi:
        print("No ABI found for contract address:", contract_address)
        return None

    response = requests.post(
        "http://evmlookup.web3resear.ch/api/keccak256/submit", json={"abi": abi}
    )
    response.raise_for_status()

    signatures = response.json()
    for signature in signatures:
        if signature["hex"] == hex_signature:
            return [signature]

    print(
        f"FAILED to find function signature for {hex_signature} in contract {contract_address}"
    )
    return None


def get_event_signature(contract_address: str, hex_signature: str) -> str:
    """Retrieves event signature text from signature databases using a hex signature
    When the function signature is not found in the database, it returns None, and suggests to use the ABI data instead.

    Args:
        contract_address: The Ethereum contract address to get event signature for
        hex_signature: The hex signature of the event to look up

    Returns:
        str: The text signature of the event if found, None otherwise
    """
    sig = get_event_signatures_from_signature_database(hex_signature)
    if sig:
        return sig

    abi = get_contract_ABI(contract_address)
    if not abi:
        print("No ABI found for contract address:", contract_address)
        return None

    response = requests.post(
        "http://evmlookup.web3resear.ch/api/keccak256/submit", json={"abi": abi}
    )
    response.raise_for_status()

    signatures = response.json()
    for signature in signatures:
        if signature["hex"] == hex_signature:
            return [signature]

    print(
        f"FAILED to find function signature for {hex_signature} in contract {contract_address}"
    )
    return None


def get_contract_ABI(contract_address: str) -> dict:
    """Retrieves contract ABI from signature databases

    Args:
        contract_address: The Ethereum contract address to get ABI for

    Returns:
        dict: Contract ABI in JSON format
    """

    abi = get_verified_contract_abi_from_etherscan(contract_address)
    if not abi:
        abi = get_contract_ABI_from_whatsabi(contract_address)

    return abi


def search_webpages(query: str) -> dict:
    """
    Searches the web for a given query using Google and returns the response.

    Args:
        query: The search query string to be used in the Google search.

    Returns:
        dict: The response from the Google search.
    """
    response = search_webpages_from_tavily(query)
    return response


def extract_webpage_info_by_urls(urls: List[str]) -> dict:
    """
    Extracts information from webpages using Browser agent and returns the response.

    Args:
        urls: A list of URLs to extract information from.

    Returns:
        dict: The response from the Browser extraction agent.
    """
    response = extract_webpage_info_by_urls_from_tavily(urls)
    return response


def get_address_label(address: str) -> list[dict]:
    """Retrieves the label for an Ethereum address, return empty list if not found
    When the label is not found, suggest to use other methods to refer the label

    Args:
        address: The Ethereum address to get the label for

    Returns:
        list[dict]: The labels for the address
    """

    etherscan_labels = get_address_labels_from_github_repo(address)
    # blocksec_labels = get_address_labels_from_blocksec([address])[0]

    # return {
    #     "etherscan_labels": etherscan_labels,
    #     "private_labels": blocksec_labels,
    # }
    return etherscan_labels


def get_transaction_time(transaction_hash: str) -> str:
    """Retrieves the time of the transaction (in UTC) from the transaction data

    Args:
        transaction_hash: The hash of the transaction to retrieve time for

    Returns:
        str: The time of the transaction
    """
    return get_transaction_time_from_jsonrpc(transaction_hash)
