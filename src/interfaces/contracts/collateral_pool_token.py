from decimal import Decimal
from typing import Optional
from src.utils.data_structures import TokenNative, UserNativeData
from src.flow.fee_tracker import FeeTracker
from src.utils.contracts import get_contract_names
from .contract_client import ContractClient


class CollateralPoolToken(ContractClient):
    def __init__(
            self, 
            token_native: TokenNative,
            pool_address: str,
            sender_data: Optional[UserNativeData]  = None, 
            fee_tracker: Optional[FeeTracker]  = None
        ):
        names = get_contract_names(self)
        super().__init__(names, token_native, pool_address, sender_data=sender_data, fee_tracker=fee_tracker)

    def debt_free_balance_of(self, address: str) -> int:
        return self.read("debtFreeBalanceOf", inputs=[address])

    def transfer(self, to_address: str, amount: int) -> None:
        self.write("transfer", inputs=[to_address, amount])

    def decimals(self) -> int:
        return self.read("decimals")
    
    def to_uba(self, amount: Decimal) -> int:
        decimals = self.decimals()
        return int(amount * Decimal(10) ** decimals)
    
    def from_uba(self, amount_uba: int) -> Decimal:
        decimals = self.decimals()
        return Decimal(amount_uba) / (Decimal(10) ** decimals)

    def name(self) -> str:
        return self.read("name")
    
    def total_supply(self) -> int:
        return self.read("totalSupply")