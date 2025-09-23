from .contract_client import ContractClient
from src.utils.config import collateral_pool_path

class CollateralPool(ContractClient):
    def __init__(self, pool_address: str):
        super().__init__(collateral_pool_path, pool_address)

    def agentVault(self):
        return self.contract.functions.agentVault().call()
    
    def poolToken(self):
        return self.contract.functions.poolToken().call()

    def debtFreeTokensOf(self, address: str):
        return self.contract.functions.debtFreeTokensOf(address).call()
