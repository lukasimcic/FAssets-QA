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
    
    def debt_locked_tokens_of(self, address: str):
        return self.read("debtLockedTokensOf", [address])

    def enter(self, amount: int):
        return self.write("enter", value=amount)
    
    def exit(self, amount: int):
        return self.write("exit", [amount])

    def fasset_fees_of(self, address: str):
        return self.read("fassetFeesOf", [address])

    def withdraw_fees(self, fees: int):
        return self.write("withdrawFees", [fees])
    
    def total_collateral(self):
        return self.read("totalCollateral")
    
    def exit_collateral_ratio_bips(self):
        return self.read("exitCollateralRatioBIPS")

    def fAsset_fees_of(self, address: str):
        return self.read("fAssetFeesOf", [address])
