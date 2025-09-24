from src.utils.config import rpc_url
from src.utils.contracts import get_contract_abi
from web3 import Web3
from web3.middleware import geth_poa_middleware


class ContractClient:
    def __init__(self, contract_path: str, contract_address: str, timeout: int | None = None):
        self.path = contract_path
        self.name = contract_address
        
        kwargs = {}
        if timeout is not None:
            kwargs['timeout'] = timeout
        self.web3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs=kwargs))
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        assert self.web3.is_connected()
        contract_abi = get_contract_abi(contract_path)
        self.contract = self.web3.eth.contract(contract_address, abi=contract_abi)

    def build_transaction(self, from_address: str, method: str, args: list = [], value: int = 0):
        nonce = self.web3.eth.get_transaction_count(from_address)
        gas = self.contract.functions[method](*args).estimate_gas({
            'from': from_address,
            'value': value
        })
        gas_price = self.web3.eth.gas_price
        tx = self.contract.functions[method](*args).build_transaction({
            'from': from_address,
            'nonce': nonce,
            'gas': gas,
            'gasPrice': gas_price,
            'value': value
        })
        return tx

    def sign_and_send_transaction(self, tx, private_key):
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        self.web3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_hash
    
    
