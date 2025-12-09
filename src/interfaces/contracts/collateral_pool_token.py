from src.utils.data_structures import UserNativeData
from src.utils.fee_tracker import FeeTracker
from .contract_client import ContractClient
from config.config_qa import collateral_pool_token_path

class CollateralPoolToken(ContractClient):
    def __init__(
            self, 
            pool_address: str,
            sender_data: UserNativeData | None = None, 
            fee_tracker: FeeTracker | None = None
        ):
        super().__init__(collateral_pool_token_path, pool_address, sender_data, fee_tracker)

    def transfer(self, to_address, amount):
        self.write("transfer", inputs=[to_address, amount])

    def decimals(self):
        return self.read("decimals")

    def name(self):
        return self.read("name")
    
    def total_supply(self):
        return self.read("totalSupply")