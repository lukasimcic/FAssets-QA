from src.utils.data_structures import TokenNative, UserNativeData
from src.utils.fee_tracker import FeeTracker
from .contract_client import ContractClient
from config.config_qa import collateral_pool_token_path

class CollateralPoolToken(ContractClient):
    def __init__(
            self, 
            token_native: TokenNative,
            pool_address: str,
            sender_data: UserNativeData | None = None, 
            fee_tracker: FeeTracker | None = None
        ):
        super().__init__(token_native, collateral_pool_token_path, pool_address, sender_data, fee_tracker)

    def transfer(self, to_address, amount):
        self.write("transfer", inputs=[to_address, amount])

    def decimals(self):
        return self.read("decimals")
    
    def to_uba(self, amount: float) -> int:
        decimals = self.decimals()
        return int(amount * 10 ** decimals)
    
    def from_uba(self, amount_uba: int) -> float:
        decimals = self.decimals()
        return amount_uba / 10 ** decimals

    def name(self):
        return self.read("name")
    
    def total_supply(self):
        return self.read("totalSupply")