from .contract_client import ContractClient
from src.utils.config import collateral_pool_token_path

class CollateralPoolToken(ContractClient):
    def __init__(self, sender_address: str, sender_private_key: str, pool_address: str):
        super().__init__(sender_address, sender_private_key, collateral_pool_token_path, pool_address)

    def transfer(self, to_address, amount):
        self.write("transfer", inputs=[to_address, amount])