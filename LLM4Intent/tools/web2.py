import os
from typing import List
import requests
from tavily import TavilyClient
from web3 import Web3

from LLM4Intent.tools.etherscan import get_verified_contract_abi_from_etherscan

# Step 1. Instantiating your TavilyClient
tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))


def search_webpages_from_tavily(query) -> dict:
    response = tavily_client.search(query)

    print("Search Response:", response)

    return response


def extract_webpage_info_by_urls_from_tavily(urls: List[str]) -> dict:
    response = tavily_client.extract(urls)

    print("Extract Response:", response)

    return response


def get_function_signatures_from_signature_database(hex_signature: str) -> dict:
    response = requests.get(
        "https://evmlookup.vercel.app/api/keccak256/function?query={query}".format(
            query=hex_signature
        )
    )
    result = response.json()

    return result["data"]


def get_event_signatures_from_signature_database(hex_signature: str) -> dict:
    response = requests.get(
        "https://evmlookup.vercel.app/api/keccak256/event?query={query}".format(
            query=hex_signature
        )
    )
    result = response.json()

    return result["data"]


def get_contract_ABI_from_whatsabi(contract_address: str) -> dict:
    url = f"https://evmlookup.web3resear.ch/api/whatsabi?contract={contract_address}"
    result = requests.get(url).json()
    # other things other than ABI can be obtained from the result:
    # - proxies
    # - hasCode
    # - isFactory
    # - abiLoadedFrom
    return result.get("data", {}).get("abi")


def get_address_labels_from_github_repo(address: str) -> list:
    address = Web3.to_checksum_address(address)
    url = f"https://eth-labels-production.up.railway.app/labels/{address}"

    response = requests.get(url)

    # [{"address":"0x4838b106fce9647bdf1e7877bf73ce8b0bad5f97","chainId":1,"label":"mev-builder","nameTag":"Titan Builder"}]

    return response.json()


def get_address_impl_labels_from_blocksec(addresses: List[str]) -> list:
    addresses = [Web3.to_checksum_address(address) for address in addresses]
    url = "https://extension.blocksec.com/api/v1/address/impl-label"

    response = requests.post(
        url,
        json={"chain": "eth", "addresses": addresses},
        headers={
            "Accept": "application/json",
            "Origin": "chrome-extension://fkhgpeojcbhimodmppkbbliepkpcgcoo",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        },
    )

    # [
    #   {
    #     "address": "0x01D26f8c5cC009868A4BF66E268c17B057fF7A73",
    #     "chain": "eth",
    #     "chainId": 1,
    #     "label": "Proxy_01d2_7a73",
    #     "logo": "",
    #     "implementAddress": "0x34cfac646f301356faa8b21e94227e3583fe3f5f",
    #     "implementLabel": "Safe: Mastercopy 1.1.1"
    #   }
    # ]

    return response.json()


def get_address_labels_from_blocksec(addresses: List[str]) -> list:
    if isinstance(addresses, str):
        addresses = [addresses]

    addresses = [Web3.to_checksum_address(address) for address in addresses]
    url = "https://extension.blocksec.com/api/v1/address-label"

    response = requests.post(
        url,
        json={"chain": "eth", "addresses": addresses},
        headers={
            "Accept": "application/json",
            "Origin": "chrome-extension://fkhgpeojcbhimodmppkbbliepkpcgcoo",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        },
    )

    print("Response:", response.text)

    # [
    #   {
    #     "address": "0x01D26f8c5cC009868A4BF66E268c17B057fF7A73",
    #     "label": "Proxy_01d2_7a73",
    #     "logo": "",
    #     "risk": 0,
    #     "chain": "eth",
    #     "chainId": 1
    #   },
    #   {
    #     "address": "0x1111111254EEB25477B68fb85Ed929f73A960582",
    #     "label": "Aggregation Router V5",
    #     "logo": "",
    #     "risk": 0,
    #     "chain": "eth",
    #     "chainId": 1
    #   },
    #   {
    #     "address": "0xfCFBcfc4f5A421089e3Df45455F7f4985FE2D6a8",
    #     "label": "EthereumFeeProxy",
    #     "logo": "",
    #     "risk": 0,
    #     "chain": "eth",
    #     "chainId": 1
    #   },
    #   {
    #     "address": "0x1111111254fb6c44bAC0beD2854e76F90643097d",
    #     "label": "1inch v4: Aggregation Router",
    #     "logo": "",
    #     "risk": 0,
    #     "chain": "eth",
    #     "chainId": 1
    #   },
    #   {
    #     "address": "0x76E2cFc1F5Fa8F6a5b3fC4c8F4788F0116861F9B",
    #     "label": "Safe: Proxy Factory 1.1.1",
    #     "logo": "",
    #     "risk": 0,
    #     "chain": "eth",
    #     "chainId": 1
    #   }
    # ]

    return response.json()


