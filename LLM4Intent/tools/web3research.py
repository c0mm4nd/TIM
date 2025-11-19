from web3research import Web3Research
from web3research.common.types import Address, Hash
from web3research.evm import ContractDecoder, ERC20_ABI
from web3 import Web3
import os

w3r = Web3Research(api_token=os.getenv("W3R_API_KEY"))

ERC20_DECODER = ContractDecoder(Web3(), contract_abi=ERC20_ABI)


def get_address_transactions_within_block_number_range_from_web3research(
    address: str, start_block: int, end_block: int
):
    address = Address(address)
    txs = list(
        w3r.eth(backend=os.getenv("W3R_BACKEND")).transactions(
            where="from = {address} or to = {address} and blockNumber >= {start_block} and blockNumber <= {end_block}".format(
                address=address, start_block=start_block, end_block=end_block
            ),
            limit=None,
        )
    )

    return [
        {
            "hash": tx["hash"],
            "nonce": tx["nonce"],
            "from": tx["from"],
            "to": tx["to"],
            "value": tx["value"],
            "gas": tx["gas"],
            "gasPrice": tx["gasPrice"],
            "input": tx["input"],
            "blockNumber": tx["blockNumber"],
            "blockTimestamp": tx["blockTimestamp"],
            **(
                {"contractAddress": tx["contractAddress"]}
                if tx["contractAddress"] is not None
                else {}
            ),
        }
        for tx in txs
    ]


def get_transactions_from_address_within_block_number_range_from_web3research(
    address: str, start_block: int, end_block: int
):
    address = Address(address)
    txs = list(
        w3r.eth(backend=os.getenv("W3R_BACKEND")).transactions(
            where="from = {address} and blockNumber >= {start_block} and blockNumber <= {end_block}".format(
                address=address, start_block=start_block, end_block=end_block
            ),
            limit=None,
        )
    )

    return [
        {
            "hash": tx["hash"],
            "nonce": tx["nonce"],
            "from": tx["from"],
            "to": tx["to"],
            "value": tx["value"],
            "gas": tx["gas"],
            "gasPrice": tx["gasPrice"],
            "input": tx["input"],
            "blockNumber": tx["blockNumber"],
            "blockTimestamp": tx["blockTimestamp"],
            **(
                {"contractAddress": tx["contractAddress"]}
                if tx["contractAddress"] is not None
                else {}
            ),
        }
        for tx in txs
    ]


def get_transactions_to_address_within_block_number_range_from_web3research(
    address: str, start_block: int, end_block: int
):
    address = Address(address)
    txs = list(
        w3r.eth(backend=os.getenv("W3R_BACKEND")).transactions(
            where="to = {address} and blockNumber >= {start_block} and blockNumber <= {end_block}".format(
                address=address, start_block=start_block, end_block=end_block
            ),
            limit=None,
        )
    )

    # keep hash, nonce, from, to, value, input, gas, gasPrice, blockNumber, timestamp, contrac only

    return [
        {
            "hash": tx["hash"],
            "nonce": tx["nonce"],
            "from": tx["from"],
            "to": tx["to"],
            "value": tx["value"],
            "gas": tx["gas"],
            "gasPrice": tx["gasPrice"],
            "input": tx["input"],
            "blockNumber": tx["blockNumber"],
            "blockTimestamp": tx["blockTimestamp"],
            **(
                {"contractAddress": tx["contractAddress"]}
                if tx["contractAddress"] is not None
                else {}
            ),
        }
        for tx in txs
    ]


