from src.interfaces.contracts import *
from src.utils.config import fdc_url, da_url, x_csrftoken
from src.utils.encoding import to_utf8_hex_string

from typing import Literal
import requests
import json
import time


class Attestation():
    def __init__(self, token_underlying : Literal["testXRP"], user_native_data, user_underlying_data, indexer_api_key):
        self.token_underlying = token_underlying
        self.contract_inputs = {
            "sender_address": user_native_data["address"],
            "sender_private_key": user_native_data["private_key"]
        }
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "X-API-KEY": indexer_api_key,
            'X-CSRFTOKEN': x_csrftoken
        }

    # utility functions

    def _generate_fdc_url(self, endpoint, attestation_type=None):
        if self.token_underlying == "testXRP":
            token_underlying = "xrp"
        else:
            raise ValueError(f"Unsupported token_underlying: {self.token_underlying}")
        if attestation_type is None:
            return f"{fdc_url}/verifier/{token_underlying}/api/indexer/{endpoint}"
        else:
            return f"{fdc_url}/verifier/{token_underlying}/{attestation_type}/{endpoint}"
        
    def _generate_source_id(self, attestation_type : Literal["Payment"]):
        if attestation_type == "Payment":
            return to_utf8_hex_string(self.token_underlying)
        else:
            raise ValueError(f"Unsupported attestation type: {attestation_type}")

    def _generate_attestation_type(self, attestation_type):
        return to_utf8_hex_string(attestation_type)
        
    def _get_transaction_id(self, tx_hash):
        url_transaction = self._generate_fdc_url("transaction")
        response = requests.get(url_transaction + f'/{tx_hash}', headers=self.headers).json()
        for _ in range(5):
            if response['status'] == 'ERROR':
                time.sleep(10)
                response = requests.get(url_transaction + f'/{tx_hash}', headers=self.headers).json()
            else:
                return response['data']['transactionId']
        raise ValueError("Transaction not found or still pending after multiple attempts")
        
    def _current_round_id(self):
        response = requests.get(da_url + '/api/v0/fsp/status').json()
        return response["latest_fdc"]["voting_round_id"]

    # core functionality

    def prepare_attestation_request(self, tx_hash, attestation_type : Literal["Payment"]):
        """
        Prepares an attestation request to the FDC.
        Returns response data.
        """
        data = {
            "attestationType": self._generate_attestation_type(attestation_type),
            "sourceId": self._generate_source_id(attestation_type),
            "requestBody": {
                "transactionId": self._get_transaction_id(tx_hash),
                "inUtxo": "0",
                "utxo": "0"
            }
        }
        response = requests.post(
            url=self._generate_fdc_url("prepareRequest", attestation_type),
            headers=self.headers,
            data=json.dumps(data)
        )
        return response.json()

    def submit_attestation_request(self, abi_encoded_request):
        """
        Sends a payment attestation request to the FDC.
        Returns round id.
        """
        frfc = FdcRequestFeeConfigurations(**self.contract_inputs)
        required_fee = frfc.get_request_fee(abi_encoded_request)
        fh = FdcHub(**self.contract_inputs)
        block_number = fh.request_attestation(abi_encoded_request, required_fee)
        r = Relay(**self.contract_inputs)
        round_id = r.get_voting_round_id(block_number)
        return round_id

    def get_proof(self, abi_encoded_request, round_id):
        """
        Retrieves the proof from the DA.
        Returns response data.
        """
        for _ in range(10):
            time.sleep(5)
            if self._current_round_id() >= round_id:
                break
        response = {}
        for _ in range(20):
            if len(response.get("proof", [])) == 0:
                time.sleep(15)
                response = requests.post(
                    url=da_url + "/api/v0/fdc/get-proof-round-id-bytes",
                    headers=self.headers,
                    data=json.dumps({
                        "votingRoundId": round_id,
                        "requestBytes": abi_encoded_request
                    })
                )
                response = response.json()
            else:
                return response
        raise ValueError("Proof not found after multiple attempts")

        










    