def get_address_risk_score_from_blocksec(address: str, labels: List[str], nameTag: str, creator: str) -> list:
    address = Web3.to_checksum_address(address)
    url = "https://extension.blocksec.com/api/v1/address-risk-score"

    response = requests.post(
        url,
        json={
            "chain": "eth",
            "address": address,
            "addressLabel": {"labels": labels, "nameTag": nameTag},
            "creator": creator,
        },
        headers={
            "Accept": "application/json",
            "Origin": "chrome-extension://fkhgpeojcbhimodmppkbbliepkpcgcoo",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        },
    )

    #     {
    #   "address": "0x01d26f8c5cc009868a4bf66e268c17b057ff7a73",
    #   "risk": 2,
    #   "riskDetailInfo": {
    #     "riskType": "",
    #     "riskItems": null,
    #     "overallRisk": 0
    #   }
    # }

    return response.json()


def get_address_funder_scores_from_blocksec(address: str) -> list:
    address = Web3.to_checksum_address(address)
    url = "https://extension.blocksec.com/api/v1/address-funder-risk"

    response = requests.post(
        url,
        json={"chain": "eth", "address": address},
        headers={
            "Accept": "application/json",
            "Origin": "chrome-extension://fkhgpeojcbhimodmppkbbliepkpcgcoo",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        },
    )

    #     {
    #     "address": "0x72d5306c01ee1178f35c369afa725c7b90ce345b",
    #     "label": "0x72d530...90ce345b",
    #     "risky": false
    #     }

    return response.json()


def get_token_market_list_from_blocksec(address: str) -> list:
    # assume the token is ERC20, get the (defi) market info
    address = Web3.to_checksum_address(address)
    url = "https://extension.blocksec.com/api/v1/token-market/list"

    response = requests.post(
        url,
        json={"chain": "eth", "address": address},
        headers={
            "Accept": "application/json",
            "Origin": "chrome-extension://fkhgpeojcbhimodmppkbbliepkpcgcoo",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        },
    )

    # {
    #   "tokenType": "ERC20",
    #   "markets": [
    #     {
    #       "name": "uniswap",
    #       "url": "https://app.uniswap.org/#/swap?outputCurrency=0x01d26f8c5cc009868a4bf66e268c17b057ff7a73"
    #     },
    #     {
    #       "name": "sushiswap",
    #       "url": "https://www.sushi.com/swap?token1=0x01d26f8c5cc009868a4bf66e268c17b057ff7a73"
    #     }
    #   ]
    # }

    return response.json()


def get_contract_upgrades_from_blocksec(address: str) -> dict:
    # assume the token is ERC20, get the (defi) market info
    address = Web3.to_checksum_address(address)
    url = "https://extension.blocksec.com/api/v1/contract/upgrades"

    response = requests.post(
        url,
        json={"chain": "eth", "address": address},
        headers={
            "Accept": "application/json",
            "Origin": "chrome-extension://fkhgpeojcbhimodmppkbbliepkpcgcoo",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        },
    )

    return response.json()

def get_approve_risk_from_blocksec(address: str) -> dict:
    address = Web3.to_checksum_address(address)
    url = "https://extension.blocksec.com/api/v1/approve-risk"

    response = requests.post(
        url,
        json=[{"chain": "eth", "address": address}], # can be a list of (chain, address)
        headers={
            "Accept": "application/json",
            "Origin": "chrome-extension://fkhgpeojcbhimodmppkbbliepkpcgcoo",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        },
    )

    return response.json()

def get_private_variable_list_from_blocksec(address: str) -> dict:
    address = Web3.to_checksum_address(address)
    url = "https://extension.blocksec.com/api/v1/private-variable/list"

    response = requests.post(
        url,
        json=[{"chain": "eth", "address": address}], # can be a list of (chain, address)
        headers={
            "Accept": "application/json",
            "Origin": "chrome-extension://fkhgpeojcbhimodmppkbbliepkpcgcoo",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        },
    )

    return response.json()

def get_private_variable_query_from_blocksec(address: str) -> dict:
    address = Web3.to_checksum_address(address)
    url = "https://extension.blocksec.com/api/v1/private-variable/query"

    response = requests.post(
        url,
        json=[{"chain": "eth", "address": address}], # can be a list of (chain, address)
        headers={
            "Accept": "application/json",
            "Origin": "chrome-extension://fkhgpeojcbhimodmppkbbliepkpcgcoo",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        },
    )

    return response.json()

def get_private_variable_query_from_blocksec(address: str) -> dict:
    address = Web3.to_checksum_address(address)
    url = "https://extension.blocksec.com/api/v1/fund-flow"

    response = requests.post(
        url,
        json={"chain": "eth", "address": address},
        headers={
            "Accept": "application/json",
            "Origin": "chrome-extension://fkhgpeojcbhimodmppkbbliepkpcgcoo",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        },
    )



    return response.json()

def get_address_method_from_blocksec(hex_signatures: List[str]) -> dict:
    url = "https://extension.blocksec.com/api/v1/address-method"

    response = requests.post(
        url,
        json={"codeHash": hex_signatures}, # can be a list of (chain, address)
        headers={
            "Accept": "application/json",
            "Origin": "chrome-extension://fkhgpeojcbhimodmppkbbliepkpcgcoo",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        },
    )

    return response.json()