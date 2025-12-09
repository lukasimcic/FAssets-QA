from src.utils.data_structures import UserNativeData
from src.utils.fee_tracker import FeeTracker
from .contract_client import ContractClient
from config.config_qa import collateral_pool_path

class CollateralPool(ContractClient):
    def __init__(
            self, 
            pool_address: str, sender_data: UserNativeData | None = None, 
            fee_tracker: FeeTracker | None = None
        ):
        super().__init__(collateral_pool_path, pool_address, sender_data, fee_tracker)

    def agent_vault(self):
        return self.read("agentVault")
    
    def pool_token(self):
        return self.read("poolToken")

    def debt_free_tokens_of(self, address: str):
        return self.read("debtFreeTokensOf", [address])
    
    def debt_locked_tokens_of(self, address: str):
        return self.read("debtLockedTokensOf", [address])

    def enter(self, amount: int):
        return self.write("enter", value=amount)["events"]
    
    def exit(self, amount: int):
        return self.write("exit", [amount])["events"]

    def fasset_fees_of(self, address: str):
        return self.read("fassetFeesOf", [address])

    def withdraw_fees(self, fees: int):
        return self.write("withdrawFees", [fees])["events"]
    
    def total_collateral(self):
        return self.read("totalCollateral")
    
    def exit_collateral_ratio_bips(self):
        return self.read("exitCollateralRatioBIPS")

    def fAsset_fees_of(self, address: str):
        return self.read("fAssetFeesOf", [address])
