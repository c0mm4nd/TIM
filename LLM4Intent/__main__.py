# %%
import os
import json
import concurrent.futures
from typing import Any, Dict, List, Mapping, Optional, Tuple
from dotenv import load_dotenv
from openai import Client, OpenAI
import argparse

from web3 import Web3
from web3research import Web3Research

from LLM4Intent.common.utils import get_logger
from LLM4Intent.roles.domain_expert import DomainExpertAnalyst
from LLM4Intent.roles.meta_controller import MetaController
from LLM4Intent.roles.stateless_checker import StatelessChecker
from LLM4Intent.roles.question_solver import QuestionSolverAnalyst
from LLM4Intent.roles.stateless_scorer import StatelessScorer

from LLM4Intent.tools.annotated import *

# 加载环境变量
load_dotenv()

# 初始化 OpenAI 客户端
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 默认模型配置
DEFAULT_MODEL_NAME = (
    "grok-3-mini-beta"  # "openai/gpt-4o-mini"  # 根据需要替换为实际模型，例如 "gpt-4o"
)
SUMMARIZING_MODEL_NAME = "gpt-4o-mini"
THINKING_MODEL_NAME = "gpt-4o-mini"
TOKEN_LIMIT = 128000  # 根据模型调整


# %%


def collect_fact(transaction_hash: str):
    transaction = get_transaction_from_jsonrpc(transaction_hash)
    receipt = get_transaction_receipt_from_jsonrpc(transaction_hash)
    to_address = transaction["to"]
    from_address = transaction["from"]
    fact = {
        **transaction,
        **receipt,
        "from_label": get_address_label(from_address),
        "to_label": get_address_label(to_address),
    }

    return fact


# %%
def workflow(transaction_hash: str, hierarchical_intents: Mapping):

    logger = get_logger("Workflow", transaction_hash)
    logger.warning(f"Analyzing transaction: {transaction_hash}")

    all_available_tools = [
        get_transaction,
        get_transaction_receipt,
        get_transaction_trace,  # maybe too large for some model
        get_address_label,
        get_address_transactions_within_block_number_range,
        get_address_eth_balance_at_block_number,
        get_address_token_balance_at_block_number,
        get_address_token_transfers_within_block_number_range,
        get_contract_code_at_block_number,
        get_contract_storage_at_block_number,
        get_token_transfers_within_block_number_range,
        get_contract_creation,
        get_contract_ABI,
        get_contract_basic_info,
        get_contract_source_code,
        get_contract_code_at_block_number,
        get_function_signature,
        get_event_signature,
        get_transaction_time,
        search_webpages,
        extract_webpage_info_by_urls,
    ]

    meta_controller = MetaController(DEFAULT_MODEL_NAME, client, transaction_hash)
    meta_plan = meta_controller.build_meta_plan(all_available_tools)
    domain_experts = [
        DomainExpertAnalyst(
            DEFAULT_MODEL_NAME,
            client,
            transaction_hash=transaction_hash,
            perspective=perspective.name,
            tips=perspective.prompt
            + "\nTIPs:\n"
            + "\n- ".join(perspective.tips)
            + "\nTOOL SUGGESTIONS:\n"
            + "\n- ".join(perspective.tool_suggestions),
        )
        for perspective in meta_plan.perspectives
    ]

    transaction_fact = collect_fact(transaction_hash)

    main_analyst_reports = {}

    def run_expert(expert: DomainExpertAnalyst) -> Tuple[str, str]:
        plan = expert.breakdown(transaction_hash)

        chat_histories = []
        for todo in plan.items:
            breakdown_question, item_prompt = todo.question, todo.prompt
            sub_analyst = QuestionSolverAnalyst(
                DEFAULT_MODEL_NAME,
                client,
                transaction_hash=transaction_hash,
                known_facts=transaction_fact,
                main_perspective=expert.perspective,
                tools=all_available_tools,
            )

            chat_histories = sub_analyst.analyze(
                chat_histories, breakdown_question, prompt=item_prompt
            )

        analyzed_intent = expert.analyze(hierarchical_intents, chat_histories)
        return expert.perspective, analyzed_intent

    # Execute analyzers in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(run_expert, expert): expert for expert in domain_experts
        }
        for future in concurrent.futures.as_completed(futures):
            perspective, analyzed_intent = future.result()
            main_analyst_reports[perspective] = analyzed_intent

    checker = StatelessChecker(DEFAULT_MODEL_NAME, client, transaction_hash)
    check_report = checker.check(
        transaction_hash, hierarchical_intents, main_analyst_reports
    )

    logger.info("check_report {}".format(check_report))

    scorer = StatelessScorer(DEFAULT_MODEL_NAME, client, transaction_hash)
    final_report = scorer.score(
        transaction_hash, main_analyst_reports, check_report, hierarchical_intents
    )

    logger.warning("Final report: {}".format(final_report))

    return {
        "perspective_reports": main_analyst_reports,
        "check_report": check_report,
        "final_report": final_report,
    }


