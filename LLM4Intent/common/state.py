import json
from typing import Any, Dict, List, Mapping, Optional

from pydantic import BaseModel, Field
from web3 import Web3

from LLM4Intent.common.knowledge_base import MemoryGraph
from LLM4Intent.common.utils import convert_tool
from LLM4Intent.tools.etherscan import (
    get_contract_creation_from_etherscan,
    get_verified_contract_abi_from_etherscan,
    get_verified_contract_source_code_from_etherscan,
)
from LLM4Intent.tools.jsonrpc import (
    get_address_token_balance_at_block_number_from_jsonrpc,
    get_address_token_transfers_within_block_number_range_from_jsonrpc,
    get_address_eth_balance_at_block_number_from_jsonrpc,
    get_address_transactions_within_block_number_range_from_jsonrpc,
    get_contract_call_at_block_number_from_jsonrpc,
    # get_contract_basic_info_from_jsonrpc,
    get_contract_code_at_block_number_from_jsonrpc,
    get_contract_storage_at_block_number_from_jsonrpc,
    get_contract_token_transfers_within_block_number_range_from_jsonrpc,
    get_transaction_from_jsonrpc,
    get_transaction_receipt_from_jsonrpc,
    get_address_type_from_jsonrpc,
)

from LLM4Intent.tools.web2 import (
    extract_webpage_info_by_urls_from_tavily,
    get_contract_ABI_from_whatsabi,
    get_event_signatures_from_signature_database,
    get_function_signatures_from_signature_database,
    search_webpages_from_tavily
)
from web3research.evm import ContractDecoder
from web3research.evm.abi import ERC20_ABI

ERC20_DECODER = ContractDecoder(Web3(), ERC20_ABI)


class DataMissing(BaseModel):
    """The missing data of the analysis."""

    tool_name: str = Field(description=f"The name of the tool.")
    tool_args: Dict[str, Any] = Field(description="The arguments of the tool.")


class ContextCoverage(BaseModel):
    """The coverage of the context analysis."""

    EOA: int = Field(description="The coverage of the EOA addresses.")
    Contract: int = Field(description="The coverage of the Contract addresses.")
    Transactions: int = Field(description="The coverage of the Transactions.")


class ContextualSituation(BaseModel):
    """The contextual situation of the transaction."""

    external_market_conditions: str = Field(
        description="Market conditions during the transaction."
    )
    concensus_on_contract: str = Field(description="Consensus on the contract state.")


