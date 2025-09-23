from .contract_client import ContractClient
from src.utils.config import collateral_pool_token_path
from web3 import Web3

class CollateralPoolToken(ContractClient):
    def __init__(self, pool_address: str):
        super().__init__(collateral_pool_token_path, pool_address)

    def transfer(self, from_address, private_key, to_address, amount):
        # Build transaction
        gas = self.contract.functions.transfer(to_address, amount).estimate_gas({
            'from': from_address
        })
        tx = self.contract.functions.transfer(to_address, amount).build_transaction({
            'from': from_address,
            'nonce': self.web3.eth.get_transaction_count(from_address),
            'gas': gas,
            'gasPrice': self.web3.eth.gas_price,
        })
        # sign and send transaction
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(tx_hash.hex())