def get_address_token_transfers_within_block_number_range_from_web3research(
    address: str, start_block: int, end_block: int
):
    address = Hash("0x000000000000000000000000" + address.removeprefix("0x"))

    Transfer_topic = Hash(ERC20_DECODER.get_event_topic("Transfer"))
    event_logs = w3r.eth(backend=os.getenv("W3R_BACKEND")).events(
        where="topic0 = {Transfer_topic} and "
        " (topic1 = {address} or topic2 = {address}) "
        " and (blockNumber >= {start_block} and blockNumber <= {end_block})".format(
            Transfer_topic=Transfer_topic,
            address=address,
            start_block=start_block,
            end_block=end_block,
        ),
        limit=None,
    )
    decoded_event_logs = []
    for log in event_logs:
        decoded_log = ERC20_DECODER.decode_event_log("Transfer", log)
        del log["topics"]
        log["decoded"] = decoded_log
        decoded_event_logs.append(log)

    print(decoded_event_logs)

    return decoded_event_logs


def get_token_transfers_from_address_within_block_number_range_from_web3research(
    address: str, start_block: int, end_block: int
):
    address = Hash("0x000000000000000000000000" + address.removeprefix("0x"))

    Transfer_topic = Hash(ERC20_DECODER.get_event_topic("Transfer"))
    event_logs = w3r.eth(backend=os.getenv("W3R_BACKEND")).events(
        where="topic0 = {Transfer_topic} and "
        " topic1 = {address} "
        " and (blockNumber >= {start_block} and blockNumber <= {end_block})".format(
            Transfer_topic=Transfer_topic,
            address=address,
            start_block=start_block,
            end_block=end_block,
        ),
        limit=None,
    )
    decoded_event_logs = []
    for log in event_logs:
        decoded_log = ERC20_DECODER.decode_event_log("Transfer", log)
        del log["topics"]
        log["decoded"] = decoded_log
        decoded_event_logs.append(log)

    print(decoded_event_logs)

    return decoded_event_logs


def get_token_transfers_to_address_within_block_number_range_from_web3research(
    address: str, start_block: int, end_block: int
):
    address = Hash("0x000000000000000000000000" + address.removeprefix("0x"))

    Transfer_topic = Hash(ERC20_DECODER.get_event_topic("Transfer"))
    event_logs = w3r.eth(backend=os.getenv("W3R_BACKEND")).events(
        where="topic0 = {Transfer_topic} and "
        " topic2 = {address} "
        " and (blockNumber >= {start_block} and blockNumber <= {end_block})".format(
            Transfer_topic=Transfer_topic,
            address=address,
            start_block=start_block,
            end_block=end_block,
        ),
        limit=None,
    )
    decoded_event_logs = []
    for log in event_logs:
        decoded_log = ERC20_DECODER.decode_event_log("Transfer", log)
        del log["topics"]
        log["decoded"] = decoded_log
        decoded_event_logs.append(log)

    print(decoded_event_logs)

    return decoded_event_logs


def get_token_transfers_within_block_number_range_from_web3research(
    contract_address: str, start_block: int, end_block: int
):
    contract_address = Address(contract_address)

    Transfer_topic = Hash(ERC20_DECODER.get_event_topic("Transfer"))
    event_logs = w3r.eth(backend=os.getenv("W3R_BACKEND")).events(
        where="address = {contract_address} and topic0 = {Transfer_topic} "
        " and (blockNumber >= {start_block} and blockNumber <= {end_block})".format(
            Transfer_topic=Transfer_topic,
            contract_address=contract_address,
            start_block=start_block,
            end_block=end_block,
        ),
        limit=None,
    )
    decoded_event_logs = []
    for log in event_logs:
        decoded_log = ERC20_DECODER.decode_event_log("Transfer", log)
        del log["topics"]
        log["decoded"] = decoded_log
        decoded_event_logs.append(log)

    print(decoded_event_logs)

    return decoded_event_logs


def get_contract_events_within_block_number_range_from_web3research(
    contract_address: str, start_block: int, end_block: int
):
    contract_address = Address(contract_address)

    event_logs = w3r.eth(backend=os.getenv("W3R_BACKEND")).events(
        where="address = {contract_address} and blockNumber >= {start_block} and blockNumber <= {end_block}".format(
            contract_address=contract_address,
            start_block=start_block,
            end_block=end_block,
        ),
        limit=None,
    )
    print(event_logs)

    return event_logs
