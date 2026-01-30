from typing import Optional
from src.utils.data_structures import TokenNative, TokenUnderlying, UserNativeData
from src.flow.fee_tracker import FeeTracker
from .contract_client import ContractClient
from src.utils.contracts import get_contract_names


class AssetManagerController(ContractClient):
    def __init__(
            self, 
            token_native: TokenNative,
            token_underlying: TokenUnderlying, 
            sender_data: Optional[UserNativeData]  = None, 
            fee_tracker: Optional[FeeTracker]  = None
        ):
        self.token_underlying = token_underlying
        names = get_contract_names(self, token_underlying)
        super().__init__(names, token_native, sender_data=sender_data, fee_tracker=fee_tracker)
