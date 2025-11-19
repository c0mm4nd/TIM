import json
import logging
import os
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
    get_type_hints,
)
from langchain_core.utils.function_calling import convert_to_openai_tool
from pydantic import BaseModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Dictionary to store file handlers for different transaction hashes
transaction_handlers = {}


def get_logger(name: str, transaction_hash: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not os.path.exists("logs"):
        os.makedirs("logs")

    log_file = os.path.join("logs", f"{transaction_hash}.log")

    # Check if we already have a handler for this transaction
    if transaction_hash not in transaction_handlers:
        # Create new handler for this transaction
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        transaction_handlers[transaction_hash] = handler

    # Check if this logger already has the transaction-specific handler
    has_transaction_handler = any(
        handler is transaction_handlers[transaction_hash] for handler in logger.handlers
    )

    # Add transaction-specific handler if not already present
    if not has_transaction_handler:
        logger.addHandler(transaction_handlers[transaction_hash])

    return logger

def convert_tool(tool: Callable) -> Dict[str, Any]:
    if tool is None:
        raise ValueError("Tool cannot be None")

    schema = convert_to_openai_tool(
        tool,
        # strict=True, # Not supported by Grok
    )
    return schema


def try_validate_json(base: BaseModel, data: str):
    try:
        return base.model_validate_json(data)
    except ValueError as e:
        try:
            return base(**json.loads(data))
        except Exception as json_error:
            raise ValueError("Invalid JSON data") from json_error
            
