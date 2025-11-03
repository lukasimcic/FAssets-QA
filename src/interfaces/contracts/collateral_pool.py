from .contract_client import ContractClient
from config.config_qa import collateral_pool_path

class CollateralPool(ContractClient):
    def __init__(self, sender_address: str, sender_private_key: str, pool_address: str):
        super().__init__(sender_address, sender_private_key, collateral_pool_path, pool_address)

    def agent_vault(self):
        return self.read("agentVault")
    
    def pool_token(self):
        return self.read("poolToken")

    def debt_free_tokens_of(self, address: str):
        return self.read("debtFreeTokensOf", [address])
