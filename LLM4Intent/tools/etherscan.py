import os
import time

import requests


def get_contract_creation_from_etherscan(contract_address: str) -> dict:
    url = "https://api.etherscan.io/v2/api?chainid=1&module=contract&action=getcontractcreation&contractaddresses={contract_address}&apikey={API_KEY}".format(
        contract_address=contract_address, API_KEY=os.environ["ETHERSCAN_API_KEY"]
    )
    while True:
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(e)
            time.sleep(10)
            continue


def get_verified_contract_source_code_from_etherscan(contract_address: str) -> dict:
    url = "https://api.etherscan.io/v2/api?chainid=1&module=contract&action=getsourcecode&address={contract_address}&apikey={API_KEY}".format(
        contract_address=contract_address, API_KEY=os.environ["ETHERSCAN_API_KEY"]
    )
    while True:
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(e)
            time.sleep(10)
            continue


def get_verified_contract_abi_from_etherscan(contract_address: str) -> dict:
    url = "https://api.etherscan.io/v2/api?chainid=1&module=contract&action=getabi&address={contract_address}&apikey={API_KEY}".format(
        contract_address=contract_address, API_KEY=os.environ["ETHERSCAN_API_KEY"]
    )
    while True:
        try:
            response = requests.get(url)
            response.raise_for_status()
            result =  response.json()
            if int(result["status"]):
                return result["result"]
            else:
                return None
        except requests.exceptions.RequestException as e:
            print(e)
            time.sleep(10)
            continue
