from typing import List, TypedDict
from .intent_defination import Intent

Transaction = TypedDict(
    "Transaction",
    {
        "hash": str,
        "blockHash": str,
        "blockNumber": int,
        "blockTimestamp": int,
        "transactionIndex": int,
        "chainId": int,
        "type": int,
        "from": str,
        "to": str,
        "value": int,
        "nonce": int,
        "input": str,
        "gas": int,
        "gasPrice": int,
        "maxFeePerGas": int,
        "maxPriorityFeePerGas": int,
        "r": str,
        "s": str,
        "v": int,
        "accessList": List,
        "contractAddress": str,
        "cumulativeGasUsed": int,
        "effectiveGasPrice": int,
        "gasUsed": int,
        "logsBloom": str,
        "root": str,
        "status": int,
    },
)


class EventLog(TypedDict):
    address: str
    blockHash: str
    blockNumber: int
    blockTimestamp: int
    transactionHash: str
    transactionIndex: int
    logIndex: int
    removed: bool
    topics: list
    data: str


class Trace(TypedDict):
    blockPos: int
    blockNumber: int
    blockTimestamp: int
    blockHash: str
    transactionHash: str
    traceAddress: list
    subtraces: int
    transactionPosition: int
    error: str
    actionType: str
    actionCallFrom: str
    actionCallTo: str
    actionCallValue: int
    actionCallInput: str
    actionCallGas: int
    actionCallType: str
    actionCreateFrom: str
    actionCreateValue: int
    actionCreateInit: str
    actionCreateGas: int
    actionSuicideAddress: str
    actionSuicideRefundAddress: str
    actionSuicideBalance: int
    actionRewardAuthor: str
    actionRewardValue: int
    actionRewardType: str
    resultType: str
    resultCallGasUsed: int
    resultCallOutput: str
    resultCreateGasUsed: int
    resultCreateCode: str
    resultCreateAddress: str


class TransactionWithLogsTraces(Transaction):
    logs: list[EventLog]
    traces: list[Trace]

class UserContext(TypedDict):
    pass

class ContractContext(TypedDict):
    pass

# class FlowContext(TypedDict):