from typing import Optional
from src.utils.data_structures import TokenNative, UserNativeData
from src.flow.fee_tracker import FeeTracker
from src.utils.contracts import get_contract_names
from .contract_client import ContractClient


class AgentVault(ContractClient):
    def __init__(
            self, 
            token_native: TokenNative,
            vault_address: str, 
            sender_data: Optional[UserNativeData]  = None, 
            fee_tracker: Optional[FeeTracker]  = None
        ):
        names = get_contract_names(self)
        super().__init__(names, token_native, vault_address, sender_data=sender_data, fee_tracker=fee_tracker)

    def collateral_pool(self) -> str:
        return self.read("collateralPool")