# on-chain knowledge-base
class State:
    def __init__(
        self,
        task: str,
        hierarchical_intents: Mapping,
        options: List[str],
    ):
        # const state
        self.task = task
        self.options = options

        # variable state
        self.last_speaker = "human"

        self.chat_history = [
            {
                "role": "user",
                "content": f"Please analyze the real intent behind the transaction with hash {self.task}",
            },
            {
                "role": "assistant",
                "content": f"Based on my knowledge, the intent is likely to fall into one of the following categories: {json.dumps(hierarchical_intents)}, I will proceed with the analysis by leveraging the appropriate tools.",
            },
        ]

        self.current_round = 0

        self.data_missing: List[DataMissing] = [
            DataMissing(
                tool_name="get_transaction_from_jsonrpc",
                tool_args={"transaction_hash": self.task},
            ),
            DataMissing(
                tool_name="get_transaction_receipt_from_jsonrpc",
                tool_args={"transaction_hash": self.task},
            ),
        ]

        self.last_analysis = None
        self.last_analysis_checked = False

        self.memory_graph = MemoryGraph()

        # as input args for an openai call
        self.openai_tools = [
            convert_tool(tool)
            for tool in [
                # JSON-RPC tools
                self.get_transaction_from_jsonrpc,
                self.get_transaction_receipt_from_jsonrpc,
                # self.get_transaction_trace_length_from_jsonrpc,
                # self.get_transaction_trace_with_index_range_from_jsonrpc,
                self.get_address_token_balance_at_block_number_from_jsonrpc,
                self.get_address_eth_balance_at_block_number_from_jsonrpc,
                self.get_address_token_transfers_within_block_number_range,
                self.get_address_transactions_within_block_number_range_from_jsonrpc,
                self.get_address_type_from_jsonrpc,
                # self.get_contract_basic_info_from_jsonrpc,
                self.get_contract_call_at_block_number_from_jsonrpc,
                self.get_contract_storage_at_block_number_from_jsonrpc,
                self.get_contract_code_at_block_number_from_jsonrpc,
                # Etherscan
                self.get_contract_creation_from_etherscan,
                self.get_verified_contract_abi_from_etherscan,
                self.get_verified_contract_source_code_from_etherscan,
                # Web2
                self.get_function_signatures_from_signature_database,
                self.get_contract_ABI_from_whatsabi,
                self.search_webpage_from_google,
                self.extract_webpage_info_by_urls,
                #
            ]
        ]

    def has_tool_called(self, tool_name, tool_args) -> bool:
        """Check if a tool has been called with specific arguments"""
        return any(
            any(
                tool_call.get("function", {}).get("name") == tool_name
                and json.loads(tool_call.get("function", {}).get("arguments", "{}"))
                == tool_args
                for tool_call in msg.get("tool_calls", [])
            )
            for msg in self.chat_history
        )

    ### tool mapping, with counting in state

    def get_transaction_from_jsonrpc(self, transaction_hash: str) -> Dict:
        """Retrieves transaction information from a JSON-RPC endpoint

        Args:
            transaction_hash: The hash of the transaction to retrieve

        Returns:
            dict: Transaction information
        """
        tx = get_transaction_from_jsonrpc(transaction_hash)
        self.memory_graph.add_transaction(tx)

        return tx

    def get_transaction_receipt_from_jsonrpc(
        self,
        transaction_hash: str,
    ) -> Dict:
        """Retrieves transaction receipt information (with event logs) from a JSON-RPC endpoint

        Args:
            transaction_hash: The hash of the transaction to retrieve receipt for

        Returns:
            dict: Transaction receipt information
        """
        return get_transaction_receipt_from_jsonrpc(transaction_hash)

    # def get_transaction_trace_length_from_jsonrpc(self, transaction_hash: str) -> int:
    #     """Retrieves transaction trace length from a JSON-RPC endpoint

    #     Args:
    #         transaction_hash: The hash of the transaction to retrieve trace length for

    #     Returns:
    #         int: Transaction trace length
    #     """
    #     return get_transaction_trace_length_from_jsonrpc(transaction_hash)

    # def get_transaction_trace_with_index_range_from_jsonrpc(
    #     self, transaction_hash: str, from_index: int, to_index: int
    # ) -> Dict:
    #     """Retrieves transaction trace information within an index range from a JSON-RPC endpoint

    #     Args:
    #         transaction_hash: The hash of the transaction to retrieve trace for
    #         from_index: Starting index
    #         to_index: Ending index, at most 50 traces can be retrieved at once, i.e. to_index <= from_index + 50

    #     Returns:
    #         Dict: Transaction trace information
    #     """
    #     if to_index > from_index + 50:
    #         raise ValueError("to_index must not exceed from_index + 50")

    #     return get_transaction_trace_with_index_range_from_jsonrpc(
    #         transaction_hash, from_index, to_index
    #     )

    def get_address_type_from_jsonrpc(self, address: str) -> str:
        """
        Retrieves the type (EOA or CA) of an address from a JSON-RPC endpoint

        Args:
            address: The Ethereum address to retrieve type for

        Returns:
            str: The type of the address, either "EOA" or "CA"
        """

        return get_address_type_from_jsonrpc(address)

    def get_address_eth_balance_at_block_number_from_jsonrpc(
        self, address: str, block_number: int
    ) -> str:
        """Retrieves ETH balance for an address at a specific block number

        Args:
            address: The Ethereum address to check balance for
            block_number: The block number to check balance at

        Returns:
            int: ETH balance in minimal units (e.g. wei)
        """
        return get_address_eth_balance_at_block_number_from_jsonrpc(address, block_number)

    def get_address_token_transfers_within_block_number_range(
        self, address: str, from_block: int, to_block: int
    ) -> List[Dict]:
        """Retrieves ERC20 token transfers for an address within a block number range

        Args:
            address: The address to get transfers for
            from_block: Starting block number
            to_block: Ending block number, at most 1000 blocks can be queried at once, i.e. to_block <= from_block + 1000

        Returns:
            List[Dict]: List of token transfer events
        """
        return get_address_token_transfers_within_block_number_range_from_jsonrpc(
            address, from_block, to_block
        )

    def get_address_transactions_within_block_number_range_from_jsonrpc(
        self, address: str, from_block: int, to_block: int
    ) -> List[Dict]:
        """Retrieves transactions for an address within a block number range

        Args:
            address: The address to get transactions for
            from_block: Starting block number
            to_block: Ending block number, at most 1000 blocks can be queried at once, i.e. to_block <= from_block + 1000

        Returns:
            List[Dict]: List of transactions
        """
        return get_address_transactions_within_block_number_range_from_jsonrpc(
            address, from_block, to_block
        )

    def get_address_token_balance_at_block_number_from_jsonrpc(
        self, token_address: str, address: str, block_number: int
    ) -> str:
        """Retrieves ERC20 token balance for an address at a specific block number

        Args:
            token_address: The address of the ERC20 token contract
            address: The address to check balance for
            block_number: The block number to check balance at

        Returns:
            int: Token balance in minimal units (e.g. wei for ETH)
        """
        return get_address_token_balance_at_block_number_from_jsonrpc(
            token_address, address, block_number
        )

    # def get_contract_basic_info_from_jsonrpc(self, contract_address: str) -> Dict:
    #     """Retrieves basic information about a smart contract

    #     Args:
    #         contract_address: The address of the smart contract

    #     Returns:
    #         Dict: Contract information
    #     """
    #     print(f"Calling get_contract_basic_info_from_jsonrpc with input:")
    #     print(f"contract_address: {contract_address}")

    #     try:
    #         result = get_contract_basic_info_from_jsonrpc(contract_address)
    #         print(f"Result: {result}")
    #         # if result.get("name") == "Not available":
    #         #     raise ValueError("Contract does not support ERC20 standard")
    #         return result
    #     except Exception as e:
    #         error_result = {"error": str(e)}
    #         print(f"Error occurred: {error_result}")
    #         return error_result

    def get_contract_call_at_block_number_from_jsonrpc(
        self, contract_address: str, data: str, block_number: int
    ) -> str:
        """Retrieves contract call data at a specific block number

        Args:
            contract_address: The address of the smart contract
            data: The data to send with the contract call
            block_number: The block number to get calls at

        Returns:
            str: Contract call data
        """
        return get_contract_call_at_block_number_from_jsonrpc(
            contract_address, data, block_number
        )

    def get_contract_code_at_block_number_from_jsonrpc(
        self, contract_address: str, block_number: int
    ) -> str:
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

    def get_contract_storage_at_block_number_from_jsonrpc(
        self, contract_address: str, storage_slot: str, block_number: int
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

    def get_contract_ERC20_token_transfers(
        self, contract_address: str, from_block: int, to_block: int
    ) -> List[Dict]:
        """Retrieves ERC20 token transfers for a contract within a block number range

        Args:
            contract_address: The address of the ERC20 token contract
            from_block: Starting block number
            to_block: Ending block number, at most 1000 blocks can be queried at once, i.e. to_block <= from_block + 1000

        Returns:
            List[Dict]: List of token transfer events
        """
        return (
            get_contract_token_transfers_within_block_number_range_from_jsonrpc(
                contract_address, from_block, to_block
            )
        )

    """-------------etherscan-------------"""

    def get_contract_creation_from_etherscan(self, contract_address: str) -> dict:
        """Retrieves contract creation information from Etherscan

        Args:
            contract_address: The Ethereum contract address to get creation info for

        Returns:
            dict: Contract creation information including creator address and transaction details
        """
        return get_contract_creation_from_etherscan(contract_address)

    def get_verified_contract_source_code_from_etherscan(
        self, contract_address: str
    ) -> dict:
        """Retrieves verified contract source code from Etherscan

        Args:
            contract_address: The Ethereum contract address to get source code for

        Returns:
            dict: Contract source code and related metadata
        """
        return get_verified_contract_source_code_from_etherscan(contract_address)

    def get_verified_contract_abi_from_etherscan(self, contract_address: str) -> dict:
        """Retrieves verified contract ABI from Etherscan

        Args:
            contract_address: The Ethereum contract address to get ABI for

        Returns:
            dict: Contract ABI in JSON format
        """
        return get_verified_contract_abi_from_etherscan(contract_address)

    """-------------database-------------"""

    def get_function_signatures_from_signature_database(
        self, hex_signature: str
    ) -> str:
        """Retrieves function signature text from signature databases using a hex signature

        Args:
            hex_signature: The hex signature of the function to look up

        Returns:
            dict: The possible text signature of the function if found
        """
        return get_function_signatures_from_signature_database(hex_signature)

    def get_contract_ABI_from_whatsabi(self, contract_address: str) -> dict:
        """Retrieves contract ABI from WhatsABI

        Args:
            contract_address: The Ethereum contract address to get ABI for

        Returns:
            dict: Contract ABI in JSON format
        """
        return get_contract_ABI_from_whatsabi(contract_address)

    def get_event_signatures_from_signature_database(self, hex_signature: str) -> str:
        """Retrieves event signature text from signature databases using a hex signature

        Args:
            hex_signature: The hex signature of the event to look up

        Returns:
            dict: The possible text signature of the event if found
        """
        return get_event_signatures_from_signature_database(hex_signature)

    def search_webpage_from_google(self, query: str):
        """retrieves webpage urls from google with the query

        Args:
            query: The query string to search for

        Returns:
            dict: The search result
        """
        result = search_webpages_from_tavily(query)

        return result

    def extract_webpage_info_by_urls(self, urls: List[str]) -> dict:
        """retrieves webpage information by urls

        Args:
            urls: List of urls to extract information from

        Returns:
            dict: The extracted information
        """

        result = extract_webpage_info_by_urls_from_tavily(urls)

        return result
