from decimal import Decimal
from typing import Optional
import toml
from src.utils.data_structures import TokenFasset, TokenNative, TokenUnderlying, UserNativeData
from src.flow.fee_tracker import FeeTracker
from .contract_client import ContractClient
from src.interfaces.contracts.asset_manager import AssetManager
from src.utils.contracts import get_contract_address

config = toml.load("config.toml")
fasset_path = config["contract"]["abi_path"]["fasset"]


class FAsset(ContractClient):
    def __init__(
            self, 
            token_native: TokenNative,
            token_underlying: TokenUnderlying, 
            sender_data: Optional[UserNativeData]  = None,
            fee_tracker: Optional[FeeTracker]  = None
        ):
        self.token_underlying = token_underlying
        fasset_address =  get_contract_address(
            token_underlying.fasset_name,
            token_native
            )
        super().__init__(token_native, fasset_path, fasset_address, sender_data, fee_tracker)

    def get_balance(self) -> Decimal:
        return self.balance_of(self.sender_address)

    def balance_of(self, address: str) -> Decimal:
        balance_uba = self.read("balanceOf", inputs=[address])
        token_fasset = TokenFasset.from_underlying(self.token_underlying)
        return token_fasset.from_uba(balance_uba)