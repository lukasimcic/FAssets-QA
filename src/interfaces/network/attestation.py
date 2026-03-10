import functools
from typing import TYPE_CHECKING, Literal, Optional
import random
import requests
import json
import time
from src.interfaces.network.tokens import TokenUnderlying
from src.interfaces.contracts import *
from src.utils.encoding import pad_right_to_64_hex, to_utf8_hex_string, keccak256_text
if TYPE_CHECKING:
    from src.flow.fee_tracker import FeeTracker
    from src.interfaces.network.networks.native_networks.native_network import NativeNetwork
    from src.utils.data_structures import UserCredentials


def retry_on_exception(max_attempts=20, min_wait=10, max_wait=15):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise RuntimeError("Failed after multiple attempts. Most recent error: " + str(e))
                    time.sleep(random.uniform(min_wait, max_wait))
        return wrapper
    return decorator

class Attestation():
    def __init__(
            self, 
            native_network: "NativeNetwork", 
            token_underlying: "TokenUnderlying", 
            user_native_credentials: "UserCredentials", 
            indexer_api_key: str, 
            fee_tracker: Optional["FeeTracker"]  = None
        ):
        self.native_network = native_network
        self.token_underlying = token_underlying
        self.contract_inputs = {
            "network": native_network,
            "sender_credentials": user_native_credentials,
            "fee_tracker": fee_tracker
        }
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "X-API-KEY": indexer_api_key
        }

    # utility functions

    def _generate_fdc_url(self, endpoint: str, attestation_type: Optional[str]  = None):
        if self.token_underlying == TokenUnderlying.testXRP:
            token_underlying = "xrp"
        if attestation_type is None:
            return f"{self.native_network.fdc_url()}/verifier/{token_underlying}/api/indexer/{endpoint}"
        else:
            return f"{self.native_network.fdc_url()}/verifier/{token_underlying}/{attestation_type}/{endpoint}"
        
    def _generate_source_id(self) -> str:
        return to_utf8_hex_string(self.token_underlying.name)
        
    def _generate_attestation_type(self, attestation_type: str) -> str:
        return to_utf8_hex_string(attestation_type)
        
    @retry_on_exception()
    def _get_transaction_id(self, tx_hash: str) -> str:
        url_transaction = self._generate_fdc_url("transaction")
        response = requests.get(url_transaction + f'/{tx_hash}', headers=self.headers).json()
        return response['data']['transactionId']
        
    @retry_on_exception()
    def _current_round_id(self) -> int:
        response = requests.get(self.native_network.da_url() + '/api/v0/fsp/status').json()
        return response["latest_fdc"]["voting_round_id"]

    def request_body_payment(self, tx_hash: str) -> dict:
        return {
            "transactionId": self._get_transaction_id(tx_hash),
            "inUtxo": "0",
            "utxo": "0"
        }
    
    def request_body_referenced_payment_nonexistence(
            self,
            destination_address: str,
            payment_reference: str,
            amount: int,
            first_block: int,
            last_block: int,
            last_timestamp: int
            ) -> dict:
        return {
            "minimalBlockNumber": str(first_block),
            "deadlineBlockNumber": str(last_block),
            "deadlineTimestamp": str(last_timestamp),
            "destinationAddressHash": keccak256_text(destination_address),
            "amount": str(amount),
            "standardPaymentReference": pad_right_to_64_hex(payment_reference),
            "checkSourceAddresses": False,
            "sourceAddressesRoot": "0x" + "00" * 32
        }

    # core functionality

    def prepare_attestation_request(self, request_body: dict, attestation_type : Literal["Payment", "ReferencedPaymentNonexistence"]) -> dict:
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

    def submit_attestation_request(self, abi_encoded_request: bytes) -> int:
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

    def get_proof(self, abi_encoded_request: bytes, round_id: int) -> dict:
        """
        Retrieves the proof from the DA.
        Returns response data.
        """
        for _ in range(10):
            time.sleep(15)
            if self._current_round_id() >= round_id:
                break
        response = {}
        for _ in range(40):
            if len(response.get("proof", [])) == 0:
                time.sleep(15)
                response = requests.post(
                    url=self.native_network.da_url() + "/api/v0/fdc/get-proof-round-id-bytes",
                    headers=self.headers,
                    data=json.dumps({
                        "votingRoundId": round_id,
                        "requestBytes": abi_encoded_request
                    })
                )
                if response.status_code == 200:
                    response = response.json()
                else:
                    response = {}
            else:
                return response
        raise ValueError("Proof not found after multiple attempts")

    def get_block_range(self) -> tuple[int, int]:
        """
        Retrieves the range of available confirmed blocks in the indexer database.
        Returns (first_block, last_block).
        """
        url_transaction = self._generate_fdc_url("block-range")
        response = requests.get(url_transaction, headers=self.headers).json()
        return response['data']['first'], response['data']['last']










    