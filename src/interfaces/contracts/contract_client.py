from src.utils.contracts import get_contract_abi
from src.utils.fee_tracker import FeeTracker
from src.utils.data_structures import TokenNative, UserNativeData
from web3 import Web3
from web3.middleware import geth_poa_middleware
import warnings
import time


class ContractClient:
    def __init__(
            self, 
            token_native: TokenNative,
            contract_path: str, 
            contract_address: str, 
            sender_data: UserNativeData | None = None,
            fee_tracker: FeeTracker | None = None,
            timeout: int | None = None
        ):
        self.token_native = token_native
        self.sender_data = sender_data
        self.sender_address = sender_data.address if sender_data else None
        self.sender_private_key = sender_data.private_key if sender_data else None
        self.path = contract_path
        self.address = contract_address
        self.fee_tracker = fee_tracker
        
        kwargs = {}
        if timeout is not None:
            kwargs['timeout'] = timeout
        self.web3 = Web3(Web3.HTTPProvider(self.token_native.rpc_url, request_kwargs=kwargs))
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        assert self.web3.is_connected()
        contract_abi = get_contract_abi(contract_path)
        self.contract = self.web3.eth.contract(contract_address, abi=contract_abi)

    def _build_transaction(self, method: str, args: list = [], value: int = 0):
        nonce = self.web3.eth.get_transaction_count(self.sender_address)
        gas = self.contract.functions[method](*args).estimate_gas({
            'from': self.sender_address,
            'value': value
        })
        gas_price = self.web3.eth.gas_price
        tx = self.contract.functions[method](*args).build_transaction({
            'from': self.sender_address,
            'nonce': nonce,
            'gas': gas,
            'gasPrice': gas_price,
            'value': value
        })
        return tx

    def _sign_and_send_transaction(self, tx):
        """
        Signs and sends a transaction to the blockchain.
        Returns any event outputs.
        """
        signed_tx = self.web3.eth.account.sign_transaction(tx, self.sender_private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt
    
    def _get_events_from_receipt(self, receipt, events: list):
        """
        Extracts events from a transaction receipt.
        """
        result = {}
        for event_name in events:
            event_obj = getattr(self.contract.events, event_name, None)
            if event_obj is None:
                raise ValueError(f"Event {event_name} not found in contract.")
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message=".*MismatchedABI.*It has been discarded.*",
                    category=UserWarning,
                    module="web3.contract.base_contract"
                )
                events = event_obj().process_receipt(receipt)
            if events:
                result[event_name] = [e['args'] for e in events]
            else:
                result[event_name] = []
        return result
    
    def write(self, method: str, inputs: list = [], events: list = [], value: int = 0):
        time.sleep(0.5)
        tx = self._build_transaction(method, inputs, value)
        receipt = self._sign_and_send_transaction(tx)
        events = self._get_events_from_receipt(receipt, events)
        fees = receipt.gasUsed * getattr(receipt, 'effectiveGasPrice', tx['gasPrice'])
        self.fee_tracker.native_gas_fees += self.token_native.from_uba(fees)
        return {"receipt": receipt, "events": events}
    
    def read(self, method: str, inputs: list = []):
        time.sleep(0.5)
        return self.contract.functions[method](*inputs).call()

    
    
