from .contract_client import ContractClient
from src.utils.config import collateral_pool_token_path
from web3 import Web3

class CollateralPoolToken(ContractClient):
    def __init__(self, pool_address: str):
        super().__init__(collateral_pool_token_path, pool_address)

    def transfer(self, from_address, private_key, to_address, amount):
        tx = self.build_transaction(from_address, method="transfer", args=[to_address, amount])
        self.sign_and_send_transaction(tx, private_key)