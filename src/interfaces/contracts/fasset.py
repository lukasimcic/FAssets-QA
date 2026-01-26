from decimal import Decimal
from typing import Optional
from src.utils.data_structures import TokenFasset, TokenNative, TokenUnderlying, UserNativeData
from src.flow.fee_tracker import FeeTracker
from .contract_client import ContractClient
from src.interfaces.contracts.asset_manager import AssetManager
from src.utils.contracts import get_contract_names


class FAsset(ContractClient):
    def __init__(
            self, 
            token_native: TokenNative,
            token_underlying: TokenUnderlying, 
            sender_data: Optional[UserNativeData] = None,
            fee_tracker: Optional[FeeTracker] = None
        ):
        self.token_underlying = token_underlying
        names = get_contract_names(self, token_underlying)
        super().__init__(names, token_native, sender_data=sender_data, fee_tracker=fee_tracker)

    def get_balance(self) -> Decimal:
        return self.balance_of(self.sender_address)

    def balance_of(self, address: str) -> Decimal:
        balance_uba = self.read("balanceOf", inputs=[address])
        token_fasset = TokenFasset.from_underlying(self.token_underlying)
        return token_fasset.from_uba(balance_uba)
    
    def approve(self, spender: str, amount: int):
        return self.write("approve", inputs=[spender, amount])
    
    def allowance(self, owner: str, spender: str) -> int:
        return self.read("allowance", inputs=[owner, spender])