def start():
    # read config from argparser
    parser = argparse.ArgumentParser(description="LLM4Intent")
    parser.add_argument("--pwd", type=str, default=".")
    parser.add_argument("--config", type=str, default="config.json")
    parser.add_argument("--openai-api-key", type=str)
    parser.add_argument("--openai-base-url", type=str)

    args = parser.parse_args()

    # read config from file
    config = json.load(open(args.config))

    hierarchical_intents = json.load(open("intent_cat.json"))
    # set working directory
    if args.pwd != ".":
        if not os.path.exists(args.pwd):
            os.makedirs(args.pwd)
        print(f"Creating directory: {args.pwd}")
    else:
        print(f"Using current directory: {os.getcwd()}")

    # read transactions from the file
    txs = config.get("txs", []) + config.get("tfs", [])

    # change working directory
    os.chdir(args.pwd)
    print(f"Working directory: {os.getcwd()}")

    # overwrite env variables
    if args.openai_api_key:
        os.environ["OPENAI_API_KEY"] = args.openai_api_key
    if args.openai_base_url:
        os.environ["OPENAI_API_BASE"] = args.openai_base_url

    for transaction_hash in txs:
        if os.path.exists(os.path.join("score_reports", f"{transaction_hash}.output.md")):
            print(f"Transaction {transaction_hash} already analyzed.")
            continue
        workflow(transaction_hash, hierarchical_intents)


def sample():
    # read config from argparser
    parser = argparse.ArgumentParser(description="LLM4Intent")
    parser.add_argument("--contract", type=str, required=True)
    parser.add_argument("--txs", type=int, default=100)
    parser.add_argument("--tfs", type=int, default=100)
    parser.add_argument("--final", type=int, default=5)
    args = parser.parse_args()

    contract = args.contract
    contract = Web3.to_checksum_address(contract)
    print(contract)

    txs_limit = args.txs
    tfs_limit = args.tfs
    final_limit = args.final

    # directly use clickhouse sampling
    w3r = Web3Research(api_token=os.getenv("W3R_API_KEY"))
    eth = w3r.ethereum(backend=os.getenv("W3R_BACKEND"))

    txs = []
    if tfs_limit > 0:
        txs += [
            "0x" + result["hash"].lower()
            for result in list(
                eth.query(
                    f"SELECT hex(transactionHash) as hash, count(logIndex) as cnt FROM ethereum.events WHERE topic0 = unhex('ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef') AND address = unhex('{contract.removeprefix("0x")}') GROUP BY transactionHash HAVING cnt > 0 ORDER BY rand() LIMIT {tfs_limit}"
                ).named_results()
            )
        ]

    if txs_limit > 0:
        txs += [
            "0x" + result["hash"].lower()
            for result in list(
                eth.query(
                    f"SELECT hex(hash) as hash FROM ethereum.transactions WHERE to = unhex('{contract.removeprefix("0x")}') ORDER BY rand() LIMIT {txs_limit}"
                ).named_results()
            )
        ]

    print(f"Got {len(txs)} transactions")

    import random

    txs = random.sample(txs, min(final_limit, len(txs)))

    hierarchical_intents = json.load(open("intent_cat.json"))

    for transaction_hash in txs:
        workflow(transaction_hash, hierarchical_intents)

    print(f"Sampled transactions: {txs}")


# Run with fastapi
def serve():
    import uvicorn
    from fastapi import FastAPI

    app = FastAPI()

    @app.get("/")
    async def read_root():
        return {"Hello": "World"}

    @app.get("/start")
    async def read_item():
        return {"status": "success"}

    uvicorn.run(app, host="0.0.0.0", port=58000)


# demo with gradio
def demo():
    import gradio as gr

    hierarchical_intents = json.load(open("intent_cat.json"))

    def analyze(transaction_hash: str):
        return workflow(transaction_hash, hierarchical_intents)

    gr.Interface(
        fn=analyze,
        inputs="text",
        outputs="json",
        title="LLM4Intent",
        description="Recognize the intent of the transaction",
    ).launch(share=True)


if __name__ == "__main__":
    start()
