from src.interfaces.contracts import *
from config.config_qa import x_csrftoken
from src.utils.encoding import pad_to_64_hex, to_utf8_hex_string, keccak256_text
from src.utils.data_structures import TokenNative, TokenUnderlying

from typing import Literal
import requests
import json
import time


class Attestation():
    def __init__(self, token_native: TokenNative, token_underlying: TokenUnderlying, user_native_data, indexer_api_key, fee_tracker=None):
        self.token_native = token_native
        self.token_underlying = token_underlying
        self.contract_inputs = {
            "token_native": token_native,
            "sender_data": user_native_data,
            "fee_tracker": fee_tracker
        }
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "X-API-KEY": indexer_api_key,
            'X-CSRFTOKEN': x_csrftoken
        }

    # utility functions

    def _generate_fdc_url(self, endpoint, attestation_type=None):
        if self.token_underlying == TokenUnderlying.testXRP:
            token_underlying = "xrp"
        if attestation_type is None:
            return f"{self.token_native.fdc_url}/verifier/{token_underlying}/api/indexer/{endpoint}"
        else:
            return f"{self.token_native.fdc_url}/verifier/{token_underlying}/{attestation_type}/{endpoint}"
        
    def _generate_source_id(self):
        return to_utf8_hex_string(self.token_underlying.name)
        
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
        response = requests.get(self.token_native.da_url + '/api/v0/fsp/status').json()
        return response["latest_fdc"]["voting_round_id"]

    def request_body_payment(self, tx_hash):
        return {
            "transactionId": self._get_transaction_id(tx_hash),
            "inUtxo": "0",
            "utxo": "0"
        }
    
    def request_body_referenced_payment_nonexistence(
            self,
            destination_address,
            payment_reference,
            amount,
            first_block,
            last_block,
            last_timestamp
            ):
        return {
            "minimalBlockNumber": str(first_block),
            "deadlineBlockNumber": str(last_block),
            "deadlineTimestamp": str(last_timestamp),
            "destinationAddressHash": keccak256_text(destination_address),
            "amount": str(amount),
            "standardPaymentReference": pad_to_64_hex(payment_reference),
            "checkSourceAddresses": False,
            "sourceAddressesRoot": "0x" + "00" * 32
        }

    # core functionality

    def prepare_attestation_request(self, request_body, attestation_type : Literal["Payment", "ReferencedPaymentNonexistence"]):
        """
        Prepares an attestation request to the FDC.
        Returns response data.
        """
        data = {
            "attestationType": self._generate_attestation_type(attestation_type),
            "sourceId": self._generate_source_id(),
            "requestBody": request_body
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
                    url=self.token_native.da_url + "/api/v0/fdc/get-proof-round-id-bytes",
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

    def get_block_range(self):
        """
        Retrieves the range of available confirmed blocks in the indexer database.
        Returns (first_block, last_block).
        """
        url_transaction = self._generate_fdc_url("block-range")
        response = requests.get(url_transaction, headers=self.headers).json()
        return response['data']['first'], response['data']['last